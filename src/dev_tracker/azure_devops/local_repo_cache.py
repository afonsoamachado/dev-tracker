import hashlib
import json
import os
import threading

_CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")

# One lock per physical cache file, shared across all LocalRepoCache
# instances (and threads) that point at the same file. Guards the
# read-modify-write sequence so concurrent get_repositories() calls for
# the same project can't corrupt or clobber each other's writes.
_file_locks: dict[str, threading.Lock] = {}
_file_locks_guard = threading.Lock()  # protects _file_locks itself


def _get_file_lock(cache_file: str) -> threading.Lock:
    with _file_locks_guard:
        if cache_file not in _file_locks:
            _file_locks[cache_file] = threading.Lock()
        return _file_locks[cache_file]


class LocalRepoCache:

    def __init__(self, file_name):
        if not file_name:
            raise Exception("Invalid Local Cache file name.")
        self.cache_file = os.path.join(_CACHE_DIR, f"{file_name}_repositories.json")
        self._lock = _get_file_lock(self.cache_file)

    def load(self) -> dict:
        """Load the on-disk repo cache, returning an empty dict on any error."""
        with self._lock:
            return self._load_unlocked()

    def save(self, cache: dict) -> None:
        """Persist the repo cache to disk (atomic replace)."""
        with self._lock:
            self._save_unlocked(cache)

    def get_or_set(self, key: str, fetch_fn):
        """
        Atomically check the cache for *key*; if missing, call *fetch_fn()*,
        store the result, and return it. The whole check-fetch-store
        sequence happens under the file lock, so concurrent callers for the
        same project never trigger duplicate API fetches or lose a write.

        Args:
            key (str): Cache key to look up.
            fetch_fn (callable): No-arg function returning the value to
                cache when *key* is missing.

        Returns:
            The cached or freshly-fetched value.
        """
        with self._lock:
            cache = self._load_unlocked()
            if key in cache:
                return cache[key]
            value = fetch_fn()
            cache[key] = value
            self._save_unlocked(cache)
            return value

    def _load_unlocked(self) -> dict:
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_unlocked(self, cache: dict) -> None:
        os.makedirs(_CACHE_DIR, exist_ok=True)
        tmp = f"{self.cache_file}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
        os.replace(tmp, self.cache_file)  # atomic on POSIX and Windows

    def repo_filter_fingerprint(self, repo_filter: list) -> str:
        """
        Return a short hash that represents the current repo filter list.
        When the configured repos change the fingerprint changes, which
        triggers a cache refresh for that project.
        """
        canonical = ",".join(sorted(repo_filter))
        return hashlib.md5(canonical.encode()).hexdigest()[:8]
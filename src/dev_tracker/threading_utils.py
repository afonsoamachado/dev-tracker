"""
Thread pool helpers shared across trackers.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed


def run_parallel(items, fn):
    """
    Run *fn(item)* for every item in *items*, in parallel, one thread per item.

    Args:
        items (Iterable): Items to process. If empty, returns [] immediately
            without spinning up an executor.
        fn (callable): Function taking a single item and returning a result.

    Returns:
        list: Results in completion order (not necessarily input order).
    """
    items = list(items)
    if not items:
        return []

    with ThreadPoolExecutor(max_workers=len(items)) as executor:
        futures = [executor.submit(fn, item) for item in items]
        return [future.result() for future in as_completed(futures)]
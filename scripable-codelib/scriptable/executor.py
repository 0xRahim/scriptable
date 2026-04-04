from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable

def run_sequential(tasks: List[Callable]):
    """Runs tasks one by one."""
    for task in tasks:
        task()

def run_threaded(tasks: List[Callable], max_workers: int = 5, delay: float = 0.0):
    """
    Runs tasks concurrently.
    delay: seconds to wait between submitting each task (rate limit friendly)
    """
    import time
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for task in tasks:
            futures.append(executor.submit(task))
            if delay:
                time.sleep(delay)

        # surface exceptions — without this, thread errors die silently
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"  [!] Thread error: {e}")
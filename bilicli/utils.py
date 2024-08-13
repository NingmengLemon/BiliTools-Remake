from typing import Sequence, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import time

from tqdm import tqdm

from bilicli.hints import WorkerThread


def update_progress(pgrbar: tqdm, thread: WorkerThread):
    curr, total, text = thread.observe()
    pgrbar.set_description(text)
    pgrbar.n = curr
    pgrbar.total = total


def run_thread_with_tqdm(thread: WorkerThread, pos: int, interval=0.05):
    with tqdm(unit="B", unit_scale=True, unit_divisor=1024, position=pos) as pgrbar:
        thread.start()
        while thread.is_alive():
            update_progress(pgrbar, thread)
            time.sleep(interval)
        update_progress(pgrbar, thread)
    return thread


def run_threads(threads: Sequence[WorkerThread]):
    exceptions = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(run_thread_with_tqdm, thread, i + 1)
            for i, thread in enumerate(threads)
        ]
        for future in tqdm(as_completed(futures), total=len(threads), desc="Overall"):
            if (_ := future.result()).exceptions:
                exceptions += _.exceptions
    if exceptions:
        logging.error("Exceptions while downloading: %s", exceptions)
    return exceptions


def parse_index_option(index_s: Optional[str]):
    if not index_s:
        return None
    return list(map(lambda x: int(x.strip()), index_s.split(",")))

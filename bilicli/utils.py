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
    with tqdm(
        unit="B", unit_scale=True, unit_divisor=1024, position=pos, leave=False
    ) as pgrbar:
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
        for future in tqdm(
            as_completed(futures), total=len(threads), desc="Overall", leave=False
        ):
            thread = future.result()
            if _ := thread.exceptions:
                exceptions += _
    for _ in exceptions:
        logging.error("Exceptions while downloading: %s", _)
    return exceptions


def parse_index_option(index_s: Optional[str]) -> list[int]:
    if not index_s:
        return []
    return list(map(lambda x: int(x.strip()), index_s.split(",")))


def generate_media_ptitle(title, long_title, i=-1, **_):
    res = ""
    res += "" if title == str(i) else title
    res += "_" if res and long_title else ""
    res += long_title if long_title else ""
    return res

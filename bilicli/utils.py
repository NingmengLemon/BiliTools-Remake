from typing import Sequence, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import time
from queue import Queue
from threading import Lock

from tqdm import tqdm

from bilicli.hints import WorkerThread


class BarPosAssigner:
    def __init__(self, init_workernum: int) -> None:
        self._queue: Queue[int] = Queue()
        self._barnum = init_workernum
        self._barnum_lock = Lock()
        for i in range(1, init_workernum + 1):
            self._queue.put(i)

    def get(self):
        if self._queue.empty():
            with self._barnum_lock:
                self._barnum += 1
                return self._barnum
        return self._queue.get()

    def put(self, pos):
        self._queue.put(pos)


def update_progress(pgrbar: tqdm, thread: WorkerThread):
    curr, total, text = thread.observe()
    pgrbar.set_description(text)
    pgrbar.n = curr
    pgrbar.total = total


def run_thread_with_tqdm(
    thread: WorkerThread,
    pos_assigner: Optional[BarPosAssigner] = None,
    interval=0.05,
    unit="B",
):
    pos = pos_assigner.get() if pos_assigner else None
    with tqdm(
        unit=unit, unit_scale=True, unit_divisor=1024, position=pos, leave=False
    ) as pgrbar:
        thread.start()
        while thread.is_alive():
            update_progress(pgrbar, thread)
            time.sleep(interval)
        update_progress(pgrbar, thread)
    if not thread.exceptions and pos_assigner:
        pos_assigner.put(pos)
    return thread


def run_threads(threads: Sequence[WorkerThread], max_worker=4, unit="B"):
    exceptions: list[Exception] = []
    assigner = BarPosAssigner(max_worker)
    with ThreadPoolExecutor(max_workers=max_worker) as executor:
        futures = [
            executor.submit(run_thread_with_tqdm, thread, assigner, unit=unit)
            for i, thread in enumerate(threads)
        ]
        for future in tqdm(
            as_completed(futures),
            total=len(threads),
            desc="Overall",
            leave=False,
            position=0,
        ):
            thread = future.result()
            if _ := thread.exceptions:
                exceptions += _
                for e in _:
                    logging.error("exception from child thread: %s", e, exc_info=True)
    return exceptions


def parse_index_option(index_s: Optional[str]) -> set[int]:
    result: set[int] = set()
    if not index_s:
        return result
    parts = index_s.split(",")

    for part in parts:
        if "-" in part:
            start, end = map(int, part.split("-"))
            result.update(range(start, end + 1))
        else:
            result.add(int(part))

    return result


def generate_media_ptitle(title, long_title, i=-1, **_):
    res = ""
    res += "" if title == str(i) else title
    res += "_" if res and long_title else ""
    res += long_title or ""
    return res

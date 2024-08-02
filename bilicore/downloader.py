import os
from typing import Callable, Optional, Any, Iterable
import threading

import requests

from biliapis import APIContainer, HEADERS


class HeaderRange:
    def __init__(self, start: int = 0, end: Optional[int] = None) -> None:
        self.start = start
        self.end = end

    def __str__(self):
        if self.end:
            return f"bytes={self.start}-{self.end}"
        return f"bytes={self.start}-"

    def __tuple__(self):
        return (self.start, self.end)


def download_common(
    url: str,
    filepath: str,
    chunk_size: int = 4096,
    session: Optional[requests.Session] = None,
    hook_func: Optional[Callable[[int, int], Any]] = None,
    **kwargs,
):
    if os.path.isfile(filepath):
        return
    tmpfilepath = filepath + ".download"
    current_size = os.path.getsize(tmpfilepath) if os.path.isfile(tmpfilepath) else 0

    session = session if session else requests.Session()
    hook_func = hook_func if hook_func else lambda x, y: None
    kwargs.setdefault("headers", HEADERS.copy())
    kwargs.setdefault("timeout", 10)
    if current_size > 0:
        kwargs["headers"]["Range"] = f"bytes={current_size}-"

    with session.get(url, stream=True, **kwargs) as resp:
        total_size = int(resp.headers.get("content-length", 0))
        if resp.status_code == 416:
            os.rename(tmpfilepath, filepath)
            return
        resp.raise_for_status()
        if resp.status_code != 206 and current_size > 0:
            current_size = 0
            write_mode = "wb+"
        else:
            write_mode = "ab+"

        with open(tmpfilepath, write_mode) as fp:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if chunk:
                    fp.write(chunk)
                    current_size += len(chunk)
                    hook_func(current_size, total_size)
    os.rename(tmpfilepath, filepath)


# experimenting
class DownloadThread(threading.Thread):
    def __init__(
        self, url: str, data_range: Optional[HeaderRange] = None, **kwargs
    ) -> None:
        super().__init__(daemon=False)
        self._stop_flag = False
        self.data_range = data_range if data_range else HeaderRange()
        self.url = url

    def run(self):
        pass

    def stop(self):
        self._stop_flag = True

    def observe(self):
        pass


class MultiThreadDownloader:
    def __init__(
        self,
        url,
        filepath,
        maxthread: int = 8,
        chunk_size: int = 32 * (2**20),
        **kwargs,
    ) -> None:
        self.url = url
        self.filepath = filepath
        self.maxthread = maxthread
        self.chunk_size = chunk_size

    def save_progress(self):
        pass

    def observe(self):
        pass

    def _worker(self):
        pass

    def _prepare(self):
        pass

    def start(self):
        pass


class Downloader:
    def __init__(self, apis: APIContainer) -> None:
        pass

import os
from typing import Callable, Optional, Any

import requests

from biliapis import APIContainer, HEADERS


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


class Downloader:
    def __init__(self, apis: APIContainer) -> None:
        pass

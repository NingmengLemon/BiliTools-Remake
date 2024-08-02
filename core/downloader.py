import os
import threading
from typing import Callable, Optional, Any, MutableMapping

import requests

from biliapis import APIContainer, HEADERS


def download(
    url: str,
    filepath: str,
    chunk_size: int = 4096,
    session: Optional[requests.Session] = None,
    hook_func: Optional[Callable[[int, int], Any]] = None,
    hook_obj: Optional[MutableMapping[str, Any]] = None,
    **kwargs
):
    # Building
    session = session if session else requests.Session()
    hook_func = hook_func if hook_func else lambda x, y: None
    hook_obj = hook_obj if hook_obj else {}
    kwargs.setdefault("headers", HEADERS)
    kwargs.setdefault("timeout", 10)

    with session.head(url, **kwargs) as head:
        resumable = head.headers.get("Accept-Ranges") == "bytes"
        total_size = int(head.headers.get("content-length", 0))
    write_mode = "ab+" if resumable else "wb+"
    current_size = (
        os.path.getsize(filepath) if os.path.isfile(filepath) and resumable else 0
    )
    dirpath, filename = os.path.split(filepath)

    with session.get(url, stream=True, **kwargs) as resp:
        pass
    
    return NotImplemented


class Downloader:
    def __init__(self, apis: APIContainer) -> None:
        pass

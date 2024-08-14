import os
from typing import Callable, Optional, Any, Literal, Iterable
import threading
from enum import Enum
import time

import requests

from biliapis import HEADERS


def get_remote_head(url, session=None, **kwargs):
    session = session if session else requests.Session()
    kwargs.setdefault("headers", HEADERS.copy())
    with session.head(url, **kwargs) as resp:
        resp.raise_for_status()
        return resp.headers.copy()


def download_common(
    url: str,
    filepath: str,
    session: Optional[requests.Session] = None,
    hook_func: Optional[Callable[[Optional[int], Optional[int]], Any]] = None,
    **kwargs,
):
    if os.path.isfile(filepath):
        return
    tmpfilepath = filepath + ".download"
    if os.path.isfile(tmpfilepath):
        headers = get_remote_head(url, **kwargs.copy())
        if headers.get("Accept-Ranges") != "bytes":
            # 不能续传，删掉上次未完成的文件
            os.remove(tmpfilepath)
    thread = DownloadThread(url=url, filepath=filepath, session=session, **kwargs)
    thread.start()
    while thread.is_alive():
        try:
            time.sleep(0.05)
            status = thread.observe()
            if hook_func:
                hook_func(status["size_local"], status["size_remote"])
        except KeyboardInterrupt:
            thread.stop()
    if thread.exception is not None:
        raise thread.exception


class DownloadStatus(Enum):
    PENDING = 0
    RUNNING = 1
    DONE = 2
    ERROR = 3


# experimenting
class DownloadThread(threading.Thread):
    def __init__(
        self,
        url: str,
        filepath: str,
        session: Optional[requests.Session] = None,
        start_byte: int = 0,
        end_byte: Optional[int] = None,
        **kwargs,
    ) -> None:
        super().__init__(daemon=True)
        self._url = url
        self._filepath = filepath
        self._session = session if session else requests.Session()
        self._start_byte = start_byte
        self._end_byte = end_byte
        kwargs["headers"] = kwargs.get("headers", HEADERS).copy()
        kwargs["headers"].pop("Range", None)
        self._kwargs = kwargs
        self.exception: Optional[Exception] = None
        self._status: dict[
            Literal["resumable", "size_remote", "size_local", "status"],
            Any,
        ] = {
            "resumable": None,  # 指的是能否断点续传，不是中途暂停
            "size_remote": None,
            "size_local": None,
            "status": DownloadStatus.PENDING,
        }
        self._pause_event = threading.Event()
        self._pause_event.set()
        self._stop_event = threading.Event()

    @property
    def filepath(self):
        return self._filepath

    def _worker(self):
        # 如果存在已完成的文件直接停
        if os.path.isfile(self._filepath):
            return
        tmpfilepath = self._filepath + ".download"
        # 检查可能遗留的临时文件
        if os.path.isfile(tmpfilepath):
            local_size = os.path.getsize(tmpfilepath)
        else:
            local_size = 0
        self._status["size_local"] = local_size
        # 设置 Range 头
        if self._start_byte > 0 or self._end_byte or local_size > 0:
            self._kwargs["headers"]["Range"] = (
                f"bytes={self._start_byte+local_size}-"
                + (f"{self._end_byte}" if self._end_byte else "")
            )
        # 开始
        with self._session.get(self._url, stream=True, **self._kwargs) as resp:
            resp.raise_for_status()
            # 获取元数据
            self._status["resumable"] = (
                resp.headers.get("Accept-Ranges") == "bytes"
                or "Content-Range" in resp.headers
            )
            content_length = int(resp.headers.get("Content-Length", -1))
            # 检查支持情况
            if "Range" in self._kwargs["headers"] and (
                resp.status_code != 206 or content_length == -1
            ):
                raise RuntimeError("range operation not supported")
            self._status["size_remote"] = local_size + content_length
            with open(tmpfilepath, "ab+") as fp:
                for chunk in resp.iter_content(chunk_size=2**16):
                    # 暂停与终止
                    if self._stop_event.is_set():
                        return
                    self._pause_event.wait()
                    if chunk:
                        fp.write(chunk)
                        local_size += len(chunk)
                        self._status["size_local"] = local_size
        os.rename(tmpfilepath, self._filepath)

    def run(self):
        try:
            self._status["status"] = DownloadStatus.RUNNING
            self._worker()
        except Exception as e:
            self._status["status"] = DownloadStatus.ERROR
            self.exception = e
        else:
            self._status["status"] = DownloadStatus.DONE

    def observe(self, raiseexc: bool = True):
        if (e := self.exception) and raiseexc:
            raise e
        return self._status.copy()

    def pause(self):
        self._pause_event.clear()

    def resume(self):
        self._pause_event.set()

    def stop(self):
        self._stop_event.set()


class SimpleDownloadThreadList(list[DownloadThread]):
    """十分甚至九分简陋的一个用来方便管理下载线程的东西"""

    def __init__(self, *args) -> None:
        if all(isinstance(item, threading.Thread) for item in args):
            super().__init__(args)
        else:
            raise ValueError("all elements should be instance of DownloadThread")

    def start_all(self):
        for t in self:
            t.start()

    def observe(self):
        size, done, errored, running, excps = 0, 0, 0, 0, []
        for t in self:
            status = t.observe(False)
            if s := status["size_local"]:
                size += int(s)
            match status["status"]:
                case DownloadStatus.DONE:
                    done += 1
                case DownloadStatus.ERROR:
                    errored += 1
                    if e := t.exception:
                        excps += [e]
                case DownloadStatus.RUNNING:
                    running += 1
        return size, done, errored, running, excps

    def switch_all(
        self,
        action: Literal["pause", "resume", "stop"],
    ):
        match action:
            case "pause":
                _ = [t.pause() for t in self]
            case "resume":
                _ = [t.resume() for t in self]
            case "stop":
                _ = [t.stop() for t in self]

    def is_alive(self):
        return bool(sum(t.is_alive() for t in self))


class MultiThreadDownloader(threading.Thread):
    """下载一个文件。如果服务器支持的话就采用多线程

    有线程出错也视为完成，错误会放在 self.child_exceptions 中"""

    def __init__(
        self,
        url,
        filepath,
        session: Optional[requests.Session] = None,
        threadnum: int = 8,
        **kwargs,
    ) -> None:
        super().__init__(daemon=True)
        self._url = url
        self._filepath = filepath
        self._threadnum = threadnum
        self._session = session if session else requests.Session()
        kwargs["headers"] = kwargs.get("headers", HEADERS).copy()
        kwargs["headers"].pop("Range", None)
        self._kwargs = kwargs
        self._status: dict[
            Literal[
                "resumable", "size_remote", "size_local", "status", "thread_active"
            ],
            Any,
        ] = {
            "resumable": None,
            "size_remote": None,
            "size_local": None,
            "status": DownloadStatus.PENDING,
            "thread_active": 0,
        }
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()
        self.child_exceptions: list[Exception] = []
        self.exception: Optional[Exception] = None

    def observe(self, raiseexc: bool = True):
        if (e := self.exception) and raiseexc:
            raise e
        return self._status.copy()

    def _worker_multi(self, ranges: list[tuple[int, int]]):
        threads = SimpleDownloadThreadList()
        for start, end in ranges:
            tmpfilepath = self._filepath + f".m{start}-{end}dl"
            threads.append(
                DownloadThread(
                    self._url,
                    tmpfilepath,
                    session=self._session,
                    start_byte=start,
                    end_byte=end,
                    **self._kwargs,
                )
            )
        threads.start_all()
        while threads.is_alive():
            size, _, _, running, _ = threads.observe()
            self._status["size_local"] = size
            self._status["thread_active"] = running
            if self._stop_event.is_set():
                threads.switch_all("stop")
                return
            if not self._pause_event.is_set():
                threads.switch_all("pause")
                self._pause_event.wait()
                threads.switch_all("resume")
            time.sleep(0.1)
        _, _, errored, _, excps = threads.observe()
        if errored == 0:
            self._merge_chunks([t.filepath for t in threads], self._filepath, True)
        else:
            self.child_exceptions = excps

    @staticmethod
    def _merge_chunks(chunks: Iterable[str], resultfile: str, delete: bool = True):
        with open(resultfile, "wb") as outfile:
            for chunk in chunks:
                with open(chunk, "rb") as infile:
                    outfile.write(infile.read())

        if delete:
            for chunk in chunks:
                os.remove(chunk)

    def _worker_single(self):
        tmpfilepath = self._filepath + ".download"
        if os.path.isfile(tmpfilepath):
            # 由于不能续传，删掉上次的未完成文件
            os.remove(tmpfilepath)
        thread = DownloadThread(
            self._url, self._filepath, session=self._session, **self._kwargs
        )
        while thread.is_alive():
            time.sleep(0.1)
            self._status["thread_active"] = 1
            self._status.update(thread.observe())
            if not self._pause_event.is_set():
                thread.pause()
                self._pause_event.wait()
                thread.resume()
        self._status["thread_active"] = 0

    def _prepare(self):
        """确定是否要多线程"""
        head = get_remote_head(self._url, session=self._session, **self._kwargs)
        length = int(head.get("Content-Length", -1))
        if head.get("Accept-Ranges") == "bytes" and (length != -1):
            return True, length
        return False, length

    def _logic(self):
        if os.path.exists(self._filepath):
            return
        multi, total_size = self._prepare()
        self._status["size_remote"] = total_size
        if multi:
            ranges = self.calculate_ranges(
                total_size=total_size, num_threads=self._threadnum
            )
            self._status["resumable"] = True
            self._worker_multi(ranges)
        else:
            self._status["resumable"] = False
            self._status["size_local"] = 0
            self._worker_single()

    def stop(self):
        self._stop_event.set()

    def pause(self):
        self._pause_event.clear()

    def resume(self):
        self._pause_event.set()

    def run(self):
        try:
            self._status["status"] = DownloadStatus.RUNNING
            self._logic()
        except Exception as e:
            self.exception = e
            self._status["status"] = DownloadStatus.ERROR
        else:
            self._status["status"] = DownloadStatus.DONE
        finally:
            self._status["thread_active"] = 0

    @staticmethod
    def calculate_ranges(total_size: int, num_threads: int):
        # 计算每个线程要下载的字节数
        chunk_size = total_size // num_threads
        ranges = []

        for i in range(num_threads):
            start = i * chunk_size
            # 最后一个线程将负责下载剩余的所有部分
            if i == num_threads - 1:
                end = total_size - 1
            else:
                end = start + chunk_size - 1
            ranges.append((start, end))

        return ranges

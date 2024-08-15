import threading
import asyncio
from typing import Callable, Iterable, Mapping, Any, Optional, Union
import functools
import subprocess

_FN_REPMAP = {
    "/": "／",
    "*": "＊",
    ":": "：",
    "\\": "＼",
    ">": "＞",
    "<": "＜",
    "|": "｜",
    "?": "？",
    '"': "＂",
}

def call_ffmpeg(*args):
    cmd = ["ffmpeg", "-loglevel", "quiet", "-nostdin", "-hide_banner"]
    cmd += args
    with subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as subp:
        return subp.wait()


def merge_avfile(
    au_file: str,
    vi_file: str,
    output_file: str,
    metadata: Optional[dict[str, str]] = None,
) -> int:
    """调用ffmpeg进行合流，并能添加元数据"""
    args = ["-i", au_file, "-i", vi_file, "-vcodec", "copy", "-acodec", "copy"]
    if metadata:
        for key, value in metadata.items():
            args.extend(["-metadata", f"{key}={value}"])
    args.append(output_file)
    return call_ffmpeg(*args)


def convert_audio(
    input_file: str,
    output_file: str,
    metadata: Optional[dict[str, str]] = None,
    cover_image: Optional[str] = None,
):
    """
    转换音频文件格式，且能添加元数据和封面图片
    元数据名称参见：https://kodi.wiki/view/Video_file_tagging#Supported_Tags

    :param input_file: 输入文件路径
    :param output_file: 输出文件路径
    :param metadata: 包含元数据的字典
    :param cover_image: 封面图片文件路径
    """
    args = ["-i", input_file]

    if metadata:
        for key, value in metadata.items():
            args.extend(["-metadata", f"{key}={value}"])

    if cover_image:
        # fmt: off
        args.extend([
            "-i", cover_image, "-map", "0", "-map", "1", 
            "-metadata:s:v", "title=Album cover", 
            "-metadata:s:v", "comment=Cover (front)"
            ])
        # fmt: on

    args.append(output_file)
    return call_ffmpeg(*args)


def filename_escape(text: str):
    for t in list(_FN_REPMAP.keys()):
        text = text.replace(t, _FN_REPMAP[t])
    return text


class ThreadWithReturn(threading.Thread):
    def __init__(
        self,
        group: None = None,
        target: Optional[Callable[..., Any]] = None,
        name: Optional[str] = None,
        args: Iterable[Any] = (),
        kwargs: Optional[Mapping[str, Any]] = None,
        *,
        daemon: bool | None = None,
    ) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self._args = args
        self._kwargs = kwargs
        self._target = target
        self.result: Any = None
        self.exception: Optional[Exception] = None

    def run(self) -> None:
        try:
            if self._kwargs is None:
                self._kwargs = {}
            if self._target:
                self.result = self._target(*self._args, **self._kwargs)
        except Exception as e:
            self.exception = e
        finally:
            del self._target, self._args, self._kwargs


async def run_as_async(
    func,
    args=(),
    kwargs=None,
    daemon: bool = True,
    check_delay: Union[float, int] = 0.1,
):
    thread = ThreadWithReturn(
        target=func, args=args, kwargs=kwargs, name=func.__name__, daemon=daemon
    )
    thread.start()
    while thread.is_alive():
        await asyncio.sleep(check_delay)
    if e := thread.exception:
        raise e
    return thread.result


def run_as_async_decorator(daemon: bool = True, check_delay: Union[float, int] = 0.1):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return run_as_async(
                func, args=args, kwargs=kwargs, daemon=daemon, check_delay=check_delay
            )

        return wrapper

    return decorator

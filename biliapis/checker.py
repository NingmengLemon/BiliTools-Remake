from typing import Optional, Union, Callable, Any
import functools

from biliapis.error import BiliError


def _check_abvid(
    avid: Optional[int], bvid: Optional[str]
) -> dict[str, Optional[Union[int, str]]]:
    if (avid is None) == (bvid is None):
        raise ValueError("Must pass either `avid` or `bvid` as a parameter")
    return {"avid": avid, "bvid": bvid}


def check_abvid(func):
    @functools.wraps(func)
    def wrapper(
        *args, avid: Optional[int] = None, bvid: Optional[str] = None, **kwargs
    ):
        return func(*args, **_check_abvid(avid=avid, bvid=bvid), **kwargs)

    return wrapper


def _check_bilicode(
    data: dict, codekey: str = "code", msgkey: str = "message", okcode: int = 0
):
    if (code := data.get(codekey, -1)) != okcode:
        raise BiliError(code, data.get(msgkey))
    return data


def check_bilicode(codekey: str = "code", msgkey: str = "message", okcode: int = 0):
    def decorator(func: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return _check_bilicode(
                func(*args, **kwargs), codekey=codekey, msgkey=msgkey, okcode=okcode
            )

        return wrapper

    return decorator

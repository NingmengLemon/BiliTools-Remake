from typing import Any, Callable, Iterable, Optional, Literal
import functools
import logging
import re

import requests

__all__ = [
    "get_csrf",
    "remove_none",
    "pick_data",
    "FallbackFailure",
    "fallback",
    "decorate",
    "extract_ids",
]


def get_csrf(session: requests.Session) -> Optional[str]:
    """从session获得很多api需要的csrf"""
    return requests.utils.dict_from_cookiejar(session.cookies).get("bili_jct")


def remove_none(d: dict[str, Any], copy: bool = False) -> dict[str, Any]:
    """
    移除字典中的值为None的键值对
    """
    if copy:
        # 创建新字典
        return {k: v for k, v in d.items() if v is not None}
    else:
        # 原地修改
        keys = [k for k, v in d.items() if v is None]
        for k in keys:
            del d[k]
        return d


def pick_data(datakey: str = "data"):
    """
    从函数的返回值中获取指定键对应的值，需求该函数返回值为`dict[str, Any]`类型
    """

    def decorator(func: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result.get(datakey)

        return wrapper

    return decorator


class FallbackFailure(Exception):
    """
    表示所有fallback方案都已失败
    """


def fallback(tolerable_exceptions: Optional[Iterable] = None):
    """
    装饰函数之后，可以使用被装饰函数的`register`装饰器方法注册来用于fallback的函数，
    要求fallback函数的参数与被装饰函数的一致。
    """

    def decorator(func):
        return Fallbacker(func, tolerable_exceptions=tolerable_exceptions)

    return decorator


class Fallbacker:
    """
    用于做fallback装饰的装饰器类
    （不完全是，需要fallback函数做辅助）
    """

    def __init__(self, func: Callable, tolerable_exceptions: Optional[Iterable] = None):
        self._tol_excs = (
            tuple(tolerable_exceptions) if tolerable_exceptions else (Exception,)
        )
        self._func = func
        self._fallback_funcs: list[Callable] = []

    def __call__(self, *args, **kwargs) -> Any:
        try:
            return self._func(*args, **kwargs)
        except self._tol_excs:
            if self._fallback_funcs:
                return self._do_fallback(*args, **kwargs)
            raise

    def _do_fallback(self, *args, **kwargs):
        for func in self._fallback_funcs:
            try:
                return func(*args, **kwargs)
            except self._tol_excs as e:
                logging.warning("Tolerated exception while falling back: %s", e)
        raise FallbackFailure("No more func to fallback")

    def register(self, func: Callable):
        """注册一个函数用于fallback"""
        self._fallback_funcs.append(func)
        return func


def decorate(func: Callable, *decorators: Callable):
    """
    对第一个参数函数，
    用后面紧跟的所有装饰器函数依序装饰它，返回装饰完成的函数
    """
    for deco in decorators:
        func = deco(func)
    return func


def extract_ids(source: str, session: Optional[requests.Session] = None) -> tuple[
    Optional[str | int],
    Optional[
        Literal[
            "auid",
            "bvid",
            "avid",
            "cvid",
            "mdid",
            "ssid",
            "epid",
            "uid",
            "mcid",
            "amid",
        ]
    ],
]:
    """
    根据输入的来源返回各种id

    session 用于重定向短链接

    TODO: 重构一下这个函数让它看上去不那么史
    """
    if "b23.tv/" in source:  # 短链接重定向
        session = session if session else requests.Session()
        url = "https://b23.tv/" + re.findall(r"b23\.tv/([a-zA-Z0-9]+)", source, re.I)[0]
        if (
            req := session.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
                },
            )
        ).status_code == 200:
            source = req.url
    # 音频id
    if res := re.findall(r"au([0-9]+)", url, re.I):
        return int(res[0]), "auid"
    # bv号
    if res := re.findall(r"BV[a-zA-Z0-9]{10}", url, re.I):
        return res[0], "bvid"
    # av号
    if res := re.findall(r"av([0-9]+)", url, re.I):
        return int(res[0]), "avid"
    # 专栏号
    if res := re.findall(r"cv([0-9]+)", url, re.I):
        return int(res[0]), "cvid"
    # 整个剧集的id
    if res := re.findall(r"md([0-9]+)", url, re.I):
        return int(res[0]), "mdid"
    # 整个季度的id
    if res := re.findall(r"ss([0-9]+)", url, re.I):
        return int(res[0]), "ssid"
    # 单集的id
    if res := re.findall(r"ep([0-9]+)", url, re.I):
        return int(res[0]), "epid"
    # 手动输入的uid
    if res := re.findall(r"uid([0-9]+)", url, re.I):
        return int(res[0]), "uid"
    # 漫画id
    if res := re.findall(r"mc([0-9]+)", url, re.I):
        return int(res[0]), "mcid"
    # 歌单
    if res := re.findall(r"am([0-9]+)", url, re.I):
        return int(res[0]), "amid"
    return None, None

from typing import Any, Callable, Iterable, Optional
import functools
import logging
from http import cookiejar
import time

import requests


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

    def decorator(func):
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


def cookiejar_from_crossdomain_url(url: str):
    """URL 来自轮询登录成功后返回的数据"""
    tmpjar = cookiejar.MozillaCookieJar()
    data = url.split("?")[-1].split("&")[:-1]
    for domain in [".bilibili.com", ".bigfun.cn", ".bigfunapp.cn", ".biligame.com"]:
        for item in data:
            i = item.split("=", 1)
            # fmt: off
            tmpjar.set_cookie(
                cookiejar.Cookie(
                    0, i[0], i[1], None, False,
                    domain, True, domain.startswith('.'),
                    '/', False, False,
                    int(time.time()) + (6 * 30 * 24 * 60 * 60),
                    False, None, None, {}
                    )
                )
            # fmt: on
    return tmpjar

def extract_ids(source: str) -> tuple[Optional[str], Optional[str | int]]:
    # TODO:
    return NotImplemented

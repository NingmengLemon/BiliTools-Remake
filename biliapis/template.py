# pylint: disable=W0212
from typing import Any, Callable, Literal
import functools
from threading import Lock
import logging

from requests import Session

from .wbi import CachedWbiManager
from .constants import HEADERS as DEFAULT_HEADERS
from .error import BiliError
from .utils import get_csrf
from . import reqcache


__all__ = ["APITemplate", "request_template", "withcsrf"]


class APITemplate:
    """
    每个分类的API的模板，预定义了一些内容供调用
    """

    _DEFAULT_HEADERS = DEFAULT_HEADERS.copy()

    def __init__(
        self, session: Session, wbimanager: CachedWbiManager, extra_data: dict
    ) -> None:
        self.__session = session
        self.__wbimanager = wbimanager
        self.__extra_data = extra_data
        self.__allow_cache_switch_lock = Lock()
        self.__allow_cache = True

    @property
    def _extra_data(self):
        return self.__extra_data

    @property
    def _session(self):
        return self.__session

    @property
    def _wbimanager(self):
        return self.__wbimanager

    @property
    def allow_cache(self):
        with self.__allow_cache_switch_lock:
            return self.__allow_cache

    @allow_cache.setter
    def allow_cache(self, value: bool):
        with self.__allow_cache_switch_lock:
            self.__allow_cache = value


def request_template(
    mod="get",
    handle: Literal["json", "str", "bytes"] = "json",
    allow_cache: bool = False,
):
    """
    对 APITemplate 的子类的方法做装饰，简化请求调用

    被装饰的函数需要返回一个url和一个字典，作为 Session.request() 的除了method外的参数，
    headers参数有默认值可省略

    handle参数对请求得到的数据做处理

    allow_cache 参数表示这个方法是否允许缓存
    """

    def decorator(
        func: Callable[..., tuple[str, dict[str, Any]] | str]
    ) -> Callable[..., dict[str, Any] | bytes | str | Any]:
        @functools.wraps(func)
        def wrapper(
            self: APITemplate, *args, **kwargs
        ) -> dict[str, Any] | bytes | str | Any:
            rv = func(self, *args, **kwargs)
            if isinstance(rv, tuple):
                url, reqparams = rv
                if reqparams is None:
                    reqparams = {}
            elif isinstance(rv, str):
                url, reqparams = rv, {}
            else:
                raise ValueError("Not specified return value type: %s" % type(rv))
            reqparams.setdefault("headers", self._DEFAULT_HEADERS)
            csrf = get_csrf(self._session)
            if allow_cache and self.allow_cache and reqcache.cache:
                cacheparams = {
                    "csrf": csrf,
                    "mod": mod,
                    "url": url,
                    "params": reqparams,
                    "handle": handle,
                }
                if (result := reqcache.cache.get(cacheparams)) is not None:
                    logging.debug("Use cache: %s %s", mod.upper(), url)
                    return result
            with self._session.request(mod, url, **reqparams) as resp:
                resp.raise_for_status()
                match handle:
                    case "str":
                        result = resp.content.decode("utf-8")
                    case "bytes":
                        result = resp.content
                    case _:
                        result = resp.json()
            if allow_cache and self.allow_cache and reqcache.cache:
                reqcache.cache.set(cacheparams, result)
                logging.debug("add cache: %s %s", mod.upper(), url)
            return result

        return wrapper

    return decorator


def withcsrf(func):
    """对 APITemplate 的子类的方法做装饰，简化请求调用

    提取session中的cookies中的 csrf 以关键字参数形式传递给被装饰函数，未能获取到csrf则报错"""

    @functools.wraps(func)
    def wrapper(self: APITemplate, *args, **kwargs):
        csrf = get_csrf(self._session)
        if not csrf:
            raise BiliError(-101, "未登录")
        kwargs["csrf"] = csrf
        return func(self, *args, **kwargs)

    return wrapper

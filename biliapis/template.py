from typing import Any, Callable, Literal
import functools

from requests import Session

from biliapis.wbi import CachedWbiManager
from biliapis.constants import HEADERS as DEFAULT_HEADERS


class APITemplate:
    """
    每个分类的API的模板，预定义了一些内容供调用
    """

    _DEFAULT_HEADERS = DEFAULT_HEADERS.copy()

    def __init__(self, session: Session, wbimanager: CachedWbiManager) -> None:
        self.__session = session
        self.__wbimanager = wbimanager

    @property
    def _session(self):
        return self.__session

    @property
    def _wbimanager(self):
        return self.__wbimanager


def request_template(
    mod="get", handle: Literal["json", "str", "raw", "bytes"] = "json"
):
    """
    对 APITemplate 的子类的方法做装饰，简化请求调用

    被装饰的函数需要返回一个url和一个字典，作为 Session.request() 的除了method外的参数，
    headers参数有默认值可省略

    handle参数对请求得到的数据做处理
    """

    def decorator(
        func: Callable[..., tuple[str, dict[str, Any]]]
    ) -> Callable[..., dict[str, Any] | bytes | str | Any]:
        @functools.wraps(func)
        def wrapper(
            self: APITemplate, *args, **kwargs
        ) -> dict[str, Any] | bytes | str | Any:
            if isinstance(rv := func(self, *args, **kwargs), tuple):
                url, reqparams = rv
                if reqparams is None:
                    reqparams = {}
            elif isinstance(rv, str):
                url, reqparams = rv, {}
            else:
                raise ValueError("Not specified return value type: %s" % type(rv))
            reqparams.setdefault(
                "headers", self._DEFAULT_HEADERS  # pylint: disable=W0212
            )
            with self._session.request(  # pylint: disable=W0212
                mod, url, **reqparams
            ) as resp:
                resp.raise_for_status()
                match handle:
                    case "str":
                        return resp.text
                    case "bytes":
                        return resp.content
                    case "raw":
                        return resp.raw
                    case _:
                        return resp.json()

        return wrapper

    return decorator

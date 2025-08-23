from typing import Any, Optional
from threading import Lock

from requests import Session, adapters

from .wbi import CachedWbiManager
from .template import APITemplate

# collect components
from .constants import HEADERS, VERSION
from . import apis

__all__ = ["APIContainer", "default_session", "new_apis"]

components = [v for k, v in vars(apis).items() if k.endswith("APIs")]


class APIContainer:
    VERSION = VERSION
    DEFAULT_HEADERS: dict[str, str] = HEADERS.copy()

    def __init__(self, session: Session, wbimanager: CachedWbiManager, extra_data: dict) -> None:
        self._session = session
        self._wbimanager = wbimanager
        self._extra_data = extra_data
        self.__components: list[APITemplate] = []
        self.__allow_cache = True
        self.__cache_switch_lock = Lock()
        for compcls in components:
            compinstance = compcls(session=session, wbimanager=wbimanager, extra_data=extra_data)
            setattr(
                self,
                compcls.__name__.removesuffix("APIs").lower(),
                compinstance,
            )
            self.__components.append(compinstance)
            
    @property
    def extra_data(self):
        return self._extra_data

    @property
    def session(self):
        return self._session

    @property
    def wbimanager(self):
        return self._wbimanager
    
    @property
    def allow_cache(self):
        with self.__cache_switch_lock:
            return self.__allow_cache
    
    @allow_cache.setter
    def allow_cache(self, value: bool):
        with self.__cache_switch_lock:
            for comp in self.__components:
                comp.allow_cache = value


def default_session():
    # 加一些，默认的优化选项，像 Retry Adapter？
    session = Session()
    retry = adapters.Retry(total=2, backoff_factor=0.5, backoff_max=10)
    adp = adapters.HTTPAdapter(max_retries=retry)
    session.mount("https://", adp)
    session.mount("http://", adp)
    return session


def new_apis(
    session: Optional[Session] = None, wbimanager: Optional[CachedWbiManager] = None, extra_data: Optional[dict[str, Any]] = None
) -> APIContainer:
    session = session if session else default_session()
    wbimanager = wbimanager if wbimanager else CachedWbiManager(session)
    extra_data = extra_data if extra_data else {}

    container = APIContainer(session=session, wbimanager=wbimanager, extra_data=extra_data)
    return container

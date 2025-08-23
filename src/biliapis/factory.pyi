from typing import Optional, Any

from requests import Session

from .wbi import CachedWbiManager
from . import apis

class APIContainer:
    DEFAULT_HEADERS: dict[str, str]
    VERSION: str

    @property
    def wbimanager(self) -> CachedWbiManager: ...
    @property
    def session(self) -> Session: ...
    @property
    def extra_data(self) -> dict: ...
    @property
    def allow_cache(self) -> bool: ...
    @allow_cache.setter
    def allow_cache(self, value: bool) -> None: ...

    audio: apis.AudioAPIs
    login: apis.LoginAPIs
    qrlogin: apis.QRLoginAPIs
    manga: apis.MangaAPIs
    media: apis.MediaAPIs
    video: apis.VideoAPIs

def new_apis(
    session: Optional[Session] = None,
    wbimanager: Optional[CachedWbiManager] = None,
    extra_data: Optional[dict[str, Any]] = None,
) -> APIContainer: ...

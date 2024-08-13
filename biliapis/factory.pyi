from typing import Optional
from requests import Session
from biliapis.wbi import CachedWbiManager
from . import apis

class APIContainer:
    DEFAULT_HEADERS: dict[str, str]
    VERSION: str
    wbimanager: CachedWbiManager
    session: Session

    audio: apis.AudioAPIs
    login: apis.LoginAPIs
    qrlogin: apis.QRLoginAPIs
    manga: apis.MangaAPIs
    media: apis.MediaAPIs
    video: apis.VideoAPIs

def new_apis(
    session: Optional[Session] = None, wbimanager: Optional[CachedWbiManager] = None
) -> APIContainer: ...

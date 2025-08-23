from typing import Any, Literal, TypedDict
from http.cookiejar import MozillaCookieJar

from biliapis.template import APITemplate

class _ExitLoginReturn(TypedDict):
    redirectUrl: str

class _RefreshCookiesReturn(TypedDict):
    stutus: Literal[0]
    message: Literal[""]
    refresh_token: str

class _CheckRefreshReqReturn(TypedDict):
    refresh: bool
    timestamp: int

class _FingerSPIReturn(TypedDict):
    b_3: str
    b_4: str

class LoginAPIs(APITemplate):
    def exit_login(self) -> _ExitLoginReturn: ...
    def __exit_login_req(self) -> str: ...
    def get_login_info(self) -> dict[str, Any]: ...
    def check_if_cookies_refresh_required(
        self,
    ) -> _CheckRefreshReqReturn: ...
    @staticmethod
    def get_correspond_path(ts: int) -> str: ...
    def get_refresh_csrf(self, correspond_path: str) -> str: ...
    def __get_refresh_csrf_req(self, corresp: str) -> str: ...
    def refresh_cookies(
        self, refresh_token: str, refresh_csrf: str
    ) -> _RefreshCookiesReturn: ...
    def confirm_refresh_cookies(self, old_refresh_token: str) -> None: ...
    def get_buvid(self) -> _FingerSPIReturn: ...

class _LoginQRReturn(TypedDict):
    url: str
    qrcode_key: str

class _LoginQRPollReturn(TypedDict):
    url: str | Literal[""]
    refresh_token: str | Literal[""]
    timestamp: int
    code: Literal[0, 86038, 86090, 86101]
    message: str

class QRLoginAPIs(APITemplate):
    def get_login_qrcode_url(self) -> _LoginQRReturn: ...
    def poll_login_qrcode(self, qrcode_key: str) -> _LoginQRPollReturn: ...
    def __poll_login_qrcode_req(self, qrcode_key: str) -> dict[str, int | str]: ...
    @staticmethod
    def cookiejar_from_crossdomain_url(url: str) -> MozillaCookieJar: ...

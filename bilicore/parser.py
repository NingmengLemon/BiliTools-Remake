from typing import Optional, Literal
import re

import requests

from biliapis.constants import HEADERS


IDS_PATTERNS = (
    (r"(BV[a-zA-Z0-9]{10})", "bvid", str),
    (r"av([0-9]+)", "avid", int),
    (r"au([0-9]+)", "auid", int),
    (r"cv([0-9]+)", "cvid", int),
    (r"md([0-9]+)", "mdid", int),
    (r"ss([0-9]+)", "ssid", int),
    (r"ep([0-9]+)", "epid", int),
    (r"uid([0-9]+)", "uid", int),
    (r"mc([0-9]+)", "mcid", int),
    (r"am([0-9]+)", "amid", int),
)


def extract_ids(
    source: str, session: Optional[requests.Session] = None
) -> Optional[
    tuple[
        str | int,
        # fmt: off
        Literal[
            "auid", "bvid", "avid",
            "cvid", "mdid", "ssid",
            "epid", "uid", "mcid",
            "amid",
        ],
        # fmt: on
    ]
]:
    """
    根据输入的来源返回各种id

    session 用于重定向短链接

    重构一下这个函数让它看上去不那么史
    """
    if short := re.search(r"b23\.tv/([a-zA-Z0-9]+)", source, re.I):  # 短链接重定向
        session = session if session else requests.Session()
        url = "https://b23.tv/" + short.group(1)
        if (req := session.get(url, stream=True, headers=HEADERS)).status_code == 200:
            source = req.url
    for pattern, idname, idtype in IDS_PATTERNS:
        if res := re.search(r"[^a-zA-Z]" + pattern, source, re.IGNORECASE):
            return idtype(res.group(1)), idname
    return None

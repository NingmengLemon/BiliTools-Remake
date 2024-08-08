from typing import Optional, Literal, Any
import re

import requests

from biliapis.constants import HEADERS
from biliapis import bilicodes


ID_PATTERNS = (
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
) -> Optional[tuple[str | int, str]]:
    """
    根据输入的来源返回各种id

    session 用于重定向短链接
    """
    if short := re.search(r"b23\.tv/([a-zA-Z0-9]+)", source, re.I):  # 短链接重定向
        session = session if session else requests.Session()
        url = "https://b23.tv/" + short.group(1)
        if (req := session.get(url, stream=True, headers=HEADERS)).status_code == 200:
            source = req.url
    for pattern, idname, idtype in ID_PATTERNS:
        if res := re.search(r"(?<![A-Za-z])" + pattern, source, re.IGNORECASE):
            return idtype(res.group(1)), idname
    return None


def select_quality(
    streams: dict[str, Any],
    aq: str | int | Literal["max", "min"] = "max",
    vq: str | int | Literal["max", "min"] = "max",
    enc: Literal["avc", "hevc"] = "avc",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """从得到的DASH视频流中按照要求选出流，返回一个元组

    优先满足画质要求，然后是编码要求;
    若无法满足质量要求，则选择能够取到的最高质量

    - streams: 获取到的dash流数据
    - aq：需求的音频质量
        - 为字符串时内容可以为质量的名称如`192k`等或者`max`或`min`，不区分大小写
        - 为整数时内容只能是质量id
    - vq：需求的视频质量，要求基本同上
        - 但是为整数时内容还可以是视频帧高
    - enc：需求的视频编码"""
    if "dash" not in streams:
        raise TypeError("not dash stream data")
    return _choose_video(vq=vq, streams=streams, enc=enc), _choose_audio(
        aq=aq, streams=streams
    )


def _choose_video(
    vq: str | int | Literal["max", "min"],
    streams: dict[str, Any],
    enc: Literal["avc", "hevc"],
):
    videos: list[dict] = streams["dash"]["video"]
    acvqs: list[int] = streams["accept_quality"]
    vq = vq if isinstance(vq, int) else vq.upper().strip()
    if vq in ("MAX", "MIN"):
        sel = max if vq == "MAX" else min
        return _filter_video(videos, vqid=sel(acvqs), enc=enc)
    if isinstance(vq, int):
        if vq in acvqs:
            return _filter_video(videos, vqid=vq, enc=enc)
        if vq in (v["height"] for v in videos):
            return _filter_video_encs([v for v in videos if v["height"] == vq], enc=enc)
        return _filter_video(videos, vqid=max(acvqs), enc=enc)
    if isinstance(vq, str):
        if vqid := bilicodes.stream_dash_video_quality_.get(vq):
            return _filter_video(videos, vqid=vqid, enc=enc)
    return _filter_video(videos, vqid=max(acvqs), enc=enc)


def _filter_video(videos, vqid: int, enc: Literal["avc", "hevc"]):
    if not (fqs := _filter_video_qs(videos, vqid=vqid)):
        fqs = _filter_video_qs(videos, vqid=max(i["id"] for i in videos))
    if fqes := _filter_video_encs(fqs, enc=enc):
        return fqes[0]
    return fqs[0]


def _filter_video_qs(videos: list[dict], vqid: int):
    return [v for v in videos if v["id"] == vqid]


def _filter_video_encs(videos: list[dict], enc: Literal["avc", "hevc"]):
    return [v for v in videos if v["codecs"][:2] == enc[:2]]


def _choose_audio(aq: str | int | Literal["max", "min"], streams: dict[str, Any]):
    audios: list[dict] = streams["dash"]["audio"]
    has_flac = False
    if flac := streams["dash"].get("flac"):
        if flac := flac.get("audio"):
            audios.append(flac)
            has_flac = True
    acaqs = [a["id"] for a in audios]
    aq = aq if isinstance(aq, int) else aq.upper().strip()
    if aq == "MAX":
        return _pick_audio_max(audios, has_flac)
    if aq == "MIN":
        return min(audios, key=lambda x: x["id"])
    if isinstance(aq, int):
        if aq in acaqs:
            return [a for a in audios if a["id"] == aq][0]
        return _pick_audio_max(audios, has_flac)
    if isinstance(aq, str):
        if aqc := bilicodes.stream_dash_audio_quality_.get(aq):
            return [a for a in audios if a["id"] == aqc][0]
    return _pick_audio_max(audios, has_flac)


def _pick_audio_max(audios: list[dict], has_flac: bool):
    if has_flac:
        return [a for a in audios if a["id"] == 30251][0]
    return max(audios, key=lambda x: x["id"])

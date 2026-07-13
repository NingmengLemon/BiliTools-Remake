"""Adapters around :mod:`bilibili_api`.

The rest of BiliTools should depend on the normalized dataclasses returned here,
not on upstream raw response dictionaries.  This keeps the future migration away
from the old hand-written ``biliapis`` layer incremental and reversible.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from bilibili_api import Credential, sync
from bilibili_api import video as bili_video

from ..models import PageInfo, StreamInfo, StreamKind, VideoInfo, VideoStreams

_VIDEO_QUALITY_ALIASES: dict[str, bili_video.VideoQuality] = {
    "360": bili_video.VideoQuality._360P,
    "360p": bili_video.VideoQuality._360P,
    "480": bili_video.VideoQuality._480P,
    "480p": bili_video.VideoQuality._480P,
    "720": bili_video.VideoQuality._720P,
    "720p": bili_video.VideoQuality._720P,
    "1080": bili_video.VideoQuality._1080P,
    "1080p": bili_video.VideoQuality._1080P,
    "1080p+": bili_video.VideoQuality._1080P_PLUS,
    "1080p60": bili_video.VideoQuality._1080P_60,
    "4k": bili_video.VideoQuality._4K,
    "2160": bili_video.VideoQuality._4K,
    "2160p": bili_video.VideoQuality._4K,
    "hdr": bili_video.VideoQuality.HDR,
    "dolby": bili_video.VideoQuality.DOLBY,
    "8k": bili_video.VideoQuality._8K,
    "4320": bili_video.VideoQuality._8K,
    "4320p": bili_video.VideoQuality._8K,
}

_AUDIO_QUALITY_ALIASES: dict[str, bili_video.AudioQuality] = {
    "64": bili_video.AudioQuality._64K,
    "64k": bili_video.AudioQuality._64K,
    "132": bili_video.AudioQuality._132K,
    "132k": bili_video.AudioQuality._132K,
    "192": bili_video.AudioQuality._192K,
    "192k": bili_video.AudioQuality._192K,
    "flac": bili_video.AudioQuality.HI_RES,
    "hires": bili_video.AudioQuality.HI_RES,
    "hi-res": bili_video.AudioQuality.HI_RES,
    "lossless": bili_video.AudioQuality.HI_RES,
    "dolby": bili_video.AudioQuality.DOLBY,
}

_VIDEO_CODEC_ALIASES: dict[str, bili_video.VideoCodecs] = {
    "avc": bili_video.VideoCodecs.AVC,
    "h264": bili_video.VideoCodecs.AVC,
    "h.264": bili_video.VideoCodecs.AVC,
    "hevc": bili_video.VideoCodecs.HEV,
    "hev": bili_video.VideoCodecs.HEV,
    "h265": bili_video.VideoCodecs.HEV,
    "h.265": bili_video.VideoCodecs.HEV,
    "av1": bili_video.VideoCodecs.AV1,
}


def _normalize_urls(
    primary: str, backups: Iterable[str] | None = None
) -> tuple[str, ...]:
    urls = [primary]
    if backups:
        urls.extend(url for url in backups if url)
    return tuple(dict.fromkeys(urls))


def _video_quality(value: str | int | None) -> bili_video.VideoQuality:
    if value is None:
        return bili_video.VideoQuality._8K
    if isinstance(value, int):
        return bili_video.VideoQuality(value)
    normalized = value.strip().lower()
    if normalized == "max":
        return bili_video.VideoQuality._8K
    if normalized == "min":
        return bili_video.VideoQuality._360P
    if alias := _VIDEO_QUALITY_ALIASES.get(normalized):
        return alias
    return bili_video.VideoQuality(int(normalized))


def _audio_quality(value: str | int | None) -> bili_video.AudioQuality:
    if value is None:
        return bili_video.AudioQuality._192K
    if isinstance(value, int):
        return bili_video.AudioQuality(value)
    normalized = value.strip().lower()
    if normalized == "max":
        return bili_video.AudioQuality._192K
    if normalized == "min":
        return bili_video.AudioQuality._64K
    if alias := _AUDIO_QUALITY_ALIASES.get(normalized):
        return alias
    return bili_video.AudioQuality(int(normalized))


def _video_codecs(value: str | Iterable[str] | None) -> list[bili_video.VideoCodecs]:
    if value is None:
        return [
            bili_video.VideoCodecs.AVC,
            bili_video.VideoCodecs.HEV,
            bili_video.VideoCodecs.AV1,
            bili_video.VideoCodecs.UNKNOWN,
        ]
    if isinstance(value, str):
        values = [value]
    else:
        values = list(value)
    codecs: list[bili_video.VideoCodecs] = []
    for item in values:
        codec = _VIDEO_CODEC_ALIASES[item.strip().lower()]
        if codec not in codecs:
            codecs.append(codec)
    if bili_video.VideoCodecs.UNKNOWN not in codecs:
        codecs.append(bili_video.VideoCodecs.UNKNOWN)
    return codecs


def _page_from_raw(index: int, raw: dict[str, Any]) -> PageInfo:
    return PageInfo(
        cid=int(raw["cid"]),
        index=index,
        title=str(raw.get("part") or raw.get("title") or f"P{index}"),
        duration=raw.get("duration"),
    )


def _stream_from_upstream(stream: object) -> StreamInfo:
    if isinstance(stream, bili_video.VideoStreamDownloadURL):
        return StreamInfo(
            kind=StreamKind.VIDEO,
            urls=_normalize_urls(stream.url, stream.backup_url),
            quality_id=stream.video_quality.value,
            quality_label=stream.video_quality.name,
            codec=stream.video_codecs.name.lower(),
            bandwidth=stream.bandwidth,
            mime_type=stream.mime_type,
            width=stream.scale[0],
            height=stream.scale[1],
            frame_rate=stream.frame_rate,
            container="dash",
            raw=stream,
        )
    if isinstance(stream, bili_video.AudioStreamDownloadURL):
        return StreamInfo(
            kind=StreamKind.AUDIO,
            urls=_normalize_urls(stream.url, stream.backup_url),
            quality_id=stream.audio_quality.value,
            quality_label=stream.audio_quality.name,
            codec=stream.codecs,
            bandwidth=stream.bandwidth,
            mime_type=stream.mime_type,
            is_lossless=stream.audio_quality is bili_video.AudioQuality.HI_RES,
            container="dash",
            raw=stream,
        )
    if isinstance(stream, bili_video.FLVStreamDownloadURL):
        return StreamInfo(
            kind=StreamKind.SINGLE,
            urls=(stream.url,),
            container="flv",
            raw=stream,
        )
    if isinstance(stream, bili_video.MP4StreamDownloadURL):
        return StreamInfo(
            kind=StreamKind.SINGLE,
            urls=(stream.url,),
            container="mp4",
            raw=stream,
        )
    raise TypeError(f"unsupported upstream stream type: {type(stream)!r}")


class BilibiliClient:
    """Thin synchronous facade over ``bilibili-api-python``."""

    def __init__(self, credential: Credential | None = None) -> None:
        self.credential = credential or Credential()

    def get_video_info(
        self, *, bvid: str | None = None, aid: int | None = None
    ) -> VideoInfo:
        """Fetch ordinary video metadata and normalize it."""

        video = bili_video.Video(bvid=bvid, aid=aid, credential=self.credential)
        raw_info = sync(video.get_info())
        raw_pages = sync(video.get_pages())
        pages = tuple(
            _page_from_raw(index, page) for index, page in enumerate(raw_pages, 1)
        )
        owner = raw_info.get("owner") or {}
        return VideoInfo(
            bvid=str(raw_info["bvid"]),
            aid=int(raw_info["aid"]),
            title=str(raw_info["title"]),
            pages=pages,
            owner_name=owner.get("name"),
            owner_mid=owner.get("mid"),
            cover_url=raw_info.get("pic"),
            copyright=raw_info.get("copyright"),
            raw=raw_info,
        )

    def get_legacy_video_detail(
        self, *, bvid: str | None = None, aid: int | None = None
    ) -> dict[str, Any]:
        """Fetch ordinary video metadata in the old ``biliapis`` shape."""

        video = bili_video.Video(bvid=bvid, aid=aid, credential=self.credential)
        raw_info = sync(video.get_info())
        raw_info["pages"] = sync(video.get_pages())
        return raw_info

    def get_legacy_video_stream_dash(
        self,
        *,
        bvid: str | None = None,
        aid: int | None = None,
        cid: int | None = None,
        page_index: int | None = None,
    ) -> dict[str, Any]:
        """Fetch ordinary video playurl payload in the old DASH dict shape."""

        video = bili_video.Video(bvid=bvid, aid=aid, credential=self.credential)
        return sync(video.get_download_url(cid=cid, page_index=page_index))

    def get_video_streams(
        self,
        *,
        bvid: str | None = None,
        aid: int | None = None,
        cid: int | None = None,
        page_index: int | None = None,
        html5: bool = False,
    ) -> VideoStreams:
        """Fetch all available stream candidates for one ordinary video page."""

        video = bili_video.Video(bvid=bvid, aid=aid, credential=self.credential)
        raw = sync(video.get_download_url(cid=cid, page_index=page_index, html5=html5))
        detector = bili_video.VideoDownloadURLDataDetecter(raw)
        streams = tuple(
            _stream_from_upstream(stream) for stream in detector.detect_all()
        )
        return VideoStreams(
            video=tuple(
                stream for stream in streams if stream.kind is StreamKind.VIDEO
            ),
            audio=tuple(
                stream for stream in streams if stream.kind is StreamKind.AUDIO
            ),
            single=tuple(
                stream for stream in streams if stream.kind is StreamKind.SINGLE
            ),
            raw=raw,
        )

    def get_best_video_streams(
        self,
        *,
        bvid: str | None = None,
        aid: int | None = None,
        cid: int | None = None,
        page_index: int | None = None,
        video_quality: str | int | None = None,
        audio_quality: str | int | None = None,
        video_codec: str | Iterable[str] | None = None,
        no_hires: bool = False,
        no_hdr: bool = False,
        no_dolby_video: bool = False,
        no_dolby_audio: bool = False,
    ) -> tuple[StreamInfo | None, ...]:
        """Fetch and normalize the best matched stream set.

        DASH streams return ``(video_stream, audio_stream)``. Old-style FLV/MP4
        payloads return a one-item tuple containing the single stream.
        """

        video = bili_video.Video(bvid=bvid, aid=aid, credential=self.credential)
        raw = sync(video.get_download_url(cid=cid, page_index=page_index))
        detector = bili_video.VideoDownloadURLDataDetecter(raw)
        streams = detector.detect_best_streams(
            video_max_quality=_video_quality(video_quality),
            audio_max_quality=_audio_quality(audio_quality),
            codecs=_video_codecs(video_codec),
            no_hires=no_hires,
            no_hdr=no_hdr,
            no_dolby_video=no_dolby_video,
            no_dolby_audio=no_dolby_audio,
        )
        normalized = tuple(
            None if stream is None else _stream_from_upstream(stream)
            for stream in streams
        )
        return normalized

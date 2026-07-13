"""Shared media models for BiliTools.

These models intentionally describe only the data BiliTools needs.  API-specific
payloads from upstream libraries should be normalized into these dataclasses
before they reach download planning or CLI code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class StreamKind(str, Enum):
    """Normalized stream categories used by download planning."""

    VIDEO = "video"
    AUDIO = "audio"
    SINGLE = "single"


@dataclass(slots=True, frozen=True)
class StreamInfo:
    """A normalized downloadable media stream."""

    kind: StreamKind
    urls: tuple[str, ...]
    quality_id: int | None = None
    quality_label: str | None = None
    codec: str | None = None
    bandwidth: int | None = None
    mime_type: str | None = None
    width: int | None = None
    height: int | None = None
    frame_rate: float | None = None
    is_lossless: bool = False
    container: Literal["dash", "flv", "mp4", "unknown"] = "unknown"
    raw: object | None = field(default=None, repr=False, compare=False)

    @property
    def primary_url(self) -> str:
        """Return the first usable URL."""

        return self.urls[0]


@dataclass(slots=True, frozen=True)
class PageInfo:
    """A normalized Bilibili video page / episode page."""

    cid: int
    index: int
    title: str
    duration: int | None = None


@dataclass(slots=True, frozen=True)
class VideoInfo:
    """A normalized ordinary video metadata payload."""

    bvid: str
    aid: int
    title: str
    pages: tuple[PageInfo, ...]
    owner_name: str | None = None
    owner_mid: int | None = None
    cover_url: str | None = None
    copyright: int | None = None
    raw: dict | None = field(default=None, repr=False, compare=False)


@dataclass(slots=True, frozen=True)
class VideoStreams:
    """Normalized stream selection candidates for one video page."""

    video: tuple[StreamInfo, ...]
    audio: tuple[StreamInfo, ...]
    single: tuple[StreamInfo, ...] = ()
    raw: dict | None = field(default=None, repr=False, compare=False)

    @property
    def is_dash(self) -> bool:
        """Whether the payload contains separated video/audio streams."""

        return bool(self.video or self.audio)

    @property
    def is_single_file(self) -> bool:
        """Whether the payload contains an old-style single FLV/MP4 stream."""

        return bool(self.single)

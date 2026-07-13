from bilibili_api import video as bili_video

from bilitools.adapters.bilibili import (
    _audio_quality,
    _stream_from_upstream,
    _video_codecs,
    _video_quality,
)
from bilitools.models import StreamKind


def test_video_quality_aliases():
    assert _video_quality(None) is bili_video.VideoQuality._8K
    assert _video_quality("max") is bili_video.VideoQuality._8K
    assert _video_quality("min") is bili_video.VideoQuality._360P
    assert _video_quality("1080p") is bili_video.VideoQuality._1080P
    assert _video_quality("4k") is bili_video.VideoQuality._4K
    assert _video_quality(80) is bili_video.VideoQuality._1080P


def test_audio_quality_aliases():
    assert _audio_quality(None) is bili_video.AudioQuality._192K
    assert _audio_quality("max") is bili_video.AudioQuality._192K
    assert _audio_quality("min") is bili_video.AudioQuality._64K
    assert _audio_quality("132k") is bili_video.AudioQuality._132K
    assert _audio_quality("flac") is bili_video.AudioQuality.HI_RES
    assert _audio_quality(30280) is bili_video.AudioQuality._192K


def test_video_codecs_aliases_keep_order_and_unknown_fallback():
    assert _video_codecs("avc") == [
        bili_video.VideoCodecs.AVC,
        bili_video.VideoCodecs.UNKNOWN,
    ]
    assert _video_codecs(["hevc", "av1", "hevc"]) == [
        bili_video.VideoCodecs.HEV,
        bili_video.VideoCodecs.AV1,
        bili_video.VideoCodecs.UNKNOWN,
    ]


def test_stream_from_upstream_video_stream():
    stream = bili_video.VideoStreamDownloadURL(
        url="https://example.test/video.m4s",
        video_quality=bili_video.VideoQuality._1080P,
        video_codecs=bili_video.VideoCodecs.AVC,
        backup_url=["https://example.test/video-backup.m4s"],
        bandwidth=1000,
        codecs="avc1.640028",
        frame_rate=30.0,
        scale=(1920, 1080),
        sar=(1, 1),
        mime_type="video/mp4",
        segment_base_initialization="0-1",
        segment_base_index_range="2-3",
    )

    normalized = _stream_from_upstream(stream)

    assert normalized.kind is StreamKind.VIDEO
    assert normalized.urls == (
        "https://example.test/video.m4s",
        "https://example.test/video-backup.m4s",
    )
    assert normalized.quality_id == 80
    assert normalized.quality_label == "_1080P"
    assert normalized.codec == "avc"
    assert normalized.width == 1920
    assert normalized.height == 1080
    assert normalized.container == "dash"


def test_stream_from_upstream_audio_stream():
    stream = bili_video.AudioStreamDownloadURL(
        url="https://example.test/audio.m4s",
        audio_quality=bili_video.AudioQuality.HI_RES,
        backup_url=[],
        bandwidth=1000,
        codecs="fLaC",
        mime_type="audio/flac",
        segment_base_initialization="0-1",
        segment_base_index_range="2-3",
    )

    normalized = _stream_from_upstream(stream)

    assert normalized.kind is StreamKind.AUDIO
    assert normalized.urls == ("https://example.test/audio.m4s",)
    assert normalized.quality_id == 30251
    assert normalized.is_lossless is True
    assert normalized.container == "dash"


def test_stream_from_upstream_single_file_streams():
    flv = _stream_from_upstream(
        bili_video.FLVStreamDownloadURL(url="https://example.test/video.flv")
    )
    mp4 = _stream_from_upstream(
        bili_video.MP4StreamDownloadURL(url="https://example.test/video.mp4")
    )

    assert flv.kind is StreamKind.SINGLE
    assert flv.container == "flv"
    assert mp4.kind is StreamKind.SINGLE
    assert mp4.container == "mp4"

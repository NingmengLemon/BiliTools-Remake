"""Fixtures for pure-function stream-related tests that don't need network access."""

import json
import os
from typing import Any

import pytest

from bilitools.bilicore.threads import SingleVideoThread


@pytest.fixture(scope="session")
def old_single_file_stream_data() -> dict[str, Any]:
    """Mimics the get_download_url result for BV1ds411Z7rQ (old MP4 single-file)."""

    return {
        "format": "hdmp4",
        "quality": 64,
        "timelength": 285014,
        "accept_quality": [32, 16],
        "accept_format": "hdmp4,mp4",
        "durl": [
            {
                "ahead": "",
                "backup_url": [],
                "length": 285014,
                "order": 1,
                "size": 14338331,
                "url": "https://example.test/video.mp4",
                "vhead": "",
            }
        ],
    }


@pytest.fixture(scope="session")
def old_single_file_video_detail() -> dict[str, Any]:
    """Mimics get_video_detail for BV1ds411Z7rQ."""

    return {
        "bvid": "BV1ds411Z7rQ",
        "aid": 1293289,
        "title": "【洛天依】I LOVE U (oCaU Remix)",
        "pic": "https://example.test/cover.jpg",
        "copyright": 1,
        "owner": {"name": "TestUser", "mid": 12345},
        "pages": [
            {
                "cid": 836369,
                "page": 1,
                "part": "【洛天依】I LOVE U (oCaU Remix)",
                "duration": 285,
            }
        ],
    }

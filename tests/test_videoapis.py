import logging
import sys
import os
import json

import pytest
from requests import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from biliapis.apis.video import VideoAPIs  # pylint: disable=C
from biliapis.wbi import CachedWbiManager  # pylint: disable=C

SAVEDIR = "./samples/"
if not os.path.exists(SAVEDIR):
    os.mkdir(SAVEDIR)

session = Session()
apis = VideoAPIs(session, CachedWbiManager(session))


def test_get_detail():
    data = apis.get_video_detail(avid=170001)
    with open(os.path.join(SAVEDIR, "video_detail.json"), "w+", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def test_get_stream():
    streams = apis.get_stream_dash(cid=279786, avid=170001)
    with open(os.path.join(SAVEDIR, "video_streams.json"), "w+", encoding="utf-8") as f:
        json.dump(streams, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main()

import os
import logging
import sys
import json

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from bilicore import parser  # pylint: disable=C0413,E0611

with open("./tests/video_streams_with_flac.json", "r", encoding="utf-8") as fp:
    SAMPLE: dict = json.load(fp)


def test_min():
    v, a = parser.select_quality(SAMPLE, aq="min", vq="min")
    assert v["height"] == 338
    assert a["bandwidth"] == 52761


def test_max():
    v, a = parser.select_quality(SAMPLE, aq="max", vq="max")
    assert v["height"] == 2160
    assert a["bandwidth"] == 706587


def test_spec():
    v, a = parser.select_quality(SAMPLE, aq="132k", vq="1080p")
    assert v["id"] == 80
    assert a["id"] == 30232


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main()

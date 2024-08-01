import logging
import sys
import os
import json

import pytest
from requests import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from biliapis.apis.audio import AudioAPIs  # pylint: disable=C
from biliapis.wbi import CachedWbiManager  # pylint: disable=C

SAVEDIR = "./samples/"
if not os.path.exists(SAVEDIR):
    os.mkdir(SAVEDIR)

session = Session()
apis = AudioAPIs(session, CachedWbiManager(session))


def test_get_detail():
    data = apis.get_info(auid=37787)
    with open(os.path.join(SAVEDIR, "audio_info.json"), "w+", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def test_get_stream():
    streams = apis.get_stream(auid=37787)
    with open(os.path.join(SAVEDIR, "audio_stream.json"), "w+", encoding="utf-8") as f:
        json.dump(streams, f, indent=4, ensure_ascii=False)


def test_get_tags():
    tags = apis.get_tags(auid=37787)
    with open(os.path.join(SAVEDIR, "audio_tags.json"), "w+", encoding="utf-8") as f:
        json.dump(tags, f, indent=4, ensure_ascii=False)


def test_get_playmenu():
    menu = apis.get_playmenu(amid=125312)
    with open(
        os.path.join(SAVEDIR, "audio_playmenu.json"), "w+", encoding="utf-8"
    ) as f:
        json.dump(menu, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main()

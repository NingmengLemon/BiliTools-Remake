import logging
import sys
import os
import json

import pytest
from requests import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from biliapis.apis.media import MediaAPIs  # pylint: disable=C
from biliapis.wbi import CachedWbiManager  # pylint: disable=C

SAVEDIR = "./samples/"
if not os.path.exists(SAVEDIR):
    os.mkdir(SAVEDIR)

session = Session()
apis = MediaAPIs(session, CachedWbiManager(session))


def test_wrong_arg_num():
    with pytest.raises(ValueError):
        apis.get_detail(mdid=1, ssid=1)


def test_get_detail():
    data = apis.get_detail(ssid=1293)
    with open(os.path.join(SAVEDIR, "media_detail.json"), "w+", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    data_by_mdid = apis.get_detail(mdid=1293)
    assert data["title"] == data_by_mdid["title"]


def test_get_info():
    info = apis.get_info(mdid=1293)
    with open(os.path.join(SAVEDIR, "media_info.json"), "w+", encoding="utf-8") as f:
        json.dump(info, f, indent=4, ensure_ascii=False)


def test_get_section():
    sec = apis.get_section(ssid=1293)
    with open(os.path.join(SAVEDIR, "media_section.json"), "w+", encoding="utf-8") as f:
        json.dump(sec, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main()

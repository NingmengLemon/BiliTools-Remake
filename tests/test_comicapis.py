import logging
import sys
import os
import json

import pytest
from requests import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from biliapis.apis.manga import MangaAPIs  # pylint: disable=C
from biliapis.wbi import CachedWbiManager  # pylint: disable=C

SAVEDIR = "./samples/"
if not os.path.exists(SAVEDIR):
    os.mkdir(SAVEDIR)

session = Session()
apis = MangaAPIs(session, CachedWbiManager(session))


def test_get_detail():
    data = apis.get_detail(mcid=32020)
    with open(os.path.join(SAVEDIR, "manga_info.json"), "w+", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def test_get_ep():
    ep = apis.get_episode_info(epid=806132)
    with open(os.path.join(SAVEDIR, "manga_epinfo.json"), "w+", encoding="utf-8") as f:
        json.dump(ep, f, indent=4, ensure_ascii=False)


def test_get_image_flow():
    epid = 806132
    indexs = apis.get_image_index(epid=epid)
    with open(
        os.path.join(SAVEDIR, "manga_imgindex.json"), "w+", encoding="utf-8"
    ) as f:
        json.dump(indexs, f, indent=4, ensure_ascii=False)
    # urls = [i["path"] for i in indexs["images"]]
    urls = [indexs["images"][0]["path"]]
    tokens = apis.get_image_token(*urls)
    with open(
        os.path.join(SAVEDIR, "manga_imgtoken.json"), "w+", encoding="utf-8"
    ) as f:
        json.dump(tokens, f, indent=4, ensure_ascii=False)
    urls = [i["url"] + "?token=" + i["token"] for i in tokens]
    for i, u in enumerate(urls):
        with open(
            os.path.join(SAVEDIR, "manga_img_ep{}_{}.jpg".format(epid, i)), "wb+"
        ) as f:
            f.write(apis.session.get(u, headers=apis.DEFAULT_HEADERS).content)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main()

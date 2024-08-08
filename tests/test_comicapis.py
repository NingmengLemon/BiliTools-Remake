import logging
import os

import pytest

from initapis import apis, dump_data, SAVEDIR


def test_get_detail():
    data = apis.manga.get_detail(mcid=32020)
    dump_data("manga_info.json", data)


def test_get_ep():
    ep = apis.manga.get_episode_info(epid=806132)
    dump_data("manga_epinfo.json", ep)


def test_get_image_flow():
    epid = 806132
    indexs = apis.manga.get_image_index(epid=epid)
    dump_data("manga_imgindex.json", indexs)
    # urls = [i["path"] for i in indexs["images"]]
    urls = [indexs["images"][0]["path"]]
    tokens = apis.manga.get_image_token(*urls)
    dump_data("manga_imgtoken.json", tokens)
    urls = [i["url"] + "?token=" + i["token"] for i in tokens]
    for i, u in enumerate(urls):
        with open(os.path.join(SAVEDIR, f"manga_img_ep{epid}_{i}.jpg"), "wb+") as f:
            f.write(apis.session.get(u, headers=apis.DEFAULT_HEADERS).content)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main()

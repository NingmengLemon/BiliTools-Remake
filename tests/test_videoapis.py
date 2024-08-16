import logging
import os

import pytest

from initapis import apis, dump_data, SAVEDIR
from bilicore import downloader


def test_get_detail():
    data = apis.video.get_video_detail(bvid="BV14h4y1G7Mi")
    dump_data("video_detail.json", data)


def test_get_stream():
    streams = apis.video.get_stream_dash(cid=279786, avid=170001)
    dump_data("video_streams.json", streams)
    downloader.download_common(
        streams["dash"]["video"][0]["base_url"], os.path.join(SAVEDIR, "vstream.m4s")
    )


def test_get_player():
    player = apis.video.get_player_info(cid=1156509226, bvid="BV14h4y1G7Mi")
    dump_data("video_player.json", player)


def test_get_danmaku():
    cid = 1156509226
    with open(os.path.join(SAVEDIR, "danmaku.xml"), "w+", encoding="utf-8") as fp:
        fp.write(apis.video.get_danmaku(cid))


def test_get_pagelist():
    avid = 99999999
    pl = apis.video.get_pagelist(avid=avid)
    dump_data("video_pagelist.json", pl)


def test_videolist_related():
    uid = 37737161
    seaid = 587216
    serid = 2800548
    dump_data(
        "vl_season_content.json",
        apis.video.get_season_content(season_id=seaid, uid=uid),
    )
    dump_data(
        "vl_seasons_series_list.json", apis.video.get_seasons_series_list(uid=uid)
    )
    dump_data("vl_series_list.json", apis.video.get_series_list(uid=uid))
    dump_data(
        "vl_series_content.json",
        apis.video.get_series_content(series_id=serid, uid=uid),
    )
    dump_data("vl_series_info.json", apis.video.get_series_info(series_id=serid))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main()

import logging
import os

import pytest

from init import apis, dump_data, SAVEDIR


def test_get_detail():
    data = apis.video.get_video_detail(bvid="BV14h4y1G7Mi")
    dump_data("video_detail.json", data)


def test_get_stream():
    streams = apis.video.get_stream_dash(cid=279786, avid=170001)
    dump_data("video_streams.json", streams)


def test_get_player():
    player = apis.video.get_player_info(cid=1156509226, bvid="BV14h4y1G7Mi")
    dump_data("video_player.json", player)


def test_get_danmaku():
    cid = 1156509226
    with open(os.path.join(SAVEDIR, "danmaku.xml"), "w+", encoding="utf-8") as fp:
        fp.write(apis.video.get_danmaku(cid))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main()

import logging
import pytest

from initapis import apis, dump_data


def test_get_detail():
    data = apis.audio.get_info(auid=37787)
    dump_data("audio_info.json", data)


def test_get_stream():
    streams = apis.audio.get_stream(auid=37787)
    dump_data("audio_stream.json", streams)


def test_get_tags():
    tags = apis.audio.get_tags(auid=37787)
    dump_data("audio_tags.json", tags)


def test_get_playmenu():
    amid = 125312
    menu = apis.audio.get_playmenu_content(amid=amid)
    dump_data("audio_playmenu.json", menu)
    info = apis.audio.get_playmenu_info(amid=amid)
    dump_data("audio_playmenu_info.json", info)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main()

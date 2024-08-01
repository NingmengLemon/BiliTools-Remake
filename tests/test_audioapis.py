import logging
import pytest

from init import apis, dump_data


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
    menu = apis.audio.get_playmenu(amid=125312)
    dump_data("audio_playmenu.json", menu)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main()

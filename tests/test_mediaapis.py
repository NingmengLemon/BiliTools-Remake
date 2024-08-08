import logging

import pytest

from initapis import apis, dump_data


def test_wrong_arg_num():
    with pytest.raises(ValueError):
        apis.media.get_detail(mdid=1, ssid=1)


def test_get_detail():
    data = apis.media.get_detail(ssid=1293)
    dump_data("media_detail.json", data)
    data_by_mdid = apis.media.get_detail(mdid=1293)
    assert data["title"] == data_by_mdid["title"]


def test_get_info():
    info = apis.media.get_info(mdid=1293)
    dump_data("media_info.json", info)


def test_get_section():
    sec = apis.media.get_section(ssid=1293)
    dump_data("media_section.json", sec)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main()

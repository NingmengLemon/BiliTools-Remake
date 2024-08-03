import os
import logging
import sys
import time

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from bilicore import downloader  # pylint: disable=C0413,E0611

SAVEDIR = "./samples/"
if not os.path.exists(SAVEDIR):
    os.mkdir(SAVEDIR)


TEST_LINKS = (
    ("https://web.hycdn.cn/arknights/files/20240730/Pepe.rar", "pepe.rar"),
    ("http://deb.monblog.top:10712/files/Adobe_Illustrator_2022_SP.zip", "ai2022.zip"),
    (
        "https://mirror.nyist.edu.cn/ubuntu-releases/24.04/ubuntu-24.04-desktop-amd64.iso",
        "ubuntu2404_amd64.iso",
    ),
)


def test_common_downloader():
    url, filename = TEST_LINKS[0]
    downloader.download_common(
        url,
        os.path.join(SAVEDIR, filename),
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        },
        hook_func=lambda x, y: print(x, "/", y, "bytes complete"),
    )


def test_multithread_downloader():
    url, filename = TEST_LINKS[2]
    d = downloader.MultiThreadDownloader(
        url,
        os.path.join(SAVEDIR, filename),
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        },
        threadnum=8,
    )
    d.start()
    while d.is_alive():
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            d.stop()
            break
    if d.exception:
        raise d.exception
    if excs := d.child_exceptions:
        raise excs[0]


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main()

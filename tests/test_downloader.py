import os
import logging
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core import downloader  # pylint: disable=C0413,E0611

SAVEDIR = "./samples/"
if not os.path.exists(SAVEDIR):
    os.mkdir(SAVEDIR)


def test_common_downloader():
    downloader.download_common(
        "https://web.hycdn.cn/arknights/files/20240730/Pepe.rar",
        os.path.join(SAVEDIR, "pepe.zip"),
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        },
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main()

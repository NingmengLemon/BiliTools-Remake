import logging
import pytest

from initapis import apis, SAVEDIR
from bilicore import core


def test_commonvideo():
    p = core.SingleVideoProcess(apis, 171776208, avid=99999999, savedir=SAVEDIR)
    p.start()
    p.join()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main()

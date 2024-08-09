import logging
import pytest

from initapis import apis, SAVEDIR
from bilicore import core


def test_commonvideo():
    p = core.SingleVideoProcess(apis, 171776208, avid=99999999, savedir=SAVEDIR)
    p.start()
    p.join()
    assert p.exception is None, p.exception


def test_commonvideo_audio():
    p = core.SingleVideoProcess(
        apis, 171776208, avid=99999999, savedir=SAVEDIR, audio_only=True
    )
    p.start()
    p.join()
    assert p.exception is None, p.exception


def test_audio():
    p = core.SingleAudioProcess(apis, 37787, SAVEDIR)
    p.start()
    p.join()
    assert p.exception is None, p.exception


def test_manga():
    p = core.SingleMangaChapterProcess(apis, 806132, SAVEDIR)
    p.start()
    p.join()
    assert p.exception is None, p.exception


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main()

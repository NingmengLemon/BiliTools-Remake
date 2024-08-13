import logging
import pytest

from initapis import apis, SAVEDIR
from bilicore import core


def test_commonvideo():
    p = core.SingleVideoThread(apis, 171776208, avid=99999999, savedir=SAVEDIR)
    p.start()
    p.join()
    assert not bool(p.exceptions), p.exceptions


def test_commonvideo_audio():
    p = core.SingleVideoThread(
        apis, 171776208, avid=99999999, savedir=SAVEDIR, audio_only=True
    )
    p.start()
    p.join()
    assert not bool(p.exceptions), p.exceptions


def test_audio():
    p = core.SingleAudioThread(apis, 37787, SAVEDIR)
    p.start()
    p.join()
    assert not bool(p.exceptions), p.exceptions


def test_manga():
    p = core.SingleMangaChapterThread(apis, 806132, SAVEDIR)
    p.start()
    p.join()
    assert not bool(p.exceptions), p.exceptions


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main()

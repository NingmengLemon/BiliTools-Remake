from typing import TypeAlias

from ..bilicore.threads import (
    SingleAudioThread,
    SingleMangaChapterThread,
    SingleVideoThread,
)

__all__ = ["WorkerThread"]

WorkerThread: TypeAlias = (
    SingleVideoThread | SingleAudioThread | SingleMangaChapterThread
)

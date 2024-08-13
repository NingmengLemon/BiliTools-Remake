from typing import TypeAlias

from bilicore.core import SingleVideoThread, SingleAudioThread, SingleMangaChapterThread

__all__ = ["WorkerThread"]

WorkerThread: TypeAlias = (
    SingleVideoThread | SingleAudioThread | SingleMangaChapterThread
)

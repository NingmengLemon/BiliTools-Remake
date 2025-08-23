from typing import TypeAlias

from bilicore.threads import SingleVideoThread, SingleAudioThread, SingleMangaChapterThread

__all__ = ["WorkerThread"]

WorkerThread: TypeAlias = (
    SingleVideoThread | SingleAudioThread | SingleMangaChapterThread
)

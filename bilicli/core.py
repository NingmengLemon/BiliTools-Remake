from typing import Literal, Optional, Iterable, Any
import threading

from bilicore import (
    download_common,
    MultiThreadDownloader,
    DownloadThread,
    select_quality,
)
from biliapis.utils import remove_none
from biliapis import APIContainer


class SingleVideoProcess(threading.Thread):
    def __init__(
        self,
        apis: APIContainer,
        cid: int,
        *,
        avid: Optional[int] = None,
        bvid: Optional[str] = None,
        audio_only: bool = False,
        video_data: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(daemon=False)
        if (avid is None) == (bvid is None):
            raise ValueError("need ONE between avid and bvid")
        self._cid = cid
        self._id = remove_none({"avid": avid, "bvid": bvid})
        self._apis = apis
        self._audio_only = audio_only
        self._video_data = video_data if video_data else None

    def run(self):
        if self._video_data is None:
            self._video_data = self._apis.video.get_video_detail(**self._id)
        vdata = self._video_data
        if vdata:
            assert self._cid in [p["cid"] for p in vdata["pages"]], "wrong cid"
        player_info = self._apis.video.get_player_info(vdata[""])

    def stop(self):
        pass

    def pause(self):
        pass

    def resume(self):
        pass

    def observe(self):
        pass


def process(
    mode: Literal["video", "media", "manga", "audio", "tbd"], savedir: str, **kwargs
):
    """ """
    pass


def _process_video(savedir: str, **kwargs):
    pass


def _process_media(savedir: str, **kwargs):
    pass

from typing import Optional

from biliapis import APIContainer
from bilicore.core import SingleVideoThread
from bilicli import printers, utils


class CliCore:
    def __init__(self, apis: APIContainer) -> None:
        self.__apis = apis

    @property
    def _apis(self):
        return self.__apis

    def _common_video_process(
        self, savedir: Optional[str], *, avid=None, bvid=None, **options
    ):
        video_data = self._apis.video.get_video_detail(avid=avid, bvid=bvid)
        printers.print_video_info(video_data)
        pindexs = utils.parse_index_option(options.get("index"))  # 从1始计
        if not savedir:
            return
        pages = (
            video_data["pages"]
            if pindexs is None
            else [
                page for i, page in enumerate(video_data["pages"]) if i + 1 in pindexs
            ]
        )
        utils.run_threads(
            [
                SingleVideoThread(
                    self._apis,
                    page["cid"],
                    bvid=video_data["bvid"],
                    savedir=savedir,
                    **options,
                    video_data=video_data,
                )
                for page in pages
            ]
        )

    def _media_process(
        self, savedir: Optional[str], *, ssid=None, mdid=None, epid=None, **options
    ):
        media_detail = self._apis.media.get_detail(mdid=mdid, ssid=ssid, epid=epid)
        printers.print_media_detail(media_detail)
        pindexs = utils.parse_index_option(options.get("index"))  # 从1始计
        if not savedir:
            return
        eps = []
        # TODO: 继续写

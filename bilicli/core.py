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
        indexs = utils.parse_index_option(options.get("index"))
        printers.print_video_info(video_data, indexs)
        if not savedir:
            return
        pages = (
            video_data["pages"]
            if indexs is None
            else [video_data["pages"][i] for i in indexs]
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

    def _media_process(self, **options):
        pass

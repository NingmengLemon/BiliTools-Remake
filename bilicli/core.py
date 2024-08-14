from typing import Optional, Any

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
        pindexs = set(utils.parse_index_option(options.get("index")))  # 从1始计
        if not savedir:
            return
        pages = [
            page
            for i, page in enumerate(video_data["pages"])
            if i + 1 in pindexs or not pindexs
        ]
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
        if not savedir:
            return
        pindexs = set(utils.parse_index_option(options.get("index")))  # 从1始计
        # 超出正片分P索引的作为番外处理，但不指定索引则还是只处理正片
        eps = media_detail.get("episodes", [])
        eps_to_handle: list[tuple[int, dict[str, Any]]] = [
            (i + 1, ep) for i, ep in enumerate(eps) if i + 1 in pindexs or not pindexs
        ]
        offset = len(eps)
        if (secs := media_detail.get("section", [])) and pindexs:
            for sec in secs:
                eps = sec.get("episodes", [])
                for i, ep in enumerate(eps):
                    if (reali := i + 1 + offset) in pindexs:
                        eps_to_handle.append((reali, ep))
                offset += len(eps)
        utils.run_threads(
            [
                SingleVideoThread(
                    self._apis,
                    cid=ep["cid"],
                    bvid=ep["bvid"],
                    savedir=savedir,
                    **options,
                    title=media_detail["season_title"],
                    pindex=i,
                    ptitle=utils.generate_media_ptitle(**ep, i=i),
                )
                for i, ep in eps_to_handle
            ]
        )

    def _manga_process(self, savedir: Optional[str], *, mcid: int, **options):
        # TODO: write this
        return NotImplemented

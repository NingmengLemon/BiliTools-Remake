from typing import Optional, Any, Callable
import functools
import math

from biliapis import APIContainer
from bilicore.threads import (
    SingleVideoThread,
    SingleAudioThread,
    SingleMangaChapterThread,
)
from . import printers, utils


def check_exceptions(func: Callable[..., Optional[list[Exception]]]):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        excs = func(*args, **kwargs)
        print("\nall done!")
        if excs:
            print(f"{len(excs)} exception(s) occurred, plz check log")

    return wrapped


class CliCore:
    def __init__(self, apis: APIContainer) -> None:
        self.__apis = apis
        self._idname_to_procmethod_map: list[tuple[tuple[str, ...], Callable, bool]] = [
            (("bvid", "avid"), self._common_video_process, False),
            (("mdid", "ssid", "epid"), self._media_process, False),
            (("auid",), self._audio_process, False),
            (("amid",), self._audio_playmenu_process, False),
            (("mcid",), self._manga_process, False),
            (("series_id",), self._video_series_process, True),
            (("season_id",), self._video_season_process, True),
        ]

    @property
    def _apis(self):
        return self.__apis

    @check_exceptions
    def _common_video_process(
        self, savedir: Optional[str], *, avid=None, bvid=None, **options
    ):
        video_data = self._apis.video.get_video_detail(avid=avid, bvid=bvid)
        printers.print_video_info(video_data)
        pindexs = utils.parse_index_option(options.get("index"))  # 从1始计
        if not savedir:
            return
        print("\nstarting download...\n")
        pages = [
            page
            for i, page in enumerate(video_data["pages"])
            if i + 1 in pindexs or not pindexs
        ]
        if not pages:
            return
        return utils.run_threads(
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
            ],
            max_worker=options.get("max_worker", 4),
        )

    @check_exceptions
    def _media_process(
        self, savedir: Optional[str], *, ssid=None, mdid=None, epid=None, **options
    ):
        media_detail = self._apis.media.get_detail(mdid=mdid, ssid=ssid, epid=epid)
        printers.print_media_detail(media_detail)
        if not savedir:
            return
        print("\nstarting download...\n")
        pindexs = utils.parse_index_option(options.get("index"))  # 从1始计
        # 超出正片分P索引的作为番外处理，不指定索引则只处理正片
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
        if not eps_to_handle:
            return
        return utils.run_threads(
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
            ],
            max_worker=options.get("max_worker", 4),
        )

    @check_exceptions
    def _manga_process(self, savedir: Optional[str], *, mcid: int, **options):
        manga_info = self._apis.manga.get_detail(mcid=mcid)
        if "ep_list" in manga_info and manga_info.get("ep_list"):
            manga_info["ep_list"].sort(key=lambda x: x["ord"])
        else:
            manga_info["ep_list"] = []
        printers.print_manga_info(manga_info)
        if not savedir:
            return
        pindexs = utils.parse_index_option(options.get("index"))
        print("\nstarting download...\n")
        eps_to_handle = [
            page
            for i, page in enumerate(manga_info["ep_list"])
            if i + 1 in pindexs or not pindexs
        ]
        if not eps_to_handle:
            return
        return utils.run_threads(
            [
                SingleMangaChapterThread(
                    apis=self._apis, epid=ep["id"], savedir=savedir
                )
                for ep in eps_to_handle
            ],
            max_worker=options.get("max_worker", 4),
            unit="it",
        )

    @check_exceptions
    def _audio_process(self, savedir: Optional[str], *, auid: int, **options):
        audio_info = self._apis.audio.get_info(auid=auid)
        printers.print_audio_info(audio_info)
        if not savedir:
            return
        print("\nstarting download...\n")
        return utils.run_threads(
            [
                SingleAudioThread(
                    self._apis,
                    auid=auid,
                    savedir=savedir,
                    **options,
                    audio_data=audio_info,
                )
            ]
        )

    @check_exceptions
    def _audio_playmenu_process(self, savedir: Optional[str], *, amid: int, **options):
        page_size = 50  # max=100
        info = self._apis.audio.get_playmenu_info(amid=amid)
        content = self._apis.audio.get_playmenu_content(
            amid=amid, page=1, page_size=page_size
        )
        songlist: list[dict[str, Any]] = content["data"]
        while content["curPage"] < content["pageCount"]:
            content = self._apis.audio.get_playmenu_content(
                amid=amid, page=content["curPage"] + 1, page_size=page_size
            )
            songlist += content["data"]

        printers.print_audio_playmenu_info(info, songlist)
        if not savedir:
            return
        print("\nstarting download...\n")
        pindexs = utils.parse_index_option(options.get("index"))
        return utils.run_threads(
            [
                SingleAudioThread(
                    self._apis,
                    auid=song["id"],
                    savedir=savedir,
                    **options,
                    audio_data=song,
                )
                for i, song in enumerate(songlist)
                if i + 1 in pindexs or not pindexs
            ]
        )

    @check_exceptions
    def _video_series_process(
        self,
        savedir: Optional[str],
        *,
        series_id: int,
        all_ids: Optional[dict[str, str | int]] = None,
        **options,
    ):
        if not all_ids:
            all_ids = {}
        series = self._apis.video.get_series_info(series_id)["meta"]
        _, videos = utils.query_all_pages(
            functools.partial(
                self._apis.video.get_series_content,
                series_id=series_id,
                uid=all_ids.get("uid", 1),
            ),
            page_size=100,
            curr=lambda x: x["page"]["num"],
            total=lambda x: math.ceil(x["page"]["total"] / x["page"]["size"]),
            archives=lambda x: x["archives"],
        )
        printers.print_series(series, videos)
        if not savedir:
            return
        pindexs = utils.parse_index_option(options.get("index"))
        print("preparing...")
        videos_to_handle = videos_to_handle = utils.process_videolist_to_pagelist(
            self._apis, videos, pindexs
        )
        if not videos_to_handle:
            return
        return utils.run_threads(
            [
                SingleVideoThread(
                    self._apis, cid=cid, bvid=bvid, savedir=savedir, **options
                )
                for bvid, cid in videos_to_handle
            ]
        )

    @check_exceptions
    def _video_season_process(
        self,
        savedir: Optional[str],
        *,
        season_id: int,
        all_ids: Optional[dict[str, str | int]] = None,
        **options,
    ):
        if not all_ids:
            all_ids = {}
        season, videos = utils.query_all_pages(
            functools.partial(
                self._apis.video.get_season_content,
                season_id=season_id,
                uid=all_ids.get("uid", 1),
            ),
            page_size=100,
            curr=lambda x: x["page"]["page_num"],
            total=lambda x: math.ceil(x["page"]["total"] / x["page"]["page_size"]),
            archives=lambda x: x["archives"],
        )
        season = season["meta"]
        printers.print_season(season, videos)
        if not savedir:
            return
        pindexs = utils.parse_index_option(options.get("index"))
        print("preparing...")
        videos_to_handle = utils.process_videolist_to_pagelist(
            self._apis, videos, pindexs
        )
        if not videos_to_handle:
            return
        return utils.run_threads(
            [
                SingleVideoThread(
                    self._apis, cid=cid, bvid=bvid, savedir=savedir, **options
                )
                for bvid, cid in videos_to_handle
            ]
        )

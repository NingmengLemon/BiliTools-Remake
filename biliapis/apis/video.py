from typing import Any, Generator, Callable
import functools
import logging

from requests import Session

from biliapis import template
from biliapis import checker
from biliapis import utils
from biliapis.error import BiliError
from biliapis.wbi import CachedWbiManager


class VideoAPIs(template.APITemplate):
    _API_DETAIL = "https://api.bilibili.com/x/web-interface/view"
    _API_STREAM_WBI = "https://api.bilibili.com/x/player/wbi/playurl"
    _APIS_STREAM_FALLBACK = (
        ("https://api.bilibili.com/pgc/player/web/v2/playurl", "data"),
        ("https://api.bilibili.com/pgc/player/web/playurl", "result"),
        ("https://api.bilibili.com/x/player/playurl", "result"),
    )
    _API_PLAYER = "https://api.bilibili.com/x/player/v2"
    _API_PAGELIST = "https://api.bilibili.com/x/player/pagelist"
    # 用户创建的视频列表分成 Season 和 Series 两种
    _API_SEASON_CONTENT = (  # 获取单个season的内容
        "https://api.bilibili.com/x/polymer/web-space/seasons_archives_list"
    )
    _API_SEASONS_SERIES_LIST = (
        # 同时获取一个用户创建的season和series们，每个season/series的内容不完整
        "https://api.bilibili.com/x/polymer/web-space/seasons_series_list"
    )
    _API_SERIES_LIST = (  # 同时获取一个用户创建的series们，每个series的内容不完整
        "https://api.bilibili.com/x/polymer/web-space/home/seasons_series"
    )
    _API_SERIES_CONTENT = (  # 获取单个series的内容
        "https://api.bilibili.com/x/series/archives"
    )
    _API_SERIES_INFO = (  # 获取单个series的信息
        "https://api.bilibili.com/x/series/series"
    )

    def __init__(self, session: Session, wbimanager: CachedWbiManager) -> None:
        super().__init__(session, wbimanager)
        factory = self.__get_stream_dash_fallback_factory()
        self._get_stream_dash_fallback = utils.fallback((BiliError,))(next(factory))
        for func in factory:
            self._get_stream_dash_fallback.register(func)

    @utils.pick_data()
    @checker.check_abvid
    @checker.check_bilicode()
    @template.request_template()
    def get_video_detail(self, *, avid=None, bvid=None):
        params = utils.remove_none({"aid": avid, "bvid": bvid})
        return VideoAPIs._API_DETAIL, {"params": params}

    @checker.check_abvid
    def get_stream_dash(self, cid: int, *, avid=None, bvid=None) -> dict[str, Any]:
        params = {
            "cid": cid,
            "fnval": 16 | 64 | 128 | 1024,
            "fourk": 1,
        }
        params.update(
            utils.remove_none(
                {
                    "avid": avid,
                    "bvid": bvid,
                }
            )
        )
        params_signed = self._wbimanager.sign(params.copy())
        try:
            return self._get_stream_dash_wbi(params_signed)
        except BiliError as e:
            logging.warning("Error while fetching stream with wbi: %s", e)
        return self._get_stream_dash_fallback(params)

    @utils.pick_data()
    @checker.check_bilicode()
    @template.request_template()
    def _get_stream_dash_wbi(self, params_signed: dict):
        return VideoAPIs._API_STREAM_WBI, {"params": params_signed}

    def __get_stream_dash_fallback_factory(self) -> Generator[Callable, None, None]:
        def get_fallback(api: str, params_: dict):
            return api, {"params": params_}

        for a, k in VideoAPIs._APIS_STREAM_FALLBACK:
            yield utils.decorate(
                functools.partial(get_fallback, a),
                template.request_template(),
                checker.check_bilicode(),
                utils.pick_data(k),
            )

    @utils.pick_data()
    @checker.check_abvid
    @checker.check_bilicode()
    @template.request_template()
    def get_player_info(self, cid: int, *, avid=None, bvid=None):
        """获取web端播放器的元数据，包括字幕文件

        要获取字幕文件需要登录（否则字幕列表为空）"""
        params = {"cid": cid}
        params.update(
            utils.remove_none(
                {
                    "avid": avid,
                    "bvid": bvid,
                }
            )
        )
        return VideoAPIs._API_PLAYER, {"params": params}

    @template.request_template(handle="str")
    def get_danmaku(self, cid):
        """获取弹幕xml文件"""
        return f"https://comment.bilibili.com/{cid}.xml"

    @template.request_template(handle="str")
    def get_danmaku_new(self, cid):
        return f"https://api.bilibili.com/x/v1/dm/list.so?oid={cid}"

    @utils.pick_data()
    @checker.check_abvid
    @checker.check_bilicode()
    @template.request_template()
    def get_pagelist(self, *, avid=None, bvid=None):
        params = utils.remove_none({"aid": avid, "bvid": bvid})
        return VideoAPIs._API_PAGELIST, {"params": params}

    @utils.pick_data()
    @checker.check_bilicode()
    @template.request_template()
    def get_season_content(
        self, season_id: int, uid: int, page=1, page_size=100, sort_reverse=False
    ):
        """
        获取用户创建的合集中的视频列表
        """
        return VideoAPIs._API_SEASON_CONTENT, {
            "params": self._wbimanager.sign(
                {
                    "mid": uid,
                    "season_id": season_id,
                    "sort_reverse": sort_reverse,
                    "page_num": page,
                    "page_size": page_size,
                    "web_location": "0.0",
                }
            )
        }

    @utils.pick_data()
    @checker.check_bilicode()
    @template.request_template()
    def get_seasons_series_list(self, uid: int, page=1, page_size=20):
        """
        获取用户创建的所有合集和系列，单个合集或系列的内容不完整
        """
        return VideoAPIs._API_SEASONS_SERIES_LIST, {
            "params": self._wbimanager.sign(
                {
                    "mid": uid,
                    "page_num": page,
                    "page_size": page_size,
                    "web_location": "0.0",
                }
            )
        }

    @utils.pick_data()
    @checker.check_bilicode()
    @template.request_template()
    def get_series_list(self, uid: int, page=1, page_size=20):
        """
        获取用户创建的所有系列，单个系列内容不完整
        """
        return VideoAPIs._API_SERIES_LIST, {
            "params": self._wbimanager.sign(
                {
                    "mid": uid,
                    "page_num": page,
                    "page_size": page_size,
                    "web_location": "0.0",
                }
            )
        }

    @utils.pick_data()
    @checker.check_bilicode()
    @template.request_template()
    def get_series_content(
        self, series_id: int, uid: int, page=1, page_size=20, ascending_sort=False
    ):
        """
        获取单个系列的内容
        """
        return VideoAPIs._API_SERIES_CONTENT, {
            "params": {
                "mid": uid,
                "series_id": series_id,
                "pn": page,
                "ps": page_size,
                "sort": ("asc" if ascending_sort else "desc"),
                "only_normal": True,
            }
        }

    @utils.pick_data()
    @checker.check_bilicode()
    @template.request_template()
    def get_series_info(self, series_id: int):
        """获取单个系列的信息"""
        return VideoAPIs._API_SERIES_INFO, {"params": {"series_id": series_id}}

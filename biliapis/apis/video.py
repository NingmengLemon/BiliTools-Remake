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
    APIS_STREAM_FALLBACK = (
        ("https://api.bilibili.com/pgc/player/web/v2/playurl", "data"),
        ("https://api.bilibili.com/pgc/player/web/playurl", "result"),
        ("https://api.bilibili.com/x/player/playurl", "result"),
    )
    _API_PLAYER = "https://api.bilibili.com/x/player/v2"

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

        for a, k in VideoAPIs.APIS_STREAM_FALLBACK:
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
        '''获取web端播放器的元数据，包括字幕文件
        
        要获取字幕文件需要登录（否则字幕列表为空），
        判断字幕是否是AI生成可以判断URL中是否包含`ai_subtitle`'''
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

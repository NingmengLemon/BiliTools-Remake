from typing import Any, Optional

from biliapis.template import APITemplate

class VideoAPIs(APITemplate):
    def get_video_detail(
        self, *, avid: Optional[int] = None, bvid: Optional[str] = None
    ) -> dict[str, Any]: ...
    def get_stream_dash(
        self, cid: int, *, avid: Optional[int] = None, bvid: Optional[str] = None
    ) -> dict[str, Any]: ...
    def _get_stream_dash_wbi(self, params_signed: dict) -> dict[str, Any]: ...
    def get_player_info(
        self, cid: int, *, avid: Optional[int] = None, bvid: Optional[str] = None
    ) -> dict[str, Any]: ...
    def get_danmaku(self, cid: int) -> str: ...
    def get_danmaku_new(self, cid: int) -> str: ...
    def get_pagelist(
        self, *, avid: Optional[int] = None, bvid: Optional[str] = None
    ) -> list[dict[str, Any]]: ...
    def get_season_content(
        self,
        season_id: int,
        uid: int,
        page: int = 1,
        page_size: int = 100,
        sort_reverse: bool = False,
    ) -> dict[str, Any]: ...
    def get_seasons_series_list(
        self, uid: int, page: int = 1, page_size: int = 20
    ) -> dict[str, Any]: ...
    def get_series_list(
        self, uid: int, page: int = 1, page_size: int = 20
    ) -> dict[str, Any]: ...
    def get_series_content(
        self,
        series_id: int,
        uid: int,
        page: int = 1,
        page_size: int = 20,
        ascending_sort: bool = False,
    ) -> dict[str, Any]: ...
    def get_series_info(self, series_id: int) -> dict[str, Any]: ...

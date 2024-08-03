from typing import Any, Literal, Optional

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

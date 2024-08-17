from typing import Optional, Any

from .. import checker
from .. import utils
from .. import template


class MediaAPIs(template.APITemplate):
    _API_SEASON = "https://api.bilibili.com/pgc/view/web/season"
    _API_MEDIA = "https://api.bilibili.com/pgc/review/user"
    _API_SECTION = "https://api.bilibili.com/pgc/web/season/section"

    def get_detail(
        self,
        *,
        mdid: Optional[int] = None,
        ssid: Optional[int] = None,
        epid: Optional[int] = None,
    ) -> dict[str, Any]:
        """获取剧集的详细信息

        应当从三个参数中选择一个来传入，应用顺序：mdid - ssid - epid"""
        if sum(bool(i) for i in (mdid, ssid, epid)) != 1:
            raise ValueError("Must pass ONE parameter from `mdid` `ssid` and `epid`")
        if mdid:
            media = self.get_info(mdid=mdid)
            ssid = media.get("media", {}).get("season_id")  # pylint: disable=E1101
        if ssid:
            return self._get_detail_via_ssid(ssid=ssid)
        if epid:
            return self._get_detail_via_epid(epid=epid)
        raise ValueError("Must pass a parameter from `mdid` `ssid` and `epid`")

    @utils.pick_data("result")
    @checker.check_bilicode()
    @template.request_template(allow_cache=True)
    def get_section(self, ssid: int):
        """获取剧集的分集信息，需求 season_id"""
        return MediaAPIs._API_SECTION, {"params": {"season_id": ssid}}

    @utils.pick_data("result")
    @checker.check_bilicode()
    @template.request_template(allow_cache=True)
    def get_info(self, mdid: int):
        """获取剧集信息，需求 media_id"""
        return MediaAPIs._API_MEDIA, {"params": {"media_id": mdid}}

    @utils.pick_data("result")
    @checker.check_bilicode()
    @template.request_template(allow_cache=True)
    def _get_detail_via_ssid(self, ssid: int):
        return MediaAPIs._API_SEASON, {"params": {"season_id": ssid}}

    @utils.pick_data("result")
    @checker.check_bilicode()
    @template.request_template(allow_cache=True)
    def _get_detail_via_epid(self, epid: int):
        return MediaAPIs._API_SEASON, {"params": {"ep_id": epid}}

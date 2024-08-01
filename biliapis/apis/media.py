from typing import Optional

from biliapis import checker
from biliapis import utils
from biliapis import template


class MediaAPIs(template.APITemplate):
    API_SEASON = "https://api.bilibili.com/pgc/view/web/season"
    API_MEDIA = "https://api.bilibili.com/pgc/review/user"
    API_SECTION = "https://api.bilibili.com/pgc/web/season/section"

    def get_detail(
        self,
        *,
        mdid: Optional[int] = None,
        ssid: Optional[int] = None,
        epid: Optional[int] = None,
    ):
        """获取剧集的详细信息

        应当从三个参数中选择一个来传入，应用顺序：mdid - ssid - epid"""
        if sum(bool(i) for i in (mdid, ssid, epid)) != 1:
            raise ValueError("Must pass ONE parameter from `mdid` `ssid` and `epid`")
        if mdid:
            media = self.get_info(mdid=mdid)
            ssid = media["media"]["season_id"]
        if ssid:
            return self._get_detail_via_ssid(ssid=ssid)
        if epid:
            return self._get_detail_via_epid(epid=epid)

    @utils.pick_data("result")
    @checker.check_bilicode()
    @template.request_template()
    def get_section(self, ssid: int):
        """获取剧集的分集信息，需求 season_id"""
        return MediaAPIs.API_SECTION, {"params": {"season_id": ssid}}

    @utils.pick_data("result")
    @checker.check_bilicode()
    @template.request_template()
    def get_info(self, mdid: int):
        """获取剧集信息，需求 media_id"""
        return MediaAPIs.API_MEDIA, {"params": {"media_id": mdid}}

    @utils.pick_data("result")
    @checker.check_bilicode()
    @template.request_template()
    def _get_detail_via_ssid(self, ssid: int):
        return MediaAPIs.API_SEASON, {"params": {"season_id": ssid}}

    @utils.pick_data("result")
    @checker.check_bilicode()
    @template.request_template()
    def _get_detail_via_epid(self, epid: int):
        return MediaAPIs.API_SEASON, {"params": {"ep_id": epid}}

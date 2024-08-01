from typing import Literal

from biliapis import checker
from biliapis import utils
from biliapis import template


class AudioAPIs(template.APITemplate):
    API_INFO = "https://www.bilibili.com/audio/music-service-c/web/song/info"
    API_STREAM = "https://api.bilibili.com/audio/music-service-c/url"
    API_LYRICS = "https://www.bilibili.com/audio/music-service-c/web/song/lyric"
    API_TAGS = "https://www.bilibili.com/audio/music-service-c/web/tag/song"
    API_PLAYMENU = "https://www.bilibili.com/audio/music-service-c/web/song/of-menu"

    @utils.pick_data()
    @checker.check_bilicode(msgkey="msg")
    @template.request_template()
    def get_info(self, auid: int):
        """获取单曲信息"""
        return AudioAPIs.API_INFO, {"params": {"sid": auid}}

    @utils.pick_data()
    @checker.check_bilicode(msgkey="msg")
    @template.request_template()
    def get_stream(self, auid: int, quality: Literal[0, 1, 2, 3] = 3):
        """
        单曲取流

        quality = 0(128K) / 1(192K) / 2(320K) / 3(FLAC)
        """
        return AudioAPIs.API_STREAM, {
            "params": {
                "songid": auid,
                "quality": quality,
                "privilege": 2,
                "mid": 0,
                "platform": "web",
            }
        }

    @utils.pick_data()
    @checker.check_bilicode(msgkey="msg")
    @template.request_template()
    def get_tags(self, auid: int):
        """获取单曲标签"""
        return AudioAPIs.API_TAGS, {"params": {"sid": auid}}

    @utils.pick_data()
    @checker.check_bilicode(msgkey="msg")
    @template.request_template()
    def get_playmenu(self, amid: int, page: int = 1, page_size: int = 100):
        """获取歌单"""
        return AudioAPIs.API_PLAYMENU, {
            "params": {"sid": amid, "pn": page, "ps": page_size}
        }

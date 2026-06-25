from .. import checker
from .. import utils
from .. import template


class AudioAPIs(template.APITemplate):
    _API_INFO = "https://www.bilibili.com/audio/music-service-c/web/song/info"
    _API_STREAM = "https://api.bilibili.com/audio/music-service-c/url"
    _API_TAGS = "https://www.bilibili.com/audio/music-service-c/web/tag/song"
    _API_PLAYMENU_CONTENT = (
        "https://www.bilibili.com/audio/music-service-c/web/song/of-menu"
    )
    _API_PLAYMENU_INFO = "https://www.bilibili.com/audio/music-service-c/web/menu/info"

    @utils.pick_data()
    @checker.check_bilicode(msgkey="msg")
    @template.request_template(allow_cache=True)
    def get_info(self, auid):
        """获取单曲信息"""
        return self._API_INFO, {"params": {"sid": auid}}

    @utils.pick_data()
    @checker.check_bilicode(msgkey="msg")
    @template.request_template()
    def get_stream(self, auid, quality=3):
        """
        单曲取流

        quality = 0(128K) / 1(192K) / 2(320K) / 3(FLAC)
        """
        return self._API_STREAM, {
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
    @template.request_template(allow_cache=True)
    def get_tags(self, auid):
        """获取单曲标签"""
        return self._API_TAGS, {"params": {"sid": auid}}

    @utils.pick_data()
    @checker.check_bilicode(msgkey="msg")
    @template.request_template(allow_cache=True)
    def get_playmenu_content(self, amid, page=1, page_size=100):
        """获取歌单"""
        return self._API_PLAYMENU_CONTENT, {
            "params": {"sid": amid, "pn": page, "ps": page_size}
        }

    @utils.pick_data()
    @checker.check_bilicode(msgkey="msg")
    @template.request_template(allow_cache=True)
    def get_playmenu_info(self, amid):
        return self._API_PLAYMENU_INFO, {
            "params": {"sid": amid},
        }

import json

from .. import checker
from .. import utils
from .. import template


class MangaAPIs(template.APITemplate):
    _API_DETAIL = "https://manga.bilibili.com/twirp/comic.v1.Comic/ComicDetail"
    _API_EP_INFO = "https://manga.bilibili.com/twirp/comic.v1.Comic/GetEpisode"
    _API_IMG_INDEX = "https://manga.bilibili.com/twirp/comic.v1.Comic/GetImageIndex"
    _API_IMG_TOKEN = "https://manga.bilibili.com/twirp/comic.v1.Comic/ImageToken"
    PARAMS_UNI = "?device=pc&platform=web"

    @utils.pick_data()
    @checker.check_bilicode(msgkey="msg")
    @template.request_template("post")
    def get_detail(self, mcid: int):
        """获取一本漫画的详细信息"""
        return self._API_DETAIL + self.PARAMS_UNI, {"data": {"comic_id": mcid}}

    @utils.pick_data()
    @checker.check_bilicode(msgkey="msg")
    @template.request_template("post", allow_cache=True)
    def get_episode_info(self, epid: int):
        """获取一个漫画章节的信息"""
        return self._API_EP_INFO + self.PARAMS_UNI, {"data": {"id": epid}}

    @utils.pick_data()
    @checker.check_bilicode(msgkey="msg")
    @template.request_template("post")
    def get_image_index(self, epid: int):
        """获取一个漫画章节的图片目录，每张图片对应一个path用于获取图片本体"""
        return self._API_IMG_INDEX + self.PARAMS_UNI, {"data": {"ep_id": epid}}

    @utils.pick_data()
    @checker.check_bilicode(msgkey="msg")
    @template.request_template("post")
    def get_image_token(self, *paths: str):
        """用图片path获取图片token，
        将每张图片的url字段和token字段拼接可得到图片的最终url
        
        url+ "?token=" + token"""
        return self._API_IMG_TOKEN + self.PARAMS_UNI, {
            "data": {"urls": json.dumps(list(paths))}
        }

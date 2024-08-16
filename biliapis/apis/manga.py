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
        return MangaAPIs._API_DETAIL + MangaAPIs.PARAMS_UNI, {"data": {"comic_id": mcid}}

    @utils.pick_data()
    @checker.check_bilicode(msgkey="msg")
    @template.request_template("post")
    def get_episode_info(self, epid: int):
        """获取一个漫画章节的信息"""
        return MangaAPIs._API_EP_INFO + MangaAPIs.PARAMS_UNI, {"data": {"id": epid}}

    @utils.pick_data()
    @checker.check_bilicode(msgkey="msg")
    @template.request_template("post")
    def get_image_index(self, epid: int):
        """获取一个漫画章节的图片目录，每张图片对应一个path用于获取图片本体"""
        return MangaAPIs._API_IMG_INDEX + MangaAPIs.PARAMS_UNI, {"data": {"ep_id": epid}}

    @utils.pick_data()
    @checker.check_bilicode(msgkey="msg")
    @template.request_template("post")
    def get_image_token(self, *paths: str):
        """用图片path获取图片token，
        将每张图片的url字段和token字段拼接可得到图片的最终url
        
        url+ "?token=" + token"""
        return MangaAPIs._API_IMG_TOKEN + MangaAPIs.PARAMS_UNI, {
            "data": {"urls": json.dumps(list(paths))}
        }

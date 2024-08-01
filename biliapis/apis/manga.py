import json

from biliapis import checker
from biliapis import utils
from biliapis import template


class MangaAPIs(template.APITemplate):
    API_DETAIL = "https://manga.bilibili.com/twirp/comic.v1.Comic/ComicDetail"
    API_EP_INFO = "https://manga.bilibili.com/twirp/comic.v1.Comic/GetEpisode"
    API_IMG_INDEX = "https://manga.bilibili.com/twirp/comic.v1.Comic/GetImageIndex"
    API_IMG_TOKEN = "https://manga.bilibili.com/twirp/comic.v1.Comic/ImageToken"
    PARAMS_UNI = "?device=pc&platform=web"

    @utils.pick_data()
    @checker.check_bilicode(msgkey="msg")
    @template.request_template("post")
    def get_detail(self, mcid: int):
        return MangaAPIs.API_DETAIL + MangaAPIs.PARAMS_UNI, {"data": {"comic_id": mcid}}

    @utils.pick_data()
    @checker.check_bilicode(msgkey="msg")
    @template.request_template("post")
    def get_episode_info(self, epid: int):
        return MangaAPIs.API_EP_INFO + MangaAPIs.PARAMS_UNI, {"data": {"id": epid}}

    @utils.pick_data()
    @checker.check_bilicode(msgkey="msg")
    @template.request_template("post")
    def get_image_index(self, epid: int):
        return MangaAPIs.API_IMG_INDEX + MangaAPIs.PARAMS_UNI, {"data": {"ep_id": epid}}

    @utils.pick_data()
    @checker.check_bilicode(msgkey="msg")
    @template.request_template("post")
    def get_image_token(self, *paths: str):
        return MangaAPIs.API_IMG_TOKEN + MangaAPIs.PARAMS_UNI, {
            "data": {"urls": json.dumps(list(paths))}
        }

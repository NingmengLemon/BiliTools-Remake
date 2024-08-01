import json

from biliapis import checker
from biliapis import utils
from biliapis import template
from biliapis import error


class LoginAPIs(template.APITemplate):
    API_EXIT = "https://passport.bilibili.com/login/exit/v2"
    API_INFO = "https://api.bilibili.com/x/web-interface/nav"

    @utils.pick_data()
    @checker.check_bilicode()
    def exit_login(self):
        data = self.__exit_login_req()
        if "请先登录" in data:
            raise error.BiliError(-101, "未登录")
        return json.loads(data)

    @template.request_template("post", "str")
    def __exit_login_req(self):
        csrf = utils.get_csrf(self.session)
        if not csrf:
            raise error.BiliError(-101, "未登录")
        return LoginAPIs.API_EXIT, {"data": {"biliCSRF": csrf}}

    @utils.pick_data()
    @checker.check_bilicode()
    @template.request_template()
    def get_login_info(self):
        """获得当前登录用户的信息"""
        return LoginAPIs.API_INFO


class QRLoginAPIs(template.APITemplate):
    API_LOGIN_URL = "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
    API_POLL = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"

    @utils.pick_data()
    @checker.check_bilicode()
    @template.request_template()
    def get_login_qrcode_url(self):
        """
        用于获取登录二维码

        获取到的URL生成为二维码供用户扫描，
        qrcode_key传给poll进行扫描状态轮询
        """
        return QRLoginAPIs.API_LOGIN_URL, {}

    @utils.pick_data()
    @checker.check_bilicode()
    @template.request_template()
    def poll_login_qrcode(self, qrcode_key):
        """
        使用qrcode_key进行扫描状态轮询

        成功后会自动设置cookies并返回一个跨域登录URL
        """
        return QRLoginAPIs.API_POLL, {"params": {"qrcode_key": qrcode_key}}

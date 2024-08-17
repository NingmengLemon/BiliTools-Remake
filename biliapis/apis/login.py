# pylint: disable=E1101,E1120
# 不是哥们 pylint你疑似有点不太聪明
# 好的我承认其实是我装饰器用多了导致的
import json
import time
from http import cookiejar
import binascii
import logging

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from lxml import etree

from .. import checker
from .. import utils
from .. import template
from .. import error

# 关于刷新 Cookies 的相关内容，参见
# https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/login/cookie_refresh.md
_KEY_CORRESP = RSA.importKey(
    """\
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDLgd2OAkcGVtoE3ThUREbio0Eg
Uc/prcajMKXvkCKFCWhJYJcLkcM2DKKcSeFpD/j6Boy538YXnR6VhcuUJOhH2x71
nzPjfdTcqMz7djHum0qSZA0AyCBDABUqCrfNgCiJ00Ra7GmRj+YCK1NJEuewlb40
JNrRuoEUXpabUzGB8QIDAQAB
-----END PUBLIC KEY-----"""
)
_CIPHER_CORRESP = PKCS1_OAEP.new(_KEY_CORRESP, SHA256)


class LoginAPIs(template.APITemplate):
    _API_EXIT = "https://passport.bilibili.com/login/exit/v2"
    _API_INFO = "https://api.bilibili.com/x/web-interface/nav"
    _API_CHECK_COOKIES_REFRESH = (
        "https://passport.bilibili.com/x/passport-login/web/cookie/info"
    )
    _API_REFRESH_CSRF = "https://www.bilibili.com/correspond/1/"
    _API_REFRESH_COOKEIS = (
        "https://passport.bilibili.com/x/passport-login/web/cookie/refresh"
    )
    _API_REFRESH_CONFIRM = (
        "https://passport.bilibili.com/x/passport-login/web/confirm/refresh"
    )

    @utils.pick_data()
    @checker.check_bilicode()
    def exit_login(self):
        data = self.__exit_login_req()
        if "请先登录" in data:
            raise error.BiliError(-101, "未登录")
        data = json.loads(data)
        if data.get("code") == 0:
            self._extra_data["bili_refresh_token"] = None
        return data

    @template.request_template("post", "str")
    @template.withcsrf
    def __exit_login_req(self, csrf):
        return LoginAPIs._API_EXIT, {"data": {"biliCSRF": csrf}}

    @utils.pick_data()
    @checker.check_bilicode()
    @template.request_template()
    def get_login_info(self):
        """获得当前登录用户的信息"""
        return LoginAPIs._API_INFO

    @utils.pick_data()
    @checker.check_bilicode()
    @template.request_template()
    @template.withcsrf
    def check_if_cookies_refresh_required(self, csrf=None):
        return LoginAPIs._API_CHECK_COOKIES_REFRESH, {"params": {"csrf": csrf}}

    @staticmethod
    def get_correspond_path(ts: int):
        """ts: 毫秒级时间戳"""
        encrypted = _CIPHER_CORRESP.encrypt(f"refresh_{ts}".encode())
        return binascii.b2a_hex(encrypted).decode()

    def get_refresh_csrf(self, correspond_path):
        html = etree.fromstring(
            self.__get_refresh_csrf_req(correspond_path), etree.HTMLParser()
        )
        return html.xpath("//div[id='1-name']/text()")

    @template.request_template(handle="str")
    def __get_refresh_csrf_req(self, corresp: str):
        return LoginAPIs._API_REFRESH_CSRF + corresp

    @utils.pick_data()
    @checker.check_bilicode()
    @template.request_template("post")
    @template.withcsrf
    def refresh_cookies(self, refresh_token, refresh_csrf, csrf=None):
        return LoginAPIs._API_REFRESH_COOKEIS, {
            "params": {
                "refresh_token": refresh_token,
                "source": "main_web",
                "refresh_csrf": refresh_csrf,
                "csrf": csrf,
            }
        }

    @utils.discard_return
    @checker.check_bilicode()
    @template.request_template("post")
    @template.withcsrf
    def confirm_refresh_cookies(self, old_refresh_token, csrf=None):
        return LoginAPIs._API_REFRESH_CONFIRM, {
            "params": {"csrf": csrf, "refresh_token": old_refresh_token}
        }


class QRLoginAPIs(template.APITemplate):
    _API_LOGIN_URL = (
        "https://passport.bilibili.com/x/passport-login/web/qrcode/generate"
    )
    _API_POLL = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"

    @utils.pick_data()
    @checker.check_bilicode()
    @template.request_template()
    def get_login_qrcode_url(self):
        """
        用于获取登录二维码

        获取到的URL生成为二维码供用户扫描，
        qrcode_key传给poll进行扫描状态轮询
        """
        return QRLoginAPIs._API_LOGIN_URL, {}

    def poll_login_qrcode(self, qrcode_key):
        data = self.__poll_login_qrcode_req(qrcode_key)
        if data.get("code") == 0:
            self._extra_data["bili_refresh_token"] = data.get("refresh_token")
            logging.debug(
                "refresh token write to extra data, %s",
                data.get("refresh_token"),
            )
        return data

    @utils.pick_data()
    @checker.check_bilicode()
    @template.request_template()
    def __poll_login_qrcode_req(self, qrcode_key):
        """
        使用qrcode_key进行扫描状态轮询

        成功后会自动设置cookies并返回一个跨域登录URL和refresh_token
        """
        return QRLoginAPIs._API_POLL, {"params": {"qrcode_key": qrcode_key}}

    @staticmethod
    def cookiejar_from_crossdomain_url(url: str):
        """URL 来自轮询登录成功后返回的数据"""
        tmpjar = cookiejar.MozillaCookieJar()
        data = url.split("?")[-1].split("&")[:-1]
        for domain in (".bilibili.com", ".bigfun.cn", ".bigfunapp.cn", ".biligame.com"):
            for item in data:
                i = item.split("=", 1)
                # fmt: off
                tmpjar.set_cookie(
                    cookiejar.Cookie(
                        0, i[0], i[1], None, False,
                        domain, True, domain.startswith('.'),
                        '/', False, False,
                        int(time.time()) + (6 * 30 * 24 * 60 * 60),
                        False, None, None, {}
                        )
                    )
                # fmt: on
        return tmpjar

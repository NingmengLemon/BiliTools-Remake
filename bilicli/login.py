import logging
import time

import qrcode

from biliapis import APIContainer, BiliError
from bilicli.printers import print_login_info


def get_login_info_noexc(apis: APIContainer):
    try:
        return apis.login.get_login_info()
    except BiliError:
        return None


def logout_process(apis: APIContainer):
    try:
        apis.login.exit_login()
        print("已成功登出。")
    except BiliError as e:
        if e.code == -101:
            print("登出不成功，因为根本没有登录")
        else:
            raise


def login_process(apis: APIContainer):
    if _ := get_login_info_noexc(apis):
        print("已经登录过了！以下是用户信息：")
        print_login_info(_)
        return

    try:
        _ = apis.qrlogin.get_login_qrcode_url()
        loginurl = _["url"]
        oauthkey = _["qrcode_key"]
    except Exception as e:
        logging.error("Failed to get login URL: %s", e)
        return

    qr = qrcode.main.QRCode()
    qr.add_data(loginurl)
    qr.make(fit=True)
    qr.print_ascii(invert=True)

    print("Scan QRCode to login...")

    while True:
        try:
            _ = apis.qrlogin.poll_login_qrcode(oauthkey)
            status = _["code"]
            url = _["url"]
            match status:
                case 0:
                    print("登录成功！")
                    logging.debug("crossdomain url: %s", url)
                    return
                case 86038:
                    print("二维码超时。按 Enter 重试，或输入任意内容再按 Enter 退出")
                    return None if input() else login_process(apis=apis)
                case 86090:
                    print("\r已扫描二维码，请在手机上确认登录...", end="")
                case 86101:
                    print("\r等待扫描二维码...", end="")
            time.sleep(2)
        except Exception as e:
            logging.error("Error during login process: %s", e)
            break
    return

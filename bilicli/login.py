import logging
import time

import qrcode

from biliapis import APIContainer, BiliError
from .printers import print_login_info


def get_login_info_noexc(apis: APIContainer):
    try:
        return apis.login.get_login_info()
    except BiliError:
        return None


def logout_process(apis: APIContainer):
    try:
        apis.login.exit_login()
        print("Logged out successfully.")
    except BiliError as e:
        if e.code == -101:
            print("Could not logout: not logged in at all!")
        else:
            raise


def login_process(apis: APIContainer):
    if _ := get_login_info_noexc(apis):
        print("Already logged in. User info below:")
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
                    print("\nLogged in successfully!")
                    logging.debug("crossdomain url: %s", url)
                    return
                case 86038:
                    print(
                        "\nQRCode timed out. Simply press enter to try again, or input something to abort:"
                    )
                    return None if input() else login_process(apis=apis)
                case 86090:
                    print("\rScanned, confirm on your APP", end="")
                case 86101:
                    print("\rWaiting for scanning...", end="")
            time.sleep(2)
        except Exception as e:
            logging.error("Error during login process: %s", e)
            break
    return


def refresh_cookies_flow(apis: APIContainer, refresh_token=None):
    """会在extra_data里塞一个refresh_token

    ~~但是还没有测试过~~"""
    print("Attemping to refresh cookies...")
    logging.info("Attempting to refresh cookies...")
    if not refresh_token:
        refresh_token = apis.extra_data.get("bili_refresh_token")
    if not refresh_token:
        logging.warning("no refresh token found")
        return
    # 检查是否需要刷新
    try:
        data = apis.login.check_if_cookies_refresh_required()
    except BiliError as e:
        if e.code == -101:
            logging.warning("not logged in")
            return
        raise
    if not data["refresh"]:
        logging.info("no need to refresh cookies")
        print("no need to refresh cookies")
        return
    logging.info("start to refresh cookies...")
    ts = data["timestamp"]
    # 需要刷新，开始
    corresp = apis.login.get_correspond_path(ts)
    refresh_csrf = apis.login.get_refresh_csrf(corresp)
    old_refresh_token = refresh_token
    refresh_token = apis.login.refresh_cookies(
        refresh_csrf=refresh_csrf, refresh_token=refresh_token
    ).get("refresh_token")
    # 刷新完成，存储，确认
    apis.extra_data["bili_refresh_token"] = refresh_token
    apis.login.confirm_refresh_cookies(old_refresh_token=old_refresh_token)
    logging.info("refresh cookies completed")
    print("refresh complete")
    return refresh_token

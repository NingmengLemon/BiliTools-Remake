import logging
import os
import time

import pytest
import qrcode

from initapis import apis, dump_data, SAVEDIR
from biliapis import BiliError  # pylint: disable=E0611


def test_exit_with_no_login():
    with pytest.raises(BiliError):
        apis.login.exit_login()


def test_get_qrlogin_flow():
    data = apis.qrlogin.get_login_qrcode_url()
    assert isinstance(data, dict)
    dump_data("login_qrcode.json", data)
    url = data.get("url")
    key = data.get("qrcode_key")
    assert url is not None and key is not None
    with open(os.path.join(SAVEDIR, "login_qrcode_img.png"), "wb+") as fp:
        img = qrcode.make(url)
        img.save(fp)
    print("scan the code.")
    while True:
        status = apis.qrlogin.poll_login_qrcode(key)
        print(status["message"])
        code = status["code"]
        dump_data(f"login_qrcode_poll_code{code}.json", status)
        if code in (0, 86038):
            break
        time.sleep(2)
    if code == 0:
        info = apis.login.get_login_info()
        dump_data("login_user_info.json", info)
        exit_data = apis.login.exit_login()
        dump_data("login_logout.json", exit_data)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main()

import logging
import sys
import os
import json
import time

import pytest
from requests import Session
import qrcode

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from biliapis.error import BiliError
from biliapis.apis.login import LoginAPIs, QRLoginAPIs  # pylint: disable=C
from biliapis.wbi import CachedWbiManager  # pylint: disable=C

SAVEDIR = "./samples/"
if not os.path.exists(SAVEDIR):
    os.mkdir(SAVEDIR)

session = Session()
login_apis = LoginAPIs(session, CachedWbiManager(session))
qrlogin_apis = QRLoginAPIs(session, CachedWbiManager(session))


def test_exit_with_no_login():
    with pytest.raises(BiliError):
        login_apis.exit_login()


def test_get_qrlogin_flow():
    data = qrlogin_apis.get_login_qrcode_url()
    assert isinstance(data, dict)
    with open(os.path.join(SAVEDIR, "login_qrcode.json"), "w+", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    url = data.get("url")
    key = data.get("qrcode_key")
    assert url is not None and key is not None
    with open("./samples/login_qrcode_img.png", "wb+") as fp:
        img = qrcode.make(url)
        img.save(fp)
    print("scan the code.")
    while True:
        status = qrlogin_apis.poll_login_qrcode(key)
        print(status["message"])
        with open(os.path.join(SAVEDIR, "login_qrcode_poll.json"), "w+", encoding="utf-8") as f:
            json.dump(status, f, indent=4, ensure_ascii=False)
        if status["code"] in (0, 86038):
            break
        time.sleep(2)
    if status["code"] == 0:
        info = login_apis.get_login_info()
        with open(os.path.join(SAVEDIR, "login_user_info.json"), "w+", encoding="utf-8") as f:
            json.dump(info, f, indent=4, ensure_ascii=False)
        exit_data = login_apis.exit_login()
        with open(os.path.join(SAVEDIR, "login_logout.json"), "w+", encoding="utf-8") as f:
            json.dump(exit_data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main()

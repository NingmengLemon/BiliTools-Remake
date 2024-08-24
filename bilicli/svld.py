import base64
import pickle
import json
import logging
import hashlib
import os
import hmac
import functools
import platform
import uuid

import requests

from biliapis import APIContainer, new_apis


def get_fingerprint():
    return hashlib.sha256(
        f"""
{platform.machine()}
{platform.processor()}
{platform.architecture()}
{platform.system()}
{uuid.getnode()}
""".encode()
        + "114514".encode()
    ).digest()


KEY = get_fingerprint()


def save_data(apis: APIContainer, path: str):
    data = apis.extra_data.copy()
    session_pickle = pickle.dumps(apis.session)
    data["__session"] = base64.b64encode(
        hmac.new(KEY, session_pickle, hashlib.sha256).digest() + session_pickle
    ).decode("utf-8")
    with open(path, "w+", encoding="utf-8") as fp:
        json.dump(data, fp)
        logging.info("data saved: %s", path)


def _just_return_apis(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs) -> APIContainer:
        if isinstance((_ := func(*args, **kwargs)), tuple) and len(_) == 2:
            session, extra = _
            if isinstance(session, requests.Session):
                logging.info("session loaded")
                return new_apis(session=session, extra_data=extra)
        return new_apis()

    return wrapped


@_just_return_apis
def load_data(data_path: str) -> APIContainer:
    if not os.path.isfile(data_path):
        logging.info("data file not found, create new one")
        return
    try:
        with open(data_path, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        logging.info("data file found: %s, try loading...", data_path)
        logging.debug(
            "data content: %s", json.dumps(data, indent=4, ensure_ascii=False)
        )
    except Exception as e:
        logging.warning("unable to load data: %s", e, exc_info=True)
        return
    # check
    if not isinstance(data, dict):
        logging.error("not correct data structure")
        return
    session_b64 = data.pop("__session", None)
    if not isinstance(session_b64, str):
        logging.warning("session data not found")
        return
    session = base64.b64decode(session_b64)
    session_check = session[:32]
    session_pickle = session[32:]
    if hmac.compare_digest(
        session_check,
        hmac.new(KEY, session_pickle, hashlib.sha256).digest(),
    ):
        try:
            return pickle.loads(session_pickle), data
        except Exception as e:
            logging.error("error when deserializing session: %s", e)
            return
    logging.error("session validation failed")
    return

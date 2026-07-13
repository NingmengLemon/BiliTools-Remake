import base64
import hashlib
import json
import logging
import os
import pickle

import requests

from ..biliapis import APIContainer, new_apis
from .state import CredentialState, credential_state_from_data


def save_data(apis: APIContainer, path: str):
    data = apis.extra_data.copy()
    data["__credential"] = CredentialState.from_session(apis.session).to_json()
    session_pickle = pickle.dumps(apis.session)
    data["__session"] = base64.b64encode(
        hashlib.sha256(session_pickle).digest() + session_pickle
    ).decode("utf-8")
    with open(path, "w+", encoding="utf-8") as fp:
        json.dump(data, fp)
        logging.info("data saved: %s", path)


def _load_result_to_apis(result) -> APIContainer:
    if isinstance(result, tuple) and len(result) == 2:
        session, extra = result
        if isinstance(session, requests.Session):
            logging.info("session loaded")
            return new_apis(session=session, extra_data=extra)
        if isinstance(session, CredentialState):
            logging.info("credential loaded")
            return new_apis(
                session=session.apply_to_session(requests.Session()),
                extra_data=extra,
            )
    return new_apis()


def load_data(data_path: str) -> APIContainer:
    if not os.path.isfile(data_path):
        logging.info("data file not found, create new one")
        return new_apis()
    try:
        with open(data_path, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        logging.info("data file found: %s, try loading...", data_path)
        logging.debug(
            "data content: %s", json.dumps(data, indent=4, ensure_ascii=False)
        )
    except Exception as e:
        logging.warning("unable to load data: %s", e, exc_info=True)
        return new_apis()
    # check
    if not isinstance(data, dict):
        logging.error("not correct data structure")
        return new_apis()
    if credential_state := credential_state_from_data(data):
        data.pop("__credential", None)
        logging.info("credential state found")
        return _load_result_to_apis((credential_state, data))
    session_b64 = data.pop("__session", None)
    if not isinstance(session_b64, str):
        logging.warning("session data not found")
        return new_apis()
    session = base64.b64decode(session_b64)
    session_check = session[:32]
    session_pickle = session[32:]
    if hashlib.sha256(session_pickle).digest() == session_check:
        try:
            return _load_result_to_apis((pickle.loads(session_pickle), data))
        except Exception as e:
            logging.error("error when deserializing session: %s", e)
            return new_apis()
    logging.error("session validation failed")
    return new_apis()

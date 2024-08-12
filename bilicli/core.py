import argparse
import logging
import pickle
import os
from typing import Optional
import atexit

import requests

from biliapis.constants import VERSION as API_VERSION
from biliapis import new_apis, APIContainer
from bilicore.parser import extract_ids
from bilicore.core import SingleVideoThread
from bilicli.login import login_process, logout_process

VERSION = "1.0.0-a"

DEFAULT_SESSION_PATH = "./bilisession.pkl"
session_path: Optional[str] = None

session: Optional[requests.Session] = None


def load_session(path: Optional[str] = None):
    global session
    if path is None:
        path = session_path if session_path else DEFAULT_SESSION_PATH
    if os.path.isfile(path):
        try:
            with open(path, "rb") as fp:
                session = pickle.load(fp)
        except Exception:
            session = None
    else:
        session = None

    apis = new_apis(session=session)
    session = apis.session
    logging.info("session loaded: %s", path)
    return apis


@atexit.register
def save_session(path: Optional[str] = None):
    if path is None:
        path = session_path if session_path else DEFAULT_SESSION_PATH
    with open(path, "wb+") as fp:
        pickle.dump(session, fp)
        logging.info("session saved: %s", path)


def main_process(args: argparse.Namespace):
    if args.debug:
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level=logging.DEBUG,
        )
        print("-- Debug Enabled --")
        print("args:", vars(args))

    if args.version:
        print(f"API Core v{API_VERSION}")
        print(f"CLI Core v{VERSION}")

    if _ := args.session:
        apis = load_session(_)
    else:
        apis = load_session()

    if args.login:
        login_process(apis)
        return

    if args.logout:
        logout_process(apis)
        return

    source = args.input
    savedir = args.output
    if source is None:
        print("give an input to do actual things!")
        return

    if _ := extract_ids(source=source, session=session):
        idc, idn = _
    else:
        print("unknown source...")
        return

    match idn:
        case "bvid" | "avid":
            # common video
            common_video_process(apis=apis, savedir=savedir, **{idn: idc}, **vars(args))
        case "mdid" | "ssid" | "epid":
            # media
            pass
        case "auid":
            # audio
            pass
        case "amid":
            # audio playmenu
            pass
        case "mcid":
            # manga
            pass
        case _:
            # not supported
            print(f"source type {idn}={idc} not supported yet :(")


def common_video_process(apis: APIContainer, *, avid=None, bvid=None, **options):
    VALID_THREAD_OPTIONS = (
        "audio_only",
        "video_quality",
        "audio_quality",
        "video_codec",
        "subtitle_lang",
        "subtitle_format",
    )
    thread_opts = {k: v for k, v in options.items() if k in VALID_THREAD_OPTIONS}
    video_data = apis.video.get_video_detail(avid=avid, bvid=bvid)
    if _ := options.get("index"):
        pages = map(lambda x: int(x.strip()), _.split(","))
    else:
        pages = None
    threads: list[SingleVideoThread] = []
    for page in (
        video_data["pages"]
        if pages is None
        else [p for i, p in enumerate(video_data["pages"]) if i in pages]
    ):
        threads.append(
            SingleVideoThread(apis, cid=page["cid"], bvid=video_data["bvid"])
            # FIXME
        )


def media_process(**options):
    pass

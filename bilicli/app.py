import argparse
import logging
import pickle
import os
import atexit
import functools
from typing import Optional

from biliapis import new_apis, APIContainer
from biliapis.utils import remove_none
from bilicore.parser import extract_ids
from bilicli import printers, login
from bilicli.core import CliCore


class App(CliCore):
    DEFAULT_SESSION_PATH = "./bilisession.pkl"
    VERSION = "1.0.0-alpha"

    def __init__(self, args: argparse.Namespace) -> None:
        self._args = args

        if _ := args.session:
            self._session_path = _
        else:
            self._session_path = App.DEFAULT_SESSION_PATH

        super().__init__(self._load_session(self._session_path))
        atexit.register(
            functools.partial(
                self._save_session, apis=self._apis, path=self._session_path
            )
        )

        if args.version:
            print("BiliTools - Remake")
            print(f"API v{self._apis.VERSION}")
            print(f"CLI v{self.VERSION}")

    @staticmethod
    def _load_session(path: str):
        if os.path.isfile(path):
            try:
                with open(path, "rb") as fp:
                    session = pickle.load(fp)
            except Exception:
                session = None
        else:
            session = None

        apis = new_apis(session=session)
        logging.info("session loaded: %s", path)
        return apis

    @staticmethod
    def _save_session(apis: APIContainer, path: str):
        with open(path, "wb+") as fp:
            pickle.dump(apis.session, fp)
            logging.info("session saved: %s", path)

    def run(self):
        self._main_process(self._args)

    def _main_process(self, args: argparse.Namespace):  # , args: argparse.Namespace):
        apis = self._apis

        if args.login:
            login.login_process(apis)
            return

        if args.logout:
            login.logout_process(apis)
            return

        if _ := login.get_login_info_noexc(apis):
            print("已登录。")
            printers.print_login_info(_)
        else:
            print("未登录。部分资源将无法取得！")

        source: Optional[str] = args.input
        savedir: Optional[str] = args.output
        if source is None:
            print("give an input to do actual things!")
            return

        if _ := extract_ids(source=source, session=apis.session):
            idc, idn = _
        else:
            print("unknown source...")
            return

        if args.dry_run:
            savedir = None

        if savedir is None:
            print("- dry run -")

        match idn:
            case "bvid" | "avid":
                # common video
                self._common_video_process(savedir, **{idn: idc}, **remove_none(vars(args)))  # type: ignore[misc]
            case "mdid" | "ssid" | "epid":
                # media
                self._media_process(savedir, **{idn: idc}, **remove_none(vars(args)))  # type: ignore[misc]
            case "auid":
                # audio
                pass
            case "amid":
                # audio playmenu
                pass
            case "mcid":
                # manga
                self._manga_process(savedir, mcid=idc, **remove_none(vars(args)))
            case _:
                # not supported
                print(f"source type {idn}={idc} not supported yet :(")

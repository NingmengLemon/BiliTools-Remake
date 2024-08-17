import argparse
import logging
import pickle
import os
import atexit
from typing import Optional
import json

from biliapis import new_apis, APIContainer
from biliapis.utils import remove_none
from bilicore.parser import extract_ids
from . import printers, login
from .core import CliCore


class App(CliCore):
    DEFAULT_DATADIR_PATH = os.path.join(
        os.environ.get("USERPROFILE", "./data/"), ".bilitools"
    )
    DEFAULT_SESSION_FILENAME = "bilisession.pkl"
    DEFAULT_DATA_FILENAME = "bilidata.json"
    VERSION = "1.0.0-alpha"

    def __init__(self, args: argparse.Namespace) -> None:
        self._args = args

        if not os.path.isdir((_ := self.DEFAULT_DATADIR_PATH)):
            os.mkdir(_)

        if _ := args.session_filepath:
            self._session_path = _
        else:
            self._session_path = os.path.join(
                self.DEFAULT_DATADIR_PATH, self.DEFAULT_SESSION_FILENAME
            )

        if _ := args.data_filepath:
            self._data_path = _
        else:
            self._data_path = os.path.join(
                self.DEFAULT_DATADIR_PATH, self.DEFAULT_DATA_FILENAME
            )

        super().__init__(self._load_apis(self._session_path, self._data_path))
        atexit.register(self._save_all)

        if args.version:
            print("BiliTools - Remake")
            print(f"API v{self._apis.VERSION}")
            print(f"CLI v{self.VERSION}")

    def _load_apis(self, sess_path: str, data_path: str):
        return new_apis(
            session=self._load_session(sess_path), extra_data=self._load_data(data_path)
        )

    def _save_all(self):
        self._save_data(self._apis, self._data_path)
        self._save_session(self._apis, self._session_path)

    @staticmethod
    def _load_session(session_path: str):
        if not os.path.isfile(session_path):
            return None
        try:
            with open(session_path, "rb") as fp:
                session = pickle.load(fp)
            logging.info("session loaded: %s", session_path)
            return session
        except Exception:
            return None

    @staticmethod
    def _load_data(data_path: str):
        if not os.path.isfile(data_path):
            return None
        try:
            with open(data_path, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            logging.info("data loaded: %s", data_path)
            logging.debug("data content: %s", data)
            return data
        except Exception as e:
            logging.warning("unable to load data: %s", e, exc_info=True)
            return None

    @staticmethod
    def _save_session(apis: APIContainer, path: str):
        with open(path, "wb+") as fp:
            pickle.dump(apis.session, fp)
            logging.info("session saved: %s", path)

    @staticmethod
    def _save_data(apis: APIContainer, path: str):
        with open(path, "w+", encoding="utf-8") as fp:
            json.dump(apis.extra_data, fp)
            logging.info("data saved: %s", path)

    def run(self):
        self._main_process(self._args)

    def _main_process(self, args: argparse.Namespace):
        apis = self._apis

        if args.login:
            login.login_process(apis)
            return

        if args.logout:
            login.logout_process(apis)
            return

        if _ := login.get_login_info_noexc(apis):
            print("Already logged in.")
            printers.print_login_info(_)
            if not args.no_cookies_refresh:
                login.refresh_cookies_flow(self._apis)
        else:
            print("Not logged in. Some resources will be unavailable.\n")

        source: Optional[str] = args.input
        savedir: Optional[str] = args.output
        if source is None:
            print("give an input to do actual things!")
            return

        if _ := extract_ids(source=source, session=apis.session):
            idcontent, idname = _
        else:
            print("unknown source...")
            return

        if args.dry_run:
            savedir = None

        if savedir is None:
            print("- dry run -")

        options = remove_none(vars(args))
        for i, f in self._idname_to_procmethod_map:
            if idname in i:
                f(savedir, **{idname: idcontent}, **options)
                return

import argparse
import logging
import pickle
import os
import atexit
from typing import Optional
import json
import base64
import hashlib

from biliapis import new_apis, APIContainer, init_cache
from biliapis.utils import remove_none
from bilicore.parser import extract_ids
from . import printers, login
from .core import CliCore


class App(CliCore):
    DEFAULT_DATADIR_PATH = os.path.join(
        os.path.expanduser("~"), ".bilitools"
    )
    DEFAULT_DATA_FILENAME = "bilidata.json"
    DEFAULT_CACHE_FILENAME = "bilicache.db"
    VERSION = "1.0.0-alpha"

    def __init__(self, args: argparse.Namespace) -> None:
        self._args = args

        if not os.path.isdir((_ := self.DEFAULT_DATADIR_PATH)):
            os.mkdir(_)

        if _ := args.data_filepath:
            self._data_path = _
        else:
            self._data_path = os.path.join(
                self.DEFAULT_DATADIR_PATH, self.DEFAULT_DATA_FILENAME
            )

        super().__init__(self._load_apis(self._data_path))
        atexit.register(self._save_all)

        if args.version:
            print("BiliTools - Remake")
            print(f"API v{self._apis.VERSION}")
            print(f"CLI v{self.VERSION}")

        if not args.no_cache:
            init_cache(
                os.path.join(self.DEFAULT_DATADIR_PATH, self.DEFAULT_CACHE_FILENAME),
                args.cache_expire,
            )

    def _load_apis(self, data_path: str):
        data: Optional[dict] = self._load_data(data_path)
        if not data:
            return new_apis()
        session: Optional[dict] = data.pop("__session", None)
        if not session:
            logging.warning("session data not found, create new one")
            return new_apis()
        session_b64 = session["data"]
        session_pickle = base64.b64decode(session_b64)
        if (_ := hashlib.sha256(session_pickle).hexdigest()) != session["check"]:
            logging.error("session validation failed: %s != %s", _, session["check"])
            return new_apis()
        session_obj = pickle.loads(session_pickle)
        logging.info("session loaded.")
        return new_apis(session=session_obj, extra_data=data)

    def _save_all(self):
        self._save_data(self._apis, self._data_path)

    @staticmethod
    def _load_data(data_path: str):
        if not os.path.isfile(data_path):
            logging.info("data file not found, create new one")
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
    def _save_data(apis: APIContainer, path: str):
        data = apis.extra_data.copy()
        session_pickle = pickle.dumps(apis.session)
        data["__session"] = {
            "data": base64.b64encode(session_pickle).decode(),
            "check": hashlib.sha256(session_pickle).hexdigest(),
        }
        with open(path, "w+", encoding="utf-8") as fp:
            json.dump(data, fp)
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

        if ids := extract_ids(source=source, session=apis.session):
            logging.debug("extract ids: %s", ids)
            idname = list(ids.keys())[0]
            idcontent = ids[idname]
        else:
            print("unknown source...")
            return

        if args.dry_run:
            savedir = None

        if savedir is None:
            print("- dry run -")

        options = remove_none(vars(args))
        for i, func, need_all_ids in self._idname_to_procmethod_map:
            if idname in i:
                if need_all_ids:
                    func(savedir, **{idname: idcontent}, **options, all_ids=ids)
                else:
                    func(savedir, **{idname: idcontent}, **options)
                return
        print(f"source type <{idname}> not supported yet")

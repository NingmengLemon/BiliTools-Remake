import argparse
import logging
import os
import atexit
from typing import Optional

from biliapis import APIContainer, init_cache
from biliapis.utils import remove_none
import bilicore
from bilicore.parser import extract_ids
from bilicore.utils import check_ffmpeg
from . import printers, login, utils, svld
from .core import CliCore


class App(CliCore):
    DEFAULT_DATADIR_PATH = os.path.join(os.path.expanduser("~"), ".bilitools")
    DEFAULT_DATA_FILENAME = "bilidata.json"
    DEFAULT_CACHE_FILENAME = "bilicache.db"
    VERSION = "1.0.0-beta"

    def __init__(self, args: argparse.Namespace) -> None:
        self._args = args

        if not os.path.isdir((_ := self.DEFAULT_DATADIR_PATH)):
            os.makedirs(_, exist_ok=True)

        if _ := args.data_filepath:
            self._data_filepath = _
        else:
            self._data_filepath = os.path.join(
                self.DEFAULT_DATADIR_PATH, self.DEFAULT_DATA_FILENAME
            )

        super().__init__(self._load_all(self._data_filepath))
        atexit.register(self._save_all)

        if args.version:
            print("\nBiliTools - Remake")
            print(f"API  v{self._apis.VERSION}")
            print(f"Core v{bilicore.VERSION}")
            print(f"CLI  v{self.VERSION}\n")

        if not args.no_cache:
            init_cache(
                os.path.join(self.DEFAULT_DATADIR_PATH, self.DEFAULT_CACHE_FILENAME),
                args.cache_expire,
            )

        if not check_ffmpeg():
            print("\nFFmpeg not found!!")
            print(
                "Program cannot function normally without FFmpeg, consider install it.\n"
            )
            utils.ask_confirm(args.yes)

    def _load_all(self, data_path: str) -> APIContainer:
        return svld.load_data(data_path)

    def _save_all(self):
        svld.save_data(self._apis, self._data_filepath)

    def run(self):
        self._main_process(self._args)

    def _main_process(self, args: argparse.Namespace):
        apis = self._apis

        if args.version:
            return

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
                print()
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

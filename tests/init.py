import sys
import os
import json
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from biliapis import new_apis  # pylint: disable=C0413,E0611

apis = new_apis()

SAVEDIR = "./samples/"
if not os.path.exists(SAVEDIR):
    os.mkdir(SAVEDIR)


def dump_data(filename: str, data: Any):
    with open(os.path.join(SAVEDIR, filename), "w+", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

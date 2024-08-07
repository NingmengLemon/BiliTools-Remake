from typing import Any, Literal
import json
import html

BCC_DICT_SAMPLE = {
    "font_size": 0.4,
    "font_color": "#FFFFFF",
    "background_alpha": 0.5,
    "background_color": "#9C27B0",
    "stroke": "none",
    "body": [
        {"from": 3.32, "to": 3.99, "location": 2, "content": "我\n"},
    ],
}


def sec2time(sec: float | int, fmt: Literal["srt", "vtt", "lrc"]) -> str:
    match fmt:
        case "srt":
            return "{:0>2d}:{:0>2d}:{:0>2d},{:0>3d}".format(*sec2timetuple(sec))
        case "lrc":
            h, m, s, ms = sec2timetuple(sec)
            return "{:0>2d}:{:0>2d}.{:0>2d}".format(h * 60 + m, s, ms // 10)
        case "vtt":
            return "{:0>2d}:{:0>2d}:{:0>2d}.{:0>3d}".format(*sec2timetuple(sec))


def sec2timetuple(sec: float) -> tuple[int, int, int, int]:
    h = int(sec // 3600)
    m = int(sec // 60 % 60)
    s = int(sec % 60)
    ms = int((sec * 1000) % 1000)
    return h, m, s, ms


def bcc2srt(data: dict[str, Any]) -> str:
    srt = [""]
    return NotImplemented


class BiliClosedCaption:
    def __init__(self, bccdata: dict | str | bytes | bytearray) -> None:
        if isinstance(bccdata, (str, bytes, bytearray)):
            self._data: dict[str, Any] = json.loads(bccdata)
        else:
            self._data = bccdata

    def __getattribute__(self, name: str) -> Any:
        return self._data.get(name)

    def json(self, **kwargs):
        return json.dumps(self._data, **kwargs)

    def srt(self):
        pass

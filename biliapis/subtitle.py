from typing import Any, Literal
import json
import html

# import zhconv

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

BCC_REQ_SAMPLE = [
    {
        "id": 1550024136175127808,
        "lan": "ai-zh",
        "lan_doc": "中文（自动生成）",
        "is_lock": False,
        "subtitle_url": "//aisubtitle.hdslb.com/bfs/ai_subtitle/prod/(filtered)",
        "type": 1,
        "id_str": "1550024136175127808",
        "ai_type": 0,
        "ai_status": 2,
    }
]


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
    srt: list[str] = [
        """%d
%s --> %s
%s"""
        % (
            i + 1,
            sec2time(block["from"], "srt"),
            sec2time(block["to"], "srt"),
            block["content"],
        )
        for i, block in enumerate(data["body"])
    ]
    return "\n\n".join(srt)


def bcc2vtt(data: dict[str, Any]) -> str:
    vtt: list[str] = [
        """%d
%s --> %s
%s"""
        % (
            i + 1,
            sec2time(block["from"], "vtt"),
            sec2time(block["to"], "vtt"),
            str(html.escape(block["content"]))
            .replace("\n", "\\n")
            .replace("\t", "\\t"),
        )
        for i, block in enumerate(data["body"])
    ]
    return "WEBVTT\n\n" + "\n\n".join(vtt)


def bcc2lrc(data: dict[str, Any]) -> str:
    lrc: list[str] = []
    for block in data["body"]:
        timetag_s = "[%s] " % (sec2time(block["from"], "lrc"))
        timetag_e = "[%s] " % (sec2time(block["to"], "lrc"))
        lrc += [timetag_s + line for line in block["content"].split("\n")]
        lrc.append(timetag_e)
    return "\n".join(lrc)


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

    @property
    def srt(self):
        return bcc2srt(self._data)

    @property
    def vtt(self):
        return bcc2vtt(self._data)

    @property
    def lrc(self):
        return bcc2lrc(self._data)

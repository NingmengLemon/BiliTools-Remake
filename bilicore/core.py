from typing import Literal, Optional, Any, Callable
import os
import threading
import functools
from concurrent.futures import ThreadPoolExecutor, as_completed

from biliapis.utils import remove_none
from biliapis import APIContainer, bilicodes
from biliapis import subtitle
from bilicore import (
    download_common,
    select_quality,
)
from bilicore.utils import filename_escape, merge_avfile, call_ffmpeg


class ProcessUtilsMixin:
    @staticmethod
    def _dstream(
        urls: list[str],
        file: str,
        hook: Callable[[Optional[int], Optional[int]], Any],
        apis: APIContainer,
    ):
        for i, u in enumerate(urls):
            try:
                download_common(
                    u,
                    file,
                    session=apis.session,
                    hook_func=hook,
                )
            except Exception:
                if i + 1 == len(urls):
                    raise
            else:
                return

    @staticmethod
    def _dfile(url, file, apis: APIContainer):
        data = apis.session.get(url, headers=apis.DEFAULT_HEADERS).content
        with open(file, "wb+") as fp:
            fp.write(data)


class SingleVideoProcess(threading.Thread, ProcessUtilsMixin):
    def __init__(
        self,
        apis: APIContainer,
        cid: int,
        *,
        avid: Optional[int] = None,
        bvid: Optional[str] = None,
        savedir: str,
        **options,
    ) -> None:
        super().__init__(daemon=True)
        if (avid is None) == (bvid is None):
            raise ValueError("need ONE between avid and bvid")
        self._cid = cid
        self._id = remove_none({"avid": avid, "bvid": bvid})
        self._apis = apis
        self._savedir = savedir
        self._audio_only = bool(options.get("audio_only", False))
        self._video_data: Optional[dict[str, Any]] = options.get("video_data")
        self._streams: Optional[dict[str, Any]] = options.get("stream_data")
        self._player_info: Optional[dict[str, Any]] = options.get("player_info")
        self._vq: str | int = options.get("video_quality", "max")
        self._vc: Literal["avc", "hevc"] = options.get("video_encoding", "avc")
        self._aq: str | int = options.get("audio_quality", "max")
        self._sv: Optional[str | Literal["all"]] = options.get("subtitle_lang")
        self._sf: Literal["vtt", "srt", "lrc"] = options.get("subtitle_format", "vtt")
        self._progress_text = "pending"
        self.exception: Optional[Exception] = None

    def run(self):
        try:
            self._progress_text = "starting"
            self._worker()
            self._progress_text = "done"
        except Exception as e:
            self.exception = e
            self._progress_text = "errored"

    def _worker(self):
        if self._video_data is None:
            self._video_data = self._apis.video.get_video_detail(**self._id)
        vdata = self._video_data
        cidlist = [p["cid"] for p in vdata["pages"]]
        if self._cid not in cidlist:
            raise ValueError("wrong cid")
        cid = self._cid
        pindex = cidlist.index(cid)
        bvid = vdata["bvid"]
        player_info = self._apis.video.get_player_info(cid=cid, bvid=bvid)
        if _sub := player_info.get("subtitle", {}).get("subtitles", []):
            subtitles = _sub
        else:
            subtitles = []
        streams = (
            self._apis.video.get_stream_dash(cid, bvid=bvid)
            if self._streams is None
            else self._streams
        )
        vstream, astream = select_quality(
            streams, aq=self._aq, vq=self._vq, enc=self._vc
        )
        title = vdata["title"]
        ptitle = vdata["pages"][pindex]["part"]
        vqid = vstream["id"]
        aqid = astream["id"]
        is_lossless = aqid == 30251
        vtmpfile = os.path.join(self._savedir, f"{bvid}_{cid}_{vqid}_videostream.m4v")
        atmpfile = os.path.join(
            self._savedir,
            f"{bvid}_{cid}_{aqid}_videostream" + (".flac" if is_lossless else ".m4a"),
        )
        finalfile = os.path.join(
            self._savedir,
            filename_escape(
                (
                    f"{title}"
                    + (f"_P{pindex+1}" if len(cidlist) > 1 else "")
                    + (f"_{ptitle}" if ptitle != title else "")
                    + (
                        f"_{bilicodes.stream_dash_audio_quality.get(aqid)}"
                        if self._audio_only
                        else f"_{bilicodes.stream_dash_video_quality.get(vqid)}"
                    )
                )
                + (
                    (".flac" if is_lossless else ".mp3")
                    if self._audio_only
                    # mp4 容器不支持 flac 音轨
                    else (".mkv" if is_lossless else ".mp4")
                )
            ),
        )
        if os.path.isfile(finalfile):
            self._progress_text = "skipped"
            return
        # 字幕
        subfile = os.path.join(self._savedir, finalfile + ".{lan}" + f".{self._sf}")
        if self._sv is not None:
            for sub in subtitles:
                if self._sv == "all" or self._sv.lower() == sub["lan"].lower():
                    self._dsubt(
                        "https:" + sub["subtitle_url"],
                        subfile.format(lan=sub["lan"]),
                        self._sf,
                    )
        vurls = [vstream["base_url"]] + vstream["backup_url"]
        aurls = [astream["base_url"]] + astream["backup_url"]
        # 我错了我再也不玩多线程了 😭
        ahook = functools.partial(self._progress_hook, name="audio")
        self._dstream(aurls, atmpfile, ahook, apis=self._apis)
        if self._audio_only:
            if is_lossless:
                os.rename(atmpfile, finalfile)
            else:
                call_ffmpeg(
                    "-i",
                    atmpfile,
                    "-b:a",
                    bilicodes.stream_dash_audio_quality.get(aqid).lower(),
                    finalfile,
                )
                os.remove(atmpfile)
            return
        vhook = functools.partial(self._progress_hook, name="video")
        self._dstream(vurls, vtmpfile, vhook, apis=self._apis)
        merge_avfile(atmpfile, vtmpfile, finalfile)
        os.remove(atmpfile)
        os.remove(vtmpfile)

    def _dsubt(self, url, file, fmt: Literal["vtt", "srt", "lrc"]):
        subt = self._apis.session.get(url, headers=self._apis.DEFAULT_HEADERS).json()
        with open(file, "w+", encoding="utf-8") as f:
            match fmt:
                case "lrc":
                    f.write(subtitle.bcc2lrc(subt))
                case "srt":
                    f.write(subtitle.bcc2srt(subt))
                case "vtt":
                    f.write(subtitle.bcc2vtt(subt))

    def _progress_hook(self, curr: Optional[int], total: Optional[int], name: str):
        self._progress_text = (
            f"{name}: --%"
            if curr is None or total is None
            else f"{name}: {curr/total*100:.2f}%"
        )

    def observe(self):
        return self._progress_text


class SingleAudioProcess(threading.Thread, ProcessUtilsMixin):
    def __init__(self, apis: APIContainer, auid, savedir, **options) -> None:
        super().__init__(daemon=True)
        self._apis = apis
        self._auid = auid
        self._savedir = savedir
        self._quality: Optional[Literal[0, 1, 2, 3]] = options.get("quality", 3)
        self._info: Optional[dict[str, Any]] = options.get("audio_data")
        self._progress_text = "pending"
        self._need_lrc = bool(options.get("need_lrc", False))
        self._need_cover = bool(options.get("need_cover", False))
        self.exception: Optional[Exception] = None

    def _worker(self):
        info = self._info if self._info else self._apis.audio.get_info(self._auid)
        auid = info["id"]
        stream = self._apis.audio.get_stream(auid=auid, quality=self._quality)
        is_lossless = stream["type"] == 3
        tmpfile = os.path.join(
            self._savedir,
            "au{sid}_{type}_{size}".format(**stream)
            + (".flac" if is_lossless else ".m4a"),
        )
        finalfile = os.path.join(
            self._savedir,
            filename_escape(
                "{title}".format(**info)
                + ("_" + bilicodes.stream_audio_quality.get(stream["type"], ""))
                + (".flac" if is_lossless else ".mp3")
            ),
        )
        if (lrc_url := info.get("lyric")) and self._need_lrc:
            self._dfile(lrc_url, finalfile + ".lrc", self._apis)
        if (cover := info.get("cover")) and self._need_cover:
            self._dfile(cover, finalfile + os.path.splitext(cover)[1], self._apis)
        if os.path.isfile(finalfile):
            self._progress_text = "skipped"
            return
        self._dstream(
            stream["cdns"],
            tmpfile,
            functools.partial(self._progress_hook, name="stream"),
            apis=self._apis,
        )
        if is_lossless:
            os.rename(tmpfile, finalfile)
        else:
            call_ffmpeg(
                "-i",
                tmpfile,
                "-b:a",
                bilicodes.stream_audio_quality.get(stream["type"], "320k")[:4].lower(),
                finalfile,
            )
            os.remove(tmpfile)

    def run(self):
        try:
            self._progress_text = "starting"
            self._worker()
            self._progress_text = "done"
        except Exception as e:
            self.exception = e
            self._progress_text = "errored"

    def _progress_hook(self, curr: Optional[int], total: Optional[int], name: str):
        self._progress_text = (
            f"{name}: --%"
            if curr is None or total is None
            else f"{name}: {curr/total*100:.2f}%"
        )

    def observe(self):
        return self._progress_text


class SingleMangaChapterProcess(threading.Thread, ProcessUtilsMixin):
    def __init__(self, apis: APIContainer, epid: int, savedir: str, **options) -> None:
        super().__init__(daemon=True)
        self._apis = apis
        self._epid = epid
        self._savedir = savedir
        self._ep_data: Optional[dict[str, Any]] = options.get("ep_data")
        self._create_childfolder = bool(options.get("create_childfolder", True))
        self._progress_text = "pending"
        self.exception: Optional[Exception] = None

    def _worker(self):
        epinfo = (
            self._ep_data
            if self._ep_data
            else self._apis.manga.get_episode_info(epid=self._epid)
        )
        if self._create_childfolder:
            self._savedir = os.path.join(
                self._savedir,
                filename_escape("{short_title}_{title}_{comic_title}".format(**epinfo)),
            )
            if not os.path.isdir(self._savedir):
                os.mkdir(self._savedir)
        index = self._apis.manga.get_image_index(self._epid)
        paths = [i["path"] for i in index["images"]]
        tokens = self._apis.manga.get_image_token(*paths)
        urls = [i["url"] + "?token=" + i["token"] for i in tokens]
        self._progress_text = f"0 / {len(urls)}"
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(
                    self._dfile,
                    url,
                    os.path.join(self._savedir, "%03d.jpg") % (i + 1),
                    self._apis,
                )
                for i, url in enumerate(urls)
            ]
            for i, future in enumerate(as_completed(futures)):
                try:
                    future.result()
                    self._progress_text = f"{i} / {len(urls)}"
                except Exception as e:
                    self.exception = e

    def run(self):
        try:
            self._progress_text = "starting"
            self._worker()
            self._progress_text = "done"
        except Exception as e:
            self.exception = e
            self._progress_text = "errored"

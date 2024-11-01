from typing import Literal, Optional, Any, Callable
import os
import threading
import functools
from concurrent.futures import ThreadPoolExecutor, as_completed

from biliapis.utils import remove_none
from biliapis import APIContainer, bilicodes
from biliapis import subtitle
from bilicore.downloader import download_common
from bilicore.parser import select_quality
from bilicore.utils import filename_escape, merge_avfile, convert_audio

# 写得最史的地方


class ThreadProgressMixin:
    def __init__(self) -> None:
        self.__curr = 0
        self.__total = 0
        self.__progress_text = ""
        self.__progress_name = ""
        self.__report_lock = threading.Lock()
        self.__exceptions: list[Exception] = []
        self._report_progress(0, 0, "pending")

    def _report_progress(
        self,
        curr: Optional[int] = None,
        total: Optional[int] = None,
        pgr_text: Optional[str] = None,
        pgr_name: Optional[str] = None,
    ):
        with self.__report_lock:
            if isinstance(curr, int):
                self.__curr = curr
            if isinstance(total, int):
                self.__total = total
            if isinstance(pgr_text, str):
                self.__progress_text = pgr_text
            if isinstance(pgr_name, str):
                self.__progress_name = pgr_name

    def _report_exception(self, exc: Exception):
        with self.__report_lock:
            self.__exceptions.append(exc)

    def observe(self):
        with self.__report_lock:
            return (
                self.__curr,
                self.__total,
                (
                    (f"{self.__progress_name} - " if self.__progress_name else "")
                    + f"{self.__progress_text}"
                ),
            )

    @property
    def exceptions(self):
        with self.__report_lock:
            return self.__exceptions.copy()

    def _progress_hook(
        self,
        curr: Optional[int] = None,
        total: Optional[int] = None,
        offset: int = 0,
    ):
        if curr:
            self._report_progress(curr=curr + offset)
        if total:
            self._report_progress(total=total + offset)

    def _run_wrapped(self, worker: Callable[[], Any]):
        # 这个写法有点傻逼的
        try:
            self._report_progress(pgr_text="starting")
            worker()
        except Exception as e:
            self._report_exception(e)
            self._report_progress(pgr_text="errored")


class ThreadUtilsMixin:
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


class SingleVideoThread(threading.Thread, ThreadUtilsMixin, ThreadProgressMixin):
    VALID_OPTIONS = (
        # 下载选项
        "audio_only",
        "video_quality",
        "audio_quality",
        "video_codec",
        "subtitle_lang",
        "subtitle_format",
        "need_cover",
        "no_metadata",
        # 预处理数据
        "stream_data",
        "video_data",
        "player_info",
        # 更正字段，仅影响输出文件的名称、进度条提示信息和写入的元数据
        "title",
        "pindex",
        "ptitle",
    )

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
        ThreadProgressMixin.__init__(self)
        if (avid is None) == (bvid is None):
            raise ValueError("need ONE between avid and bvid")
        self._cid = cid
        self._id = remove_none({"avid": avid, "bvid": bvid})
        self._apis = apis
        self._savedir = savedir

        options = {k: v for k, v in options.items() if k in self.VALID_OPTIONS}
        self._audio_only = bool(options.get("audio_only", False))
        self._vq: str | int = options.get("video_quality", "max")
        self._vc: Literal["avc", "hevc"] = options.get("video_codec", "avc")
        self._aq: str | int = options.get("audio_quality", "max")
        self._sv: Optional[str | Literal["all"]] = options.get("subtitle_lang")
        self._sf: Literal["vtt", "srt", "lrc"] = options.get("subtitle_format", "vtt")
        self._need_cover: bool = bool(options.get("need_cover", False))
        self._need_metadata: bool = not bool(options.get("no_metadata", False))

        self._video_data: Optional[dict[str, Any]] = options.get("video_data")
        self._streams: Optional[dict[str, Any]] = options.get("stream_data")
        self._player_info: Optional[dict[str, Any]] = options.get("player_info")

        self._correct_title: Optional[str] = options.get("title")
        self._correct_pindex: Optional[int] = options.get("pindex")
        self._correct_ptitle: Optional[str] = options.get("ptitle")

    def run(self):
        self._run_wrapped(self._worker)

    def _worker(self):
        self._report_progress(pgr_text="collecting data")
        if self._video_data is None:
            self._video_data = self._apis.video.get_video_detail(**self._id)
        vdata = self._video_data
        cidlist = [p["cid"] for p in vdata["pages"]]
        if self._cid not in cidlist:
            raise ValueError("wrong cid")
        cid = self._cid
        pindex = cidlist.index(cid)
        self._report_progress(
            pgr_name="{bvid} P{p}".format(
                bvid=vdata["bvid"],
                p=pindex + 1 if self._correct_pindex is None else self._correct_pindex,
            )
        )
        bvid = vdata["bvid"]
        player_info = self._player_info or self._apis.video.get_player_info(
            cid=cid, bvid=bvid
        )
        if _ := player_info.get("subtitle", {}).get("subtitles", []):
            subtitles = _
        else:
            subtitles = []
        streams = self._streams or self._apis.video.get_stream_dash(cid, bvid=bvid)
        vstream, astream = select_quality(
            streams, aq=self._aq, vq=self._vq, enc=self._vc
        )
        # 处理没有音轨的情况
        no_audio = astream is None
        if no_audio and self._audio_only:
            self._report_progress(pgr_text="terminated: no audio stream to download")
            return
        title = vdata["title"] if self._correct_title is None else self._correct_title
        ptitle = (
            vdata["pages"][pindex]["part"]
            if self._correct_ptitle is None
            else self._correct_ptitle
        )
        vqid = vstream["id"]
        aqid = -1 if no_audio else astream["id"]
        is_lossless = aqid == 30251
        # 生成文件名
        vtmpfile = os.path.join(self._savedir, f"{bvid}_{cid}_{vqid}_videostream.m4v")
        atmpfile = (
            ""
            if no_audio
            else os.path.join(
                self._savedir,
                f"{bvid}_{cid}_{aqid}_videostream"
                + (".flac" if is_lossless else ".m4a"),
            )
        )
        finalfile = os.path.join(
            self._savedir,
            filename_escape(
                (
                    f"{title}"
                    + (
                        (f"_P{pindex+1}" if len(cidlist) > 1 else "")
                        if self._correct_pindex is None
                        else f"_P{self._correct_pindex}"
                    )
                    + (f"_{ptitle}" if ptitle != title or self._correct_ptitle else "")
                    + (
                        f"_{bilicodes.stream_dash_audio_quality.get(aqid)}"
                        if self._audio_only
                        else f"_{bilicodes.stream_dash_video_quality.get(vqid)}"
                    )
                    # 孩子们，三目运算符并不好玩😡
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
            self._report_progress(pgr_text="skipped: file already exists")
            return
        # 封面
        coverfile: Optional[str] = None
        if self._need_cover:
            coverfile = finalfile + os.path.splitext(vdata["pic"])[1]
            self._dfile(vdata["pic"], coverfile, self._apis)
        # 字幕
        subfile = os.path.join(
            self._savedir, os.path.split(finalfile)[1] + ".{lan}" + f".{self._sf}"
        )
        if self._sv is not None:
            self._report_progress(pgr_text="fetching subtitle")
            for sub in subtitles:
                if self._sv == "all" or self._sv.lower() == sub["lan"].lower():
                    self._dsubt(
                        "https:" + sub["subtitle_url"],
                        subfile.format(lan=sub["lan"]),
                        self._sf,
                    )
        vurls = [vstream["base_url"]] + vstream["backup_url"]
        self._report_progress(pgr_text="audio stream")
        if not no_audio:
            aurls = [astream["base_url"]] + astream["backup_url"]
            self._dstream(aurls, atmpfile, self._progress_hook, apis=self._apis)
        # 仅音轨的分岔
        if self._audio_only:
            self._report_progress(pgr_text="converting")
            convert_audio(
                atmpfile,
                finalfile,
                quality=(
                    None
                    if is_lossless
                    else bilicodes.stream_dash_audio_quality.get(aqid, "192k").lower()
                ),
                metadata=(
                    self._generate_metadict(vdata, pindex)
                    if self._need_metadata
                    else None
                ),
                cover_image=(coverfile if self._need_cover else None),
            )
            os.remove(atmpfile)
            self._report_progress(pgr_text="done")
            return
        # 普通视频的分岔
        vhook = functools.partial(
            self._progress_hook,
            offset=(os.path.getsize(atmpfile) if os.path.isfile(atmpfile) else 0),
        )
        self._report_progress(pgr_text="video stream")
        self._dstream(vurls, vtmpfile, vhook, apis=self._apis)
        self._report_progress(pgr_text="merging")
        merge_avfile(
            (None if no_audio else atmpfile),
            vtmpfile,
            finalfile,
            metadata=(
                self._generate_metadict(vdata, pindex) if self._need_metadata else None
            ),
            cover_image=(coverfile if self._need_cover else None),
        )
        if not no_audio:
            os.remove(atmpfile)
        os.remove(vtmpfile)
        self._report_progress(pgr_text="done")

    def _generate_metadict(
        self,
        video_detail: dict[str, Any],
        real_pindex: int,
    ) -> dict[str, str]:
        title = self._correct_title or video_detail["title"]
        ptitle = self._correct_ptitle or video_detail["pages"][real_pindex]["part"]
        pindex = self._correct_pindex or (real_pindex + 1)
        ptitle = f"P{pindex}" + (f" - {ptitle}" if ptitle != title else "")
        metadata = {
            "title": title,
            "subtitle": ptitle,
            "comment": video_detail["bvid"],
        }
        if video_detail["copyright"] == 1:
            metadata["artist"] = video_detail["owner"]["name"]
        return metadata

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


class SingleAudioThread(threading.Thread, ThreadUtilsMixin, ThreadProgressMixin):
    VALID_OPTIONS = (
        "quality",
        "need_lyrics",
        "need_cover",
        "no_metadata"
        # 预处理数据
        "audio_data",
    )

    def __init__(self, apis: APIContainer, auid: int, savedir: str, **options) -> None:
        super().__init__(daemon=True)
        ThreadProgressMixin.__init__(self)
        self._apis = apis
        self._auid = auid
        self._savedir = savedir
        options = {k: v for k, v in options.items() if k in self.VALID_OPTIONS}
        self._quality: Optional[Literal[0, 1, 2, 3]] = options.get("quality", 3)
        self._need_lrc = bool(options.get("need_lyrics", False))
        self._need_cover = bool(options.get("need_cover", False))
        self._need_metadata = not bool(options.get("no_metadata", False))
        self._info: Optional[dict[str, Any]] = options.get("audio_data")

    def _worker(self):
        self._report_progress(pgr_text="collecting data")
        info = self._info if self._info else self._apis.audio.get_info(self._auid)
        auid = info["id"]
        self._report_progress(pgr_name=f"au{auid}")
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
            self._report_progress(pgr_text="lyrics")
            self._dfile(lrc_url, finalfile + ".lrc", self._apis)
        coverfile: Optional[str] = None
        if (cover := info.get("cover")) and self._need_cover:
            coverfile = finalfile + os.path.splitext(cover)[1]
            self._report_progress(pgr_text="cover")
            self._dfile(cover, coverfile, self._apis)
        if os.path.isfile(finalfile):
            self._report_progress(pgr_text="skipped")
            return

        self._report_progress(pgr_text="downloading")
        self._dstream(
            stream["cdns"],
            tmpfile,
            self._progress_hook,
            apis=self._apis,
        )
        self._report_progress(pgr_text="converting")
        convert_audio(
            tmpfile,
            finalfile,
            quality=(
                None
                if is_lossless
                else bilicodes.stream_audio_quality.get(stream["type"], "320k")[
                    :4
                ].lower()
            ),
            metadata=(self._generate_metadict(info) if self._need_metadata else None),
            cover_image=(coverfile if self._need_metadata else None),
        )
        os.remove(tmpfile)
        self._report_progress(pgr_text="done")

    def _generate_metadict(self, audio_info: dict[str, Any]) -> dict[str, str]:
        auid = audio_info["id"]
        meta_dict = {
            "title": audio_info["title"],
            "artist": audio_info["author"],
            "comment": f"au{auid}"
            + (" / " + audio_info["bvid"] if audio_info["bvid"] else ""),
        }
        return meta_dict

    def run(self):
        self._run_wrapped(self._worker)


class SingleMangaChapterThread(threading.Thread, ThreadUtilsMixin, ThreadProgressMixin):
    VALID_OPTIONS = (
        "create_childfolder",
        # 预处理数据
        "ep_data",
    )

    def __init__(self, apis: APIContainer, epid: int, savedir: str, **options) -> None:
        super().__init__(daemon=True)
        ThreadProgressMixin.__init__(self)
        self._apis = apis
        self._epid = epid
        self._savedir = savedir
        options = {k: v for k, v in options.items() if k in self.VALID_OPTIONS}
        self._create_childfolder = bool(options.get("create_childfolder", True))
        self._ep_data: Optional[dict[str, Any]] = options.get("ep_data")

    def _worker(self):
        self._report_progress(pgr_text="collecting data", pgr_name=f"ep{self._epid}")
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
        urls = [i["complete_url"] for i in tokens]
        self._report_progress(0, len(urls), pgr_text="downloading")
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
                    self._report_progress(i + 1, len(urls))
                except Exception as e:
                    self._report_exception(e)
        self._report_progress(pgr_text="done")

    def run(self):
        self._run_wrapped(self._worker)

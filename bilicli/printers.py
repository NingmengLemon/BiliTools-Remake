from typing import Any, Optional

from .utils import generate_media_ptitle


def print_login_info(info: dict[str, Any]):
    print(
        """
User    {uname}
UID     {mid}
Avatar  {face}
Coin    {money}
""".format(
            **info
        )
    )


def print_video_info(info: dict[str, Any]):
    print(
        """
Title     {title}
Cover     {pic}
Uploader  {owner[name]}
Zone      {tname}
av{aid} / {bvid}
""".format(
            **info
        )
    )
    pages = info["pages"]
    print("%d Part(s) in total" % (len(pages)))
    print(
        *["P{page:<4d} cID{cid:<16d} {part}".format(**page) for page in pages],
        sep="\n",
    )
    print()


def print_audio_info(info: dict[str, Any]):
    print(
        """
Title       {title}
Uploader    {uname}
Author(s)   {author}
Cover       {cover}
Lyrics      {lyric}
au{id}""".format(
            **info
        ),
        end="",
    )
    if info.get("bvid"):
        print(" -> av{aid} / {bvid}\n".format(**info))
    else:
        print("\n")


def print_media_detail(detail: dict[str, Any]):
    print(
        """
Title   {season_title}
ss{season_id} / md{media_id}
Staff:
{actors}
""".format(
            **detail
        )
    )
    # 正片
    print("\nMain Episode(s):")
    main_eps = detail.get("episodes", [])
    _print_media_episodes(main_eps)
    offset = len(main_eps)
    if secs := detail.get("section"):
        for sec in secs:
            print("\nSection {title}:".format(**sec))
            eps = sec.get("episodes", [])
            _print_media_episodes(eps, pindex_offset=offset)
            offset += len(eps)


def _print_media_episodes(eplist: Optional[list[dict[str, Any]]], pindex_offset=0):
    if eplist:
        print(
            *[
                (
                    "P{i:<4d} ep{ep_id:<8d}".format(i=i + 1 + pindex_offset, **ep)
                    + f" {generate_media_ptitle(**ep, i=i + 1 + pindex_offset)}"
                )
                for i, ep in enumerate(eplist)
            ],
            sep="\n",
        )
    else:
        print("No episode here")


def print_manga_info(info: dict[str, Any]):
    print(
        """
Title       {title}
mc{id}""".format(
            **info
        )
    )
    print("by:", ",".join(info["author_name"]))
    print()

    if eplist := info["ep_list"]:
        print(len(eplist), "episode(s) in total.")
        for i, ep in enumerate(eplist):
            print(
                "P{i:<4d} ep{id:<10d} {lock_status} {short_title}_{title}".format(
                    **ep,
                    lock_status="[ Locked ]" if ep["is_locked"] else "[Unlocked]",
                    i=i + 1,
                )
            )
    else:
        print("No episode yet.")


def print_audio_playmenu_info(aminfo: dict[str, Any], songlist: list[dict[str, Any]]):
    print(
        """
Title       {title}
Uploader    {uname}
Cover       {cover}
""".format(
            **aminfo
        )
    )
    if not songlist:
        print("No song yet.")
    print(f"{len(songlist)} song(s) in total")
    for i, song in enumerate(songlist):
        print("P{i:<4d} au{id:<9d} {title}".format(**song, i=i + 1))


def print_series(series_meta: dict[str, Any], series_content: list[dict[str, Any]]):
    print(
        """
Title       {name}
series_id={series_id} / uid={mid}

{total} video(s) in total""".format(
            **series_meta
        )
    )
    for i, video in enumerate(series_content):
        print("P{i:<4d} {bvid} {title}".format(**video, i=i + 1))
    print()


def print_season(season_meta: dict[str, Any], archives: list[dict[str, Any]]):
    print(
        """
Title       {name}
season_id={season_id} / uid={mid}
Cover       {cover}

{total} video(s) in total""".format(**season_meta)
    )
    for i, video in enumerate(archives):
        print("P{i:<4d} {bvid} {title}".format(**video, i=i + 1))
    print()

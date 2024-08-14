from typing import Any, Optional

from bilicli.utils import generate_media_ptitle


def print_login_info(info: dict[str, Any]):
    print(
        """
User    {uname}
UID     {mid}
Avatar  {face}
Coin    {money}""".format(
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
Title     {title}
Uploader  {uname}
Author    {author}
Cover     {cover}
Lyrics    {lyric}
Desc      {intro}
au{id} -> {aid} / {bvid}
""".format(
            **info
        )
    )


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

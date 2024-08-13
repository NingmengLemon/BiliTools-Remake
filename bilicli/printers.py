from typing import Any, Sequence, Optional


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
        *["P{page:<4d} cID{cid:<12d} {part}".format(**page) for page in pages],
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
""".format(**detail)
    )
    eps = detail["episodes"]
    if eps:
        print()
        print(
            *[
                "P{i:<4d} epID{ep_id:<8d} {long_title}".format(i=i + 1, **ep)
                for i, ep in enumerate(eps)
            ],
            sep="\n",
        )
    else:
        print("No episode here")

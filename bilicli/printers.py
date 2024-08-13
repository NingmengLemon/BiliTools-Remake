from typing import Any, Sequence, Optional


def print_login_info(info: dict[str, Any]):
    print(
        """
昵称\t{uname}
UID\t{mid}
头像\t{face}
硬币\t{money} 个""".format(
            **info
        )
    )


def print_video_info(info: dict[str, Any], pindexs: Optional[Sequence[int]] = None):
    print(
        """
标题\t{title}
封面\t{pic}
UP主\t{owner[name]}
分区\t{tname}
av{aid} / {bvid}""".format(
            **info
        )
    )
    pages = info["pages"]
    print("\n共 %d 个分P" % (len(pages)))
    print(
        *[
            "P{page:<4d} cid{cid:<12d} {part}".format(**pages[i])
            for i in (pindexs if pindexs else range(len(pages)))
        ],
        sep="\n",
    )
    print()

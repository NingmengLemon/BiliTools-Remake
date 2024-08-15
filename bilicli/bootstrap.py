import argparse
import logging

from bilicli.app import App

LOGFILE_PATH = "./run.log"


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="BiliTools-Remake CLI",
        description="A simple media downloader for Bilibili",
    )

    parser.add_argument("--version", action="store_true", help="打印版本")

    #
    parser.add_argument("--debug", action="store_true", help="启用调试")

    #
    parser.add_argument(
        "--session",
        type=str,
        help="指定要加载的Session文件。注意请勿加载未信任的文件。",
    )

    parser.add_argument(
        "--max-worker", type=int, default=4, help="指定最大的同时进行的线程数"
    )

    #
    parser.add_argument("--login", action="store_true", help="进行登录流程")

    parser.add_argument("--logout", action="store_true", help="进行登出流程")

    # 媒体来源，唯一必选参数
    parser.add_argument("-i", "--input", type=str, help="媒体来源")

    # 是否只下载音频
    parser.add_argument("--audio-only", action="store_true", help="只抽取视频的音轨")

    parser.add_argument("--dry-run", action="store_true", help="只打印信息不进行下载")

    # 字幕语种
    parser.add_argument(
        "--subtitle-lang",
        type=str,
        help="指定字幕语种，如`zh-cn`，可传入`all`以下载所有可用的语种",
    )

    # 字幕类型
    parser.add_argument(
        "--subtitle-format",
        type=str,
        choices=["vtt", "srt", "lrc"],
        help="指定字幕格式，可选 vtt / srt / lrc",
    )

    # 视频编码
    parser.add_argument(
        "--video-codec",
        type=str,
        choices=["avc", "hevc"],
        help="指定视频编码，可选 avc / hevc",
    )

    # 视频质量
    parser.add_argument("--video-quality", type=str, help="指定视频质量")

    # 音频质量
    parser.add_argument("--audio-quality", type=str, help="指定音频质量")

    # 分P索引
    parser.add_argument(
        "--index",
        type=str,
        help="从1始计的分P索引，可使用半角逗号分隔多个。省略时指定所有分P。",
    )

    # 是否下载歌词
    parser.add_argument(
        "--lyrics", action="store_true", help="如果来源为音乐则下载歌词"
    )

    # 是否下载封面
    parser.add_argument("--cover", action="store_true", help="如果来源为音乐则下载封面")

    # 输出路径，唯一必选参数
    parser.add_argument(
        "-o", "--output", type=str, help="指定输出路径，省略时同 --dry-run"
    )

    return parser.parse_args()


def boot():
    args = parse_arguments()
    logger = logging.getLogger()
    handler = logging.FileHandler(LOGFILE_PATH, mode="w+", encoding="utf-8")
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)
    if args.debug:
        logger.setLevel(logging.DEBUG)
        print("-- Debug Enabled --")
        logging.debug("args: %s", vars(args))
    app = App(args)
    app.run()


if __name__ == "__main__":
    boot()

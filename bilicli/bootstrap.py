import argparse
import logging

from .app import App

LOGFILE_PATH = "./run.log"


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog="bilitools-cli",
        description="A simple media downloader for Bilibili",
    )

    parser.add_argument(
        "-v", "--version", action="store_true", help="Print version info"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode. Notice debug log contains personal info!",
    )

    parser.add_argument(
        "--data-filepath",
        type=str,
        help="Specify path to load data (a json file).",
    )

    parser.add_argument(
        "--max-worker",
        type=int,
        default=4,
        help="Specify the number of max concurrent worker threads, default to 4",
    )

    parser.add_argument("--login", action="store_true", help="Do login and exit")

    parser.add_argument("--logout", action="store_true", help="Do logout and exit")

    parser.add_argument(
        "--no-cookies-refresh", action="store_true", help="Don't do cookies refresh"
    )

    parser.add_argument(
        "--no-cache", action="store_true", help="Disable cache for *some* APIs"
    )

    parser.add_argument(
        "--cache-expire",
        type=int,
        default=5 * 60,
        help="Specify cache expire time, default to 300s",
    )

    parser.add_argument("-i", "--input", type=str, help="Specify media source")

    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="For videos, only download their audio track",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print info of source and soon exit, without downloading",
    )

    parser.add_argument(
        "--subtitle-lang",
        type=str,
        help="For videos, specify language of subtitle to download like `zh-cn` if available. Give `all` to download all available.",
    )

    parser.add_argument(
        "--subtitle-format",
        type=str,
        choices=["vtt", "srt", "lrc"],
        default="vtt",
        help="For videos, choose subtitle format from `vtt` / `srt` / `lrc`, default to `vtt`",
    )

    parser.add_argument(
        "--video-codec",
        type=str,
        choices=["avc", "hevc"],
        default="avc",
        help="For videos, choose codec of video stream from `avc` / `hevc` if available.",
    )

    parser.add_argument(
        "--video-quality",
        type=str,
        help="Specify video stream quality, leave blank for highest. Mismatch means highest too.",
    )

    parser.add_argument(
        "--audio-quality",
        type=str,
        help="Specify audio stream quality, leave blank for highest. Mismatch means highest too.",
    )

    parser.add_argument(
        "--index",
        type=str,
        help="""Specify index of episode to download, count from 1. 
        Use comma to split multiple, use hyphen to give a range.
        Use --dry-run to preview index if not sure.""",
    )

    parser.add_argument(
        "--need-lyrics",
        action="store_true",
        help="For music, download their lyrics if available",
    )

    parser.add_argument("--need-cover", action="store_true", help="Download cover")

    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Don't write metadata into output file",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Specify path to a folder to store output file. Leaving it blank is equal to use --dry-run",
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

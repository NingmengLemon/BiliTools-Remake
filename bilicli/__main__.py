import argparse

from bilicli.process import main_process

# fmt: off
def parse_arguments():
    parser = argparse.ArgumentParser(description="BiliTools-Remake CLI")

    parser.add_argument('--version', action='store_true', help='打印版本然后退出')

    # 媒体来源，唯一必选参数
    parser.add_argument('-i', '--input', required=True, type=str, help='媒体来源')

    # 是否只下载音频
    parser.add_argument('--audio-only', action='store_true', help='只抽取视频的音轨')

    #
    parser.add_argument('--dry-run', action='store_true', help='只打印信息不实际下载')

    #
    parser.add_argument('--debug', action='store_true', help='启用调试')

    # 字幕语种
    parser.add_argument('--subtitle-version', type=str, help='指定字幕语种，如`zh-cn`，可传入`all`以下载所有可用的语种')

    # 字幕类型
    parser.add_argument('--subtitle-type', type=str, choices=['vtt', 'srt', 'lrc'], help='指定字幕格式，可选 vtt / srt / lrc')

    # 视频编码
    parser.add_argument('--video-codec', type=str, choices=['avc', 'hevc'], help='指定视频编码，可选 avc / hevc')

    # 视频质量
    parser.add_argument('--video-quality', type=str, help='指定视频质量')

    # 音频质量
    parser.add_argument('--audio-quality', type=str, help='指定音频质量')

    # 分P索引
    parser.add_argument('--index', type=str, help='分P索引，可使用半角逗号分隔多个')

    # 是否下载歌词
    parser.add_argument('--lyrics', action='store_true', help='如果来源为音乐则下载歌词')

    # 是否下载封面
    parser.add_argument('--cover', action='store_true', help='如果来源为音乐则下载封面')

    # 输出路径，唯一必选参数
    parser.add_argument('-o', '--output', required=True, type=str, help='指定输出路径')

    return parser.parse_args()
# fmt: on

# 示例：获取命令行参数
if __name__ == "__main__":
    args = parse_arguments()
    # main_process(args)

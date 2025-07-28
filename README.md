# BiliTools-Remake

A simple utility to download media from Bilibili, the successor(?) of [BiliTools](https://github.com/NingmengLemon/BiliTools). Both of them are self-use-oriented.

> ~~Actually just a nerd's self-entertaining toy lol.~~

Not tested on Linux yet.

*Still under development...*

## Now it can do

- Download common videos (or only their audio tracks)
- Download bangumi and movies
- Download songs
- ~~Download comics~~
- Download video collections (called season or series) created by users
- Login by scanning QRCode

**Notice:** This program cannot help you to unlock media on Bilibili, plz check your permission before you act. Also there exists risks (eg. get account banned) because of incomplete implemention solving Bilibili risk control, you are responsible for the consequences of using this program. **You have been warned.**

## Dependencies

- Python 3.10 or above
- FFmpeg

## Usage

TLDR:

- Use `-i STRING` to give a source like URL, with a valid id in it.
- Use `-o PATH` to give a path to folder to save file(s).
- Use `--index STRING` to tell program which episode(s) to download.

```
> bilitools-cli -h
usage: bilitools-cli [-h] [-v] [--debug] [--data-filepath DATA_FILEPATH] [--max-worker MAX_WORKER] [--login] [--logout] [--no-cookies-refresh]
                     [--no-cache] [--cache-expire CACHE_EXPIRE] [-i INPUT] [--audio-only] [--dry-run] [--subtitle-lang SUBTITLE_LANG]
                     [--subtitle-format {vtt,srt,lrc}] [--video-codec {avc,hevc}] [--video-quality VIDEO_QUALITY]
                     [--audio-quality AUDIO_QUALITY] [--index INDEX] [--need-lyrics] [--need-cover] [--no-metadata] [-o OUTPUT]

A simple media downloader for Bilibili

options:
  -h, --help            show this help message and exit
  -v, --version         Print version info
  --debug               Enable debug mode. Notice debug log contains personal info!
  --data-filepath DATA_FILEPATH
                        Specify path to load data (a json file).
  --max-worker MAX_WORKER
                        Specify the number of max concurrent worker threads, default to 4
  --login               Do login and exit
  --logout              Do logout and exit
  --no-cookies-refresh  Don't do cookies refresh
  --no-cache            Disable cache for *some* APIs
  --cache-expire CACHE_EXPIRE
                        Specify cache expire time, default to 300s
  -i INPUT, --input INPUT
                        Specify media source
  --audio-only          For videos, only download their audio track
  --dry-run             Only print info of source and soon exit, without downloading
  --subtitle-lang SUBTITLE_LANG
                        For videos, specify language of subtitle to download like `zh-cn` if available. Give `all` to download all available.    
  --subtitle-format {vtt,srt,lrc}
                        For videos, choose subtitle format from `vtt` / `srt` / `lrc`, default to `vtt`
  --video-codec {avc,hevc}
                        For videos, choose codec of video stream from `avc` / `hevc` if available.
  --video-quality VIDEO_QUALITY
                        Specify video stream quality, leave blank for highest. Mismatch means highest too.
  --audio-quality AUDIO_QUALITY
                        Specify audio stream quality, leave blank for highest. Mismatch means highest too.
  --index INDEX         Specify index of episode to download, count from 1. Use comma to split multiple, use hyphen to give a range. Use --dry-  
                        run to preview index if not sure.
  --need-lyrics         For music, download their lyrics if available
  --need-cover          Download cover
  --no-metadata         Don't write metadata into output file
  -o OUTPUT, --output OUTPUT
                        Specify path to a folder to store output file. Leaving it blank is equal to use --dry-run
```

### Examples

For example, you want to download video [`BV1GJ411x7h7`](https://www.bilibili.com/video/BV1GJ411x7h7/) and its `zh-cn` subtitle, and save these into current dir:

Login if you want to access higher video quality (guest's max quality is 480P, common user's is 1080P), run:

```bash
bilitools-cli --login
```

Scan the QRCode with Bilibili APP on your phone and confirm.

Secondly, run:

```bash
bilitools-cli -i "https://www.bilibili.com/video/BV1GJ411x7h7/" --subtitle-lang zh-cn -o ./
```

And program will do next things for you.

## Thanks a lot

- [bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect): Where the dream begins.
- [FFmpeg](https://ffmpeg.org/): A super-big-cup media processor.

## TODO

- Enhance ability to tolerate errors
- Lower requirement of Python version
- Try to bypass the risk-control mechanism of Bilibili
- Optimize cache logic
- Add more prompt text
- Add confirm option
- Fix failure to download some old videos that can only be downloaded with mp4 format instead of DASH (see also [SocialSisterYi/bilibili-API-collect#88](https://github.com/SocialSisterYi/bilibili-API-collect/issues/888#event-17327233308))
- *and a lot...*

*Will be rewritten in async, maybe*

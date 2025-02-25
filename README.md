# BiliTools-Remake

船新的异步版本正在绝赞构思中 ~~希望别搞成构思~~

---

预期包含:

- [ ] 视频/视频音轨
- [ ] 音乐
- [ ] 漫画
- [ ] 专栏/opus
- [ ] 课程
- [ ] 动态
- [ ] 番剧/影视
- [ ] 合集/频道
- [ ] 收藏夹
- [ ] 用户投稿
- [ ] 稍后再看
- [ ] 歌单
- [ ] 网易云关联搜索
- [ ] [BilibiliSponsorBlock](https://github.com/hanydd/BilibiliSponsorBlock/wiki/API) 驱动的广告片段自动切除
- [ ] 优雅的异步并发下载管理
- [ ] 更好的风控解决方案
- [ ] 更好的缓存方案
- [ ] 更好的程序组织
- [ ] CLI 和 GUI ~~(可能使用 Flet 或 Qt?)~~, 我都要!

---

规划 什么的

- bilitools-cli
  - download / d
    - -i & -o
    - --index / --episode / -e
    - --audio-only / -ao
    - --video-quality / -vq
    - --audio-quality / -aq
    - --dry-run / -dr
    - --subtitle-lang / -sl
    - --subtitle-format / -sf
    - --video-codec / -vc
    - --audio-codec / -ac
    - --yes / -y
  - login
  - logout
- bilitools-gui
- config
  - confirm_before_act
  - data_path
  - concurrency
  - default_qualities
    - audio
    - video
  - subtitle_langs
  - subtitle_format
  - allow_ai_subtitle
  - cache_expire
  - auto_refresh_cookies

- --debug
- --help

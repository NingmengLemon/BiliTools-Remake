# BiliTools-Remake 后续改造方案

> 写作背景：当前 `refactor` 分支已经从 `main` 的散装 `src/biliapis`、`src/bilicli`、`src/bilicore` 结构迁移到 `src/bilitools/...` 包结构，并把依赖管理从 PDM 切到 uv；同时 `pyproject.toml` 已引入 `bilibili-api-python`，并指向本地 fork 对应的 Git 源。当前分支因为刚换依赖暂时跑不起来，因此本文以静态阅读、分支差异和本地 `references/bilibili-api` 能力梳理为依据。

## 1. 总体品鉴

这是一个非常典型的“先把能跑的链路打通，再围绕痛点补抽象”的个人工具项目：目标很务实，范围也很克制，核心体验围绕“给一个 B 站链接，识别类型，预览信息，选择集数，下载流，封装成最终媒体文件”。两年前写到这个程度其实相当能打：

- 已经有清晰分层：API 封装、下载/封装核心、CLI 编排三层基本分开。
- 已经覆盖常见媒体：普通视频、番剧/电影、音频、歌单、用户合集/系列，漫画虽然 README 里标注废弃但代码仍保留。
- 已经考虑登录态、WBI 签名、缓存、fallback、断点续传、字幕转换、FFmpeg 元数据/封面写入。
- 测试虽然更偏“能不能请求真实接口”和少量纯函数测试，但至少覆盖了 API、下载器、fallback、流选择等关键点。

它的主要问题不在“想法不行”，而是两年前快速推进时留下的几个结构性债务：同步阻塞、线程状态模型、手写 API 封装、会变的 B 站接口、登录态存储、CLI 与业务编排耦合。现在既然已经准备切到 `bilibili-api-python`，最合理的方向不是继续在原有 `biliapis` 上补丁式维护，而是把项目定位成“下载器和用户体验层”，把易变 API 调用下沉到外部库和少量适配器。

## 2. 当前分支相对 main 的状态

根据 `git diff --stat main...HEAD` 和提交历史，当前 `refactor` 分支主要做了这些工作：

1. 包结构重组：原 `src/biliapis`、`src/bilicli`、`src/bilicore` 迁入 `src/bilitools/biliapis`、`src/bilitools/bilicli`、`src/bilitools/bilicore`。
2. 入口修正：`pyproject.toml` 中脚本入口为 `bilitools-cli = "bilitools.bilicli:boot"`。
3. 依赖迁移：移除 `pdm.lock`，新增 `uv.lock`，依赖包含 `bilibili-api-python`、`curl-cffi`、`tqdm`、`typer`。
4. 登录刷新被临时禁用：`refresh_cookies_flow` 目前检查到需要刷新后直接返回，避免未完成流程破坏登录态。
5. 大量 import 改为相对路径，测试也改到新包名。

值得注意的风险点：

- `README.md` 仍写 Python 3.10+，但 `pyproject.toml` 已要求 `>=3.11,<3.13`，文档与实际依赖不一致。
- 当前项目仍依赖 `qrcode`、`requests`、`pytest` 等旧链路运行时或测试时模块，但 `pyproject.toml` 的主依赖已经只剩新库和少量工具，可能是“现在跑不起来”的直接原因之一。
- `bilibili-api-python` 本身是 GPL-3.0-or-later，当前项目声明 MIT。如果未来分发时直接依赖或集成，需要确认许可证边界和发布策略。

## 3. 现有架构拆解

### 3.1 API 层

当前 `biliapis` 是手写同步 API 封装，典型调用路径是：

- `APIContainer` 收集所有 `*APIs` 组件并共享 `requests.Session`、`CachedWbiManager`、`extra_data`。
- `APITemplate.request_template` 用装饰器统一发请求、解析 JSON/文本/二进制、接入简单缓存。
- `checker` 装饰器检查 B 站返回码。
- `VideoAPIs.get_stream_dash` 先走 WBI 播放地址，再 fallback 到 PGC 和旧 playurl 接口。

优点：

- 封装很轻，调用方直接拿原始 dict，迁移成本低。
- WBI、fallback、缓存这些易踩坑点已有基本实现。

问题：

- 完全同步，和未来 `bilibili-api-python` 的 async 风格冲突。
- 直接返回原始 dict，业务层强依赖 B 站字段结构，接口变动影响面大。
- `APIContainer` 动态挂属性，类型提示和 IDE 体验弱。
- 旧接口覆盖面有限，需要持续追 B 站变化。

### 3.2 核心下载层

核心下载层目前分两块：

- `downloader.py` 负责单文件下载、临时文件、Range、断点续传、一个未实际使用的多线程下载器。
- `threads.py` 负责“一个下载任务”的编排，包括取详情、选流、下音频/视频/字幕/封面、调用 FFmpeg 转换或合流。

优点：

- 文件下载逻辑和媒体任务逻辑大体分离。
- 已有 `.download` 临时文件和 Range 续传意识。
- `ThreadProgressMixin` 给 CLI 进度条提供了统一接口。

问题：

- “任务”直接继承 `threading.Thread`，任务状态、下载策略、UI 进度耦合在一起。
- 异常只收集不结构化，CLI 最后只能提示“有异常，看日志”。
- 下载器对 HTTP 客户端抽象不足，未来从 `requests` 切到 `curl-cffi` 或异步客户端会牵动较多代码。
- `MultiThreadDownloader` 标注未实际使用，且 `_worker_single` 中线程未启动，建议不要继续沿用。
- 旧视频 FLV/MP4 非 DASH 路径仍是 TODO，但 `bilibili-api-python` 的解析器已经能识别 FLV/MP4 流。

### 3.3 CLI 层

CLI 当前使用 `argparse`：

- `bootstrap.py` 定义所有参数。
- `App` 负责加载状态、初始化缓存、检查 FFmpeg、判断登录和入口分发。
- `CliCore` 根据 `extract_ids` 的结果派发到普通视频、番剧、音频、歌单、漫画、合集/系列处理函数。
- `printers` 做预览输出，`utils.run_threads` 用 `tqdm` 展示进度。

优点：

- 单命令多媒体类型自动识别，用户输入成本低。
- `--dry-run`、`--index`、`--audio-only`、字幕、封面、元数据等选项都比较实用。

问题：

- CLI 参数和业务 option 字典混传，任务类再白名单过滤，容易出现参数名漂移。
- `argparse` 帮助文本已经比较长，继续扩展会变难维护。
- `App` 同时做状态、登录、缓存、依赖检查、业务入口分发，职责偏重。
- README 帮助文本和真实参数容易不同步。

### 3.4 状态与登录

当前 `svld.py` 将整个 `requests.Session` pickle 后 Base64 + SHA256 存进 JSON。

优点：

- 简单粗暴，能保存 cookies 和 session 配置。

问题：

- pickle 反序列化不适合长期配置文件，也不适合跨版本迁移。
- JSON 文件没有权限收紧，也没有明文敏感信息提示。
- 未来切 `bilibili-api-python` 后，更合适保存的是 `Credential` 字段：`SESSDATA`、`bili_jct`、`buvid3`、`buvid4`、`DedeUserID`、`ac_time_value`。

## 4. `bilibili-api-python` 能力对照

本地 `references/bilibili-api` 足够覆盖当前项目大部分手写 API：

| 当前能力 | 现有实现 | `bilibili-api-python` 对应能力 | 建议 |
|---|---|---|---|
| 普通视频详情 | `VideoAPIs.get_video_detail` | `video.Video.get_info()` | 迁移 |
| 普通视频分 P | `VideoAPIs.get_pagelist` | `video.Video.get_pages()` | 迁移 |
| 普通视频取流 | `VideoAPIs.get_stream_dash` | `video.Video.get_download_url()` + `VideoDownloadURLDataDetecter` | 优先迁移 |
| 番剧/电影详情 | `MediaAPIs.get_detail` | `bangumi.Bangumi` / `bangumi.Episode` | 迁移 |
| 番剧取流 | `VideoAPIs` fallback 到 PGC | `bangumi.Episode.get_download_url()` + 同一个 Detecter | 优先迁移 |
| 音频详情 | `AudioAPIs.get_info` | `audio.Audio.get_info()` | 迁移 |
| 音频取流 | `AudioAPIs.get_stream` | `audio.Audio.get_download_url()` | 迁移但注意质量参数能力可能需补 adapter |
| 歌单 | `AudioAPIs.get_playmenu_*` | `audio.AudioList.get_info()` / `get_song_list()` | 迁移 |
| 二维码登录 | `QRLoginAPIs` + CLI polling | `login_v2.QrCodeLogin` | 迁移 |
| Credential | `requests.Session.cookies` | `utils.network.Credential` | 应作为新状态核心 |
| WBI 签名 | 自写 `CachedWbiManager` | `Api(..., wbi=True)` 内置 | 删除自写 |
| 旧视频 FLV/MP4 | 当前 TODO | `VideoDownloadURLDataDetecter` 支持 FLV/MP4 | 借机补齐 |

特别值得迁移的点是 `VideoDownloadURLDataDetecter`：它已经能解析 DASH 视频/音频、FLAC、杜比、HDR、FLV/MP4，并提供 `detect_best_streams()`。这可以替代当前 `parser.select_quality` 的一部分逻辑，同时解决 README TODO 里“旧视频只有 MP4/FLV 无法下载”的问题。

## 5. 推荐目标架构

建议把项目重构为“薄 API 适配 + 下载任务引擎 + CLI/UI”三层：

```text
bilitools/
  adapters/
    bilibili.py        # 只把 bilibili-api-python 的对象转成项目内模型
  models/
    media.py           # VideoInfo / EpisodeInfo / StreamInfo / DownloadPlan
  core/
    resolver.py        # 输入 URL/ID -> MediaResource
    planner.py         # MediaResource + Options -> DownloadPlan
    downloader.py      # 文件下载，HTTP 客户端可替换
    muxer.py           # FFmpeg 合流/转码/元数据
    tasks.py           # 执行 DownloadPlan，报告结构化事件
  cli/
    app.py             # Typer 命令定义
    views.py           # rich/tqdm 输出
    state.py           # Credential 保存/加载
```

### 核心原则

1. API 层不再向业务层泄漏原始 dict。先转成项目内数据模型。
2. CLI 不再直接创建 `SingleVideoThread` 这类线程对象，而是生成下载计划。
3. 下载任务只关心 URL、headers、目标文件、后处理步骤，不关心“这个 URL 来自视频还是番剧”。
4. 登录态只保存 Credential 所需字段，不保存 pickle session。
5. 短期允许使用 `asyncio.run()` 包住 `bilibili-api-python` 的 async API；中期再决定是否把全链路改 async。

## 6. 分阶段迭代路线

### Phase 0：先让当前分支跑起来

目标：不做大迁移，先修复依赖与入口，让测试和 CLI 至少能启动。

任务：

- 补齐当前代码实际使用但 `pyproject.toml` 未声明的依赖：`requests`、`qrcode`，以及测试/开发依赖确认。
- 同步 README 的 Python 版本、安装方式和当前入口。
- 跑纯函数测试，优先保证 `test_selectdash`、`test_fallback` 通过。
- 给真实网络测试加 marker，避免默认测试直接打 B 站接口。
- 修复明显运行错误：例如 `run_as_async_decorator` 当前 wrapper 返回 coroutine 时少了 `await`。

验收：

- `uv sync` 成功。
- `uv run bilitools-cli -h` 成功。
- `uv run pytest -m "not network"` 成功。

### Phase 1：建立新适配层，但保持旧 CLI 可用

目标：不要一上来删 `biliapis`，先新增 `bilibili-api-python` adapter，选一条最核心链路替换。

任务：

- 新增 `CredentialStore`，用 JSON 保存 Credential 字段；保留旧 session 文件一次性导入能力。
- 新增 `BilibiliClient` adapter，内部使用 `bilibili_api.video.Video`、`bangumi.Episode`、`audio.Audio`。
- 新增项目内模型：`MediaInfo`、`PageInfo`、`StreamInfo`、`StreamKind`、`DownloadPlan`。
- 先迁移普通视频：详情、分 P、取流、字幕信息。
- 保留旧 `SingleVideoThread` 外观，但内部改用新 adapter 或新 planner，减少 CLI 改动面。

验收：

- 普通视频 dry-run 能展示标题、分 P、可选流。
- 普通视频下载 DASH 成功。
- 老 MP4/FLV 流视频至少能下载单文件。

### Phase 2：重做下载计划与执行器

目标：把“线程任务对象”改成“计划 + 执行器”，为 async、重试、断点续传和更好 UI 打基础。

任务：

- 定义 `DownloadPlan`：包含临时文件、最终文件、下载项列表、后处理动作。
- 定义 `DownloadItem`：URL 列表、headers、目标路径、可选校验信息。
- 下载器从 `requests` 抽象为 `HttpDownloader`，预留 `curl-cffi` 实现。
- 执行器上报结构化事件：`started`、`progress`、`retry`、`postprocess`、`done`、`failed`。
- FFmpeg 操作拆到 `muxer.py`，并让命令可测试。
- 清理或删除未使用的 `MultiThreadDownloader`。

验收：

- 单视频、多 P、仅音频、字幕、封面、元数据都通过新执行器。
- 失败时 CLI 能显示哪个文件、哪个阶段、哪个异常。
- 断点续传行为有单元测试或本地 HTTP fixture 测试。

### Phase 3：全面迁移媒体类型

目标：逐步删除自写 `biliapis`。

建议顺序：

1. 普通视频。
2. 番剧/电影。
3. 音频与歌单。
4. 用户合集/系列。
5. 漫画：如果 `bilibili-api-python` 覆盖不足或接口加密严重，建议明确标为 experimental 或移除。

每迁移一类，都保留同一套输出模型和下载计划，不让 CLI 关心底层 API 差异。

验收：

- `src/bilitools/biliapis` 不再被核心下载路径引用。
- WBI、checker、request_template、reqcache 这些自写 API 基建可以删除或归档。
- 真实网络测试只测 adapter，核心 planner/downloader 使用 fixture。

### Phase 4：CLI 体验升级

目标：从“一个大命令 + 很多参数”升级成更清楚的命令体系。

建议用 `typer` 和可选 `rich`：

```text
bilitools login
bilitools logout
bilitools whoami
bilitools inspect URL
bilitools download URL -o PATH --index 1-3 --video-quality 1080p
bilitools config show
```

任务：

- `inspect` 只解析和展示，不下载，替代现在的隐式 dry-run。
- `download` 专注执行。
- `login` 使用 `QrCodeLogin`，成功后保存 Credential。
- 配置文件区分 credential、默认下载选项、缓存。
- README 的 CLI help 自动生成或至少减少复制粘贴大段帮助文本。

验收：

- 新旧入口可并存一个版本，旧 `bilitools-cli` 给出迁移提示。
- 命令帮助可读性明显提升。
- 配置与凭据路径清晰，敏感字段不在 debug 日志直接打印。

### Phase 5：质量工程

目标：让这个个人工具更像一个“可长期修”的项目。

任务：

- 引入 ruff 格式化和 lint。
- 引入 pyright 或 basedpyright，至少检查 adapter/model/core。
- 网络测试加 marker，CI 默认跳过。
- 加本地 fixture：播放地址 JSON、详情 JSON、字幕 JSON、旧 MP4/FLV JSON。
- 对 FFmpeg 命令生成做单元测试，不必真的转码。
- 对 filename escaping、index parsing、stream selection、download resume 做纯测试。

## 7. 近期最小可执行清单

如果只看下一轮开发，建议按这个顺序做：

1. 修 `pyproject.toml` 依赖，让当前 CLI 能启动。
2. 把登录态目标模型从 `requests.Session` 改成 `Credential` 字段 JSON。
3. 写 `BilibiliClient.get_video()` 和 `BilibiliClient.get_video_streams()`，只覆盖普通视频。
4. 写 `StreamInfo` 和从 `VideoDownloadURLDataDetecter` 到 `StreamInfo` 的转换。
5. 修改 `SingleVideoThread` 或新建 `VideoDownloadTask`，让普通视频下载走新 adapter。
6. 用 fixture 测试“DASH 最佳流”“FLAC”“MP4/FLV 单流”三种计划生成。
7. 普通视频稳定后，再迁移番剧 `Episode.get_download_url()`。

## 8. 可以直接删除或延后处理的东西

建议删除或冻结：

- 未实际使用且有明显问题的 `MultiThreadDownloader`。
- 自写 WBI 和 API fallback，在迁移后不再维护。
- 直接 pickle session 的状态文件格式。
- 默认真实网络测试。

建议暂缓：

- 全链路 async。先用 async adapter + sync CLI 包一层即可，避免一次性大爆炸。
- 漫画下载。除非你确实还用，否则它会吃掉很多接口兼容成本。
- 多线程分片下载。B 站 CDN 和 Range 行为不稳定，先把单连接续传做好更有价值。

## 9. 关键风险

1. **许可证风险**：`bilibili-api-python` 是 GPL-3.0-or-later，当前项目 MIT。若发布包含该依赖的工具，需要重新评估许可证声明。
2. **接口风险**：B 站接口变化频繁，adapter 层一定要小，方便替换。
3. **登录风控风险**：扫码登录、cookie 刷新、BUVID、WBI 都可能影响可用性，不建议在 debug 日志输出完整 cookies。
4. **平台风险**：README 写未测 Linux，但其实 Windows 文件名、路径、FFmpeg 行为也要系统化测试。
5. **质量参数兼容风险**：现有 CLI 接受 `1080p`、`132k`、`max`、`min` 等字符串，新库使用 Enum，迁移时要保留兼容映射。

## 10. 一句话结论

这个项目最值得保留的是“统一输入识别 + 下载计划 + FFmpeg 后处理 + 个人使用体验”，最该放弃的是“继续手写追逐 B 站 API”。下一步不要急着全盘重写，先把普通视频链路迁到 `bilibili-api-python` adapter，稳定后用同一套模型扩到番剧和音频；当旧 `biliapis` 不再处在主路径时，再做 CLI 和下载执行器的重构。这样风险最低，也最符合当前 `refactor` 分支已经开始做的方向。

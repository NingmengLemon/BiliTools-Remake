# 此子模块的内容基本照抄自 bilibili-API-collect by @SocialSisterYi

# 有些或许应该用 enum 的？但是有点懒（）

video_zone_main = {
    1: "动画",
    13: "番剧",
    167: "国创",
    3: "音乐",
    129: "舞蹈",
    4: "游戏",
    36: "知识",
    188: "科技",
    234: "运动",
    223: "汽车",
    160: "生活",
    211: "美食",
    217: "动物圈",
    119: "鬼畜",
    155: "时尚",
    202: "资讯",
    5: "娱乐",
    181: "影视",
    177: "纪录片",
    23: "电影",
    11: "电视剧",
}

video_zone_child = {
    24: "MAD·AMV",
    25: "MMD·3D",
    47: "短片·手书·配音",
    210: "手办·模玩",
    86: "特摄",
    27: "综合",
    33: "连载动画",
    32: "完结动画",
    51: "资讯",
    152: "官方延伸",
    153: "国产动画",
    168: "国产原创相关",
    169: "布袋戏",
    195: "动态漫·广播剧",
    170: "资讯",
    28: "原创音乐",
    31: "翻唱",
    30: "VOCALOID·UTAU",
    194: "电音",
    59: "演奏",
    193: "MV",
    29: "音乐现场",
    130: "音乐综合",
    20: "宅舞",
    198: "街舞",
    199: "明星舞蹈",
    200: "中国舞",
    154: "舞蹈综合",
    156: "舞蹈教程",
    17: "单机游戏",
    171: "电子竞技",
    172: "手机游戏",
    65: "网络游戏",
    173: "桌游棋牌",
    121: "GMV",
    136: "音游",
    19: "Mugen",
    201: "科学科普",
    124: "社科·法律·心理",
    228: "人文历史",
    207: "财经商业",
    208: "校园学习",
    209: "职业职场",
    229: "设计·创意",
    122: "野生技术协会",
    95: "数码",
    230: "软件应用",
    231: "计算机技术",
    232: "工业·工程·机械",
    233: "极客DIY",
    235: "篮球·足球",
    164: "健身",
    236: "竞技体育",
    237: "运动文化",
    238: "运动综合",
    176: "汽车生活",
    224: "汽车文化",
    225: "汽车极客",
    226: "智能出行",
    227: "购车攻略",
    138: "搞笑",
    239: "家居房产",
    161: "手工",
    162: "绘画",
    21: "日常",
    76: "美食制作",
    212: "美食侦探",
    213: "美食测评",
    214: "田园美食",
    215: "美食记录",
    218: "喵星人",
    219: "汪星人",
    220: "大熊猫",
    221: "野生动物",
    222: "爬宠",
    75: "动物综合",
    22: "鬼畜调教",
    26: "音MAD",
    126: "人力VOCALOID",
    216: "鬼畜剧场",
    127: "教程演示",
    157: "美妆",
    158: "服饰",
    159: "T台",
    192: "风尚标",
    203: "热点",
    204: "环球",
    205: "社会",
    206: "综合",
    71: "综艺",
    137: "明星",
    182: "影视杂谈",
    183: "影视剪辑",
    85: "短片",
    184: "预告·资讯",
    37: "人文·历史",
    178: "科学·探索·自然",
    179: "军事",
    180: "社会·美食·旅行",
    147: "华语电影",
    145: "欧美电影",
    146: "日本电影",
    83: "其他国家",
    185: "国产剧",
    187: "海外剧",
}

# fmt: off
video_zone_relation = {  # 主分区与子分区的隶属关系
    1: [24, 25, 47, 210, 86, 27],
    13: [33, 32, 51, 152],
    167: [153, 168, 169, 195, 170],
    3: [28, 31, 30, 194, 59, 193, 29, 130],
    129: [20, 198, 199, 200, 154, 156],
    4: [17, 171, 172, 65, 173, 121, 136, 19],
    36: [201, 124, 228, 207, 208, 209, 229, 122],
    188: [95, 230, 231, 232, 233],
    234: [235, 164, 236, 237, 238],
    223: [176, 224, 225, 226, 227],
    160: [138, 239, 161, 162, 21],
    211: [76, 212, 213, 214, 215],
    217: [218, 219, 220, 221, 222, 75],
    119: [22, 26, 126, 216, 127],
    155: [157, 158, 159, 192],
    202: [203, 204, 205, 206],
    5: [71, 137],
    181: [182, 183, 85, 184],
    177: [37, 178, 179, 180],
    23: [147, 145, 146, 83],
    11: [185, 187],
}
# fmt: on


def child_zone_to_main_zone(tid):
    if tid in video_zone_relation:
        return tid
    relation = list(video_zone_relation.items())
    for mtid, ctids in relation:
        if tid in ctids:
            return mtid
    return 0


error_code = {
    -1: "应用程序不存在或已被封禁",
    -2: "AccessKey错误",
    -3: "API校验密匙错误",
    -4: "调用方对该Method没有权限",
    -101: "账号未登录",
    -102: "账号被封停",
    -103: "积分不足",
    -104: "硬币不足",
    -105: "验证码错误",
    -106: "账号非正式会员或在适应期",
    -107: "应用不存在或者被封禁",
    -108: "未绑定手机",
    -110: "未绑定手机",
    -111: "CSRF校验失败",
    -112: "系统升级中",
    -113: "账号尚未实名认证",
    -114: "请先绑定手机",
    -115: "请先完成实名认证",
    -304: "没有改动",
    -307: "撞车跳转",
    -400: "请求错误",
    -401: "未认证",
    -403: "访问权限不足",
    -404: "啥都木有",
    -405: "不支持该方法",
    -409: "冲突",
    -500: "服务器错误",
    -503: "过载保护,服务暂不可用",
    -504: "服务调用超时",
    -509: "超出限制",
    -616: "上传文件不存在",
    -617: "上传文件太大",
    -625: "登录失败次数太多",
    -626: "用户不存在",
    -628: "密码太弱",
    -629: "用户名或密码错误",
    -632: "操作对象数量限制",
    -643: "被锁定",
    -650: "用户等级太低",
    -652: "重复的用户",
    -658: "Token过期",
    -662: "密码时间戳过期",
    -688: "地理区域限制",
    -689: "版权限制",
    -701: "扣节操失败",
    -8888: "服务器错误",
    -2202: "CSRF请求非法",
    7201006: "音频未找到或已下架",
    72000000: "请求错误",
    72010027: "版权音乐重定向",
    12002: "评论区已关闭",
    12009: "评论区Type不合法",
    19002003: "房间信息不存在",
    60004: "直播间不存在",
}

stream_dash_video_quality = {
    16: "360P",
    32: "480P",
    64: "720P",
    74: "720P60",
    80: "1080P",
    112: "1080P+",
    116: "1080P60",
    120: "4K",
    125: "HDR",
    126: "DOLBY",
    127: "8K",
}

# 以下划线结尾的表示反查字典
stream_dash_video_quality_ = {v: k for k, v in stream_dash_video_quality.items()}

stream_dash_audio_quality = {
    30216: "64K",
    30232: "132K",
    30280: "192K",
    30251: "FLAC",
}

stream_dash_audio_quality_ = {v: k for k, v in stream_dash_audio_quality.items()}

# 与MP4共用一个表
stream_flv_video_quality = {
    6: "240P",
    16: "360P",
    32: "480P",
    64: "720P",
    74: "720P60",
    80: "1080P",
    112: "1080P+",
    116: "1080P60",
    120: "4K",
}

stream_flv_video_quality_ = {v: k for k, v in stream_flv_video_quality.items()}

media_type = {
    1: "番剧",
    2: "电影",
    3: "纪录片",
    4: "国创",
    5: "电视剧",
    7: "综艺",
}

stream_audio_quality = {
    -1: "192K_Trial",
    0: "128K",
    1: "192K",
    2: "320K",
    3: "FLAC",
}

stream_audio_quality_ = {v: k for k, v in stream_audio_quality.items()}

ban_reason = {
    1: "刷屏",
    2: "抢楼",
    3: "发布色情低俗信息",
    4: "发布赌博诈骗信息",
    5: "发布违禁相关信息",
    6: "发布垃圾广告信息",
    7: "发布人身攻击言论",
    8: "发布侵犯他人隐私信息",
    9: "发布引战言论",
    10: "发布剧透信息",
    11: "恶意添加无关标签",
    12: "恶意删除他人标签",
    13: "发布色情信息",
    14: "发布低俗信息",
    15: "发布暴力血腥信息",
    16: "涉及恶意投稿行为",
    17: "发布非法网站信息",
    18: "发布传播不实信息",
    19: "发布怂恿教唆信息",
    20: "恶意刷屏",
    21: "账号违规",
    22: "恶意抄袭",
    23: "冒充自制原创",
    24: "发布青少年不良内容",
    25: "破坏网络安全",
    26: "发布虚假误导信息",
    27: "仿冒官方认证账号",
    28: "发布不适宜内容",
    29: "违反运营规则",
    30: "恶意创建话题",
    31: "发布违规抽奖",
    32: "恶意冒充他人",
}

ban_origin = {
    1: "评论",
    2: "弹幕",
    3: "私信",
    4: "标签",
    5: "个人资料",
    6: "投稿",
    8: "专栏",
    10: "动态",
    11: "相簿",
}

live_stream_quality = {2: "流畅", 3: "高清", 4: "原画"}

live_stream_qn = {80: "流畅", 150: "高清", 400: "蓝光", 10000: "原画"}

comment_types = {
    1: "视频稿件",  # avid
    2: "话题",  # 话题id
    4: "活动",  # 活动id
    5: "小视频",  # 小视频id
    6: "小黑屋",  # 封禁公示id
    7: "公告",  # 公告id
    8: "直播活动",  # 直播间id
    9: "活动稿件",
    10: "直播公告",
    11: "相簿",  # 相簿id
    12: "专栏",  # cvid
    13: "票务",
    14: "音频",  # auid
    15: "风纪委员会",  # 众裁项目id
    16: "点评",
    17: "动态",  # 动态id
    18: "播单",
    19: "音乐播单",
    20: "漫画",
    21: "漫画",
    22: "漫画",  # mcid
    33: "课程",  # 课程epid
}

video_states = {
    1: "橙色通过",
    0: "开放浏览",
    -1: "待审",
    -2: "被打回",
    -3: "网警锁定",
    -4: "撞车锁定",
    -5: "管理员锁定",
    -6: "修复待审",
    -7: "暂缓审核",
    -8: "补档待审",
    -9: "等待转码",
    -10: "延迟审核",
    -11: "视频源待修",
    -12: "转储失败",
    -13: "允许评论待审",
    -14: "临时回收站",
    -15: "分发中",
    -16: "转码失败",
    -20: "创建未提交",
    -30: "创建已提交",
    -40: "定时发布",
    -100: "用户删除",
}

media_area_codes = {
    1: "中国大陆",
    2: "日本",
    3: "美国",
    4: "英国",
    5: "加拿大",
    6: "中国香港",
    7: "中国台湾",
    8: "韩国",
    9: "法国",
    10: "泰国",
    12: "新加坡",
    13: "西班牙",
    14: "俄罗斯",
    15: "德国",
    16: "其他",
    17: "丹麦",
    18: "乌克兰",
    19: "以色列",
    20: "伊朗",
    24: "匈牙利",
    22: "克罗地亚",
    23: "冰岛",
    25: "南非",
    26: "印尼",
    27: "印度",
    30: "土耳其",
    31: "墨西哥",
    32: "委内瑞拉",
    33: "巴西",
    34: "希腊",
    35: "意大利",
    36: "挪威",
    37: "捷克",
    39: "新西兰",
    40: "智利",
    41: "比利时",
    42: "波兰",
    43: "澳大利亚",
    44: "爱尔兰",
    45: "瑞典",
    46: "瑞士",
    47: "芬兰",
    48: "苏联",
    49: "荷兰",
    51: "阿根廷",
    53: "古巴",
    54: "菲律宾",
    55: "哈萨克斯坦",
}

stream_video_codec_codes = {
    7: "AVC",
    12: "HEVC",
    13: "AV1",
}

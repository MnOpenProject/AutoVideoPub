import os

''' --------------- 使用者可能有特殊需求，可修改的参数 start --------------- '''
# 设置 无头浏览器的 无头模式
# （无头模式：即启动自动化脚本时，不会弹出浏览器显示当前代码的操作，而是在后台静默操作，是不可见的）
edge_driver_headless = False

# 请求B站稿件视频数据列表时，可指定请求页码
# （列表是分页的，每页10条数据，为了方便根据B站稿件页来确定当前查询的数据，每页请求的数据量与其保持一致）
video_request_all_page = True # 该开关设置为 True 时会逐页查询所有页码的数据,设置为 False 时，在 coolect_aid_data.py 里请求数据时，便会只查询 video_data_request_page_num 变量控制的页码的数据
video_data_request_page_num = 1
# 重新处理视频时，ffmpeg 分解视频为 .ts 切片文件时，设定的一个 .ts 文件的时长（单位：秒）
# 最好不要设置太小，否则会发现视频分解时有空的情况，重组的时候视频会出现缺帧的情况
video_ts_unit_long_s = 1
# 重新处理视频时，需要选取的视频的时间范围 '需要减去的开头时长,需要减去的结尾时长'
video_redeal_rm_ht_time_long = '00:00:00,00:00:07' #'00:00:00,00:00:10'
# 下载视频时，是否排除已上传的视频
is_download_uploaded_video = False
# 分解和重组视频时，是否排除已上传的视频(可在全局配置脚本里 common_config.py 根据自己的情况进行修改控制)
is_splitcombine_uploaded_video = False
# 上传视频时，默认使用的[话题] (若需要设置多个，则逗号隔开即可（一定要用英文格式的逗号），比如 游戏,影视)
upload_default_topics = '游戏'

''' --------------- 使用者可能有特殊需求，可修改的参数 end --------------- '''

# B站接口请求时需要用到的 headers
bilibili_request_headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Host': 'member.bilibili.com',
    'Cookie': ''
}

# 小红书接口请求时需要用到的 headers
xiaohongshu_request_headers = {
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',
    'Host': 'creator.xiaohongshu.com',
    'Cookie': ''
}

# 当前脚本所在根目录
__CURPATH__ =  str(os.path.abspath(os.path.dirname(__file__))).replace('\\','/')

# 输出到日志文件
logs_out_dir = f'{__CURPATH__}/logs'

# B站 cookie 文本
cookie_txt_path = f'{__CURPATH__}/b_cookie.txt'
# 小红书 cookie 文本
# 第一行存的是 cookie 的完整字符串
# 后面几行存的是 从浏览器里读取出来的 cookie json 对象 item（这是为了方便进入 小红书 网站时，直接把cookie填入浏览器，就不用每次都重复登录了）
cookie_xiaohongshu_txt_path = f'{__CURPATH__}/xhs_cookie.txt'

# 个人信息数据脚本（在 .gitignore 里忽略上传，每次执行代码前必会先检查此脚本，不存在则创建，其中内容必须填写完整，否则程序不会继续）
personal_info_py_name = 'personal_info'
personal_info_path = f'{__CURPATH__}/{personal_info_py_name}.py'

# ffmpeg 下载完成后，解压到某个目录下，这里配置好 ffmpeg 的 bin 目录
# ffmpeg release 包官网下载地址(找到 release builds 下载 ffmpeg-release-essentials.zip 文件)：https://www.gyan.dev/ffmpeg/builds/
ffmpeg_bin_dir = 'C:/ffmpeg-5.0-essentials_build/bin'

# 这个目录下存放下载时要排除的视频title列表（不用下载，当然也就不会被上传到别的平台上）
# （初次使用的时候该目录下的文本内容一定是空的，若需要排除某些视频，则可以先请求 aid 之后得到了 request_video_all/request_remember.txt 这个文本后，从中复制出想要排除的视频title）
video_download_exclude_dir = f'{__CURPATH__}/video_exclude'
video_download_exclude_txt = f'{video_download_exclude_dir}/video_exclude.txt'


# 从B站上下载的视频原始文件
download_file_dir = f'{__CURPATH__}/video_flv'
# 从B站上下载后首次转为MP4的原始文件
covert_file_dir = f'{__CURPATH__}/video_mp4'

# ffmpeg 的 release 包的bin目录
ffmpeg_bin_dir = 'C:/ffmpeg-5.0-essentials_build/bin'

tsfiles_root_dir = f'{__CURPATH__}/video_tsfiles'
video_new_dir = f'{__CURPATH__}/video_new_mp4'

# 每次请求 aid 数据时，会把所有请求的视频的 title 都记录到这个目录下
request_all_video_remember_dir = f'{__CURPATH__}/request_video_all'
# 每次请求 aid 数据时，会把所有请求的视频的 title 都记录到这个文件里
request_remember_txt_name = 'request_remember'
# 每次请求 aid 数据时，会把所有请求的视频的 其他详细数据(比如 描述、动态等) 都记录到这个文件里，方便后面直接获取对应视频的详细数据
request_remember_data_name = 'request_data_remember'
# 每次请求 aid 数据时，也会把所有的视频的相关数据整理成一份配置（json 格式），存储到该目录下，然后在重新处理视频时(掐头去尾这类操作)，会从这里读取相应的配置参数
video_redeal_config_dir = f'{__CURPATH__}/video_redeal_config'

# 从B站上下载的视频封面图片存储目录
video_cover_from_bili_dir = f'{__CURPATH__}/video_cover_from_bili'
# 存放一份视频上传菜单的目录，上传视频时会根据该菜单文本中的顺序进行依次上传
video_upload_menu_dir = f'{__CURPATH__}/video_upload_menu'
# 上传到小红书平台时的菜单文本名称
video_upload_menu_xiaohongshu_txt_name = 'xiaohongshu_menu'

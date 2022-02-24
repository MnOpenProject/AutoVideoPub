import os
from auto_clip_video_byandroid.module_root import __MODULEROOTPATH__ as __VIDEOSOURCEROOTPATH__
from auto_clip_video_byandroid.config.dir_config import video_collection_prefix as autoclip_video_collection_prefix,video_transition_prefix as autoclip_video_transition_prefix

# 当前模块的文件夹名称，动态引入脚本的地方会用到
cur_module_name = 'video_english_ocr'

# 当前脚本所在根目录
__CURPATH__ =  str(os.path.abspath(os.path.dirname(__file__))).replace('\\','/')

# 输出到日志文件
logs_out_dir = f'{__CURPATH__}/logs'

# ffmpeg 下载完成后，解压到某个目录下，这里配置好 ffmpeg 的 bin 目录
# ffmpeg release 包官网下载地址(找到 release builds 下载 ffmpeg-release-essentials.zip 文件)：https://www.gyan.dev/ffmpeg/builds/
ffmpeg_bin_dir = 'C:/ffmpeg-5.0-essentials_build/bin'

# 视频材料来源目录
# (该项目是对 auto_clip_video_byandroid/video/ 下视频的二次加工，因为只有这样才能算是自制视频，简单的分段就算拼接也只能算转载)
video_source_dir = f'{__VIDEOSOURCEROOTPATH__}/video'

# 集锦视频前缀：
# 集锦的配置文件与其他配置文件有所不同，文件的命名必须以 collection 开头，后续功能开发将以此开头进行识别是否为集锦配置文件
video_collection_prefix = autoclip_video_collection_prefix

# 过场视频前缀
# 过场视频前缀一定要用 transition 开头，这样程序里会以此进行过滤
video_transition_prefix = autoclip_video_transition_prefix

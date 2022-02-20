from auto_clip_video_byandroid.module_root import __MODULEROOTPATH__

# 存放 在自动化操作<必剪 app>时，针对指定视频的特殊剪辑操作的脚本目录
video_action_dir = f'{__MODULEROOTPATH__}/video_action'

# 集锦视频前缀：
# 集锦的配置文件与其他配置文件有所不同，文件的命名必须以 collection 开头，后续功能开发将以此开头进行识别是否为集锦配置文件
video_collection_prefix = 'collection'

# 过场视频前缀
# 过场视频前缀一定要用 transition 开头，这样程序里会以此进行过滤
video_transition_prefix = 'transition'
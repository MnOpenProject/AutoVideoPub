''' 把 /words_translations_whole_video_dir 目录下的单词视频合并成一个视频的数据配置文档 '''
from .module_root import __MODULEROOTPATH__

# 文件生成统一放置的目录（不要改动，除非想修改代码逻辑）
eng_study_daily_read_dir = f'{__MODULEROOTPATH__}/eng_study_daily_read'
# 单词所在目录（不要改动，除非想修改代码逻辑）
words_whole_videos_dir = f'{eng_study_daily_read_dir}/words_translations_whole_video_dir'
# 合并后的视频存储目录（不要改动，除非想修改代码逻辑）
combine_words_whole_videos_dir = f'{eng_study_daily_read_dir}/combine_words_whole_videos_dir'

# ******************************************* 以下配置可根据自己的需求进行更改 ********************************************************

# 合并后的视频保存名称（根据自行需要进行更改，若文件名已存在，则终端会提示是否替换）
combine_words_video_file_name = '2022_02_08to2022_03_08'

# 要合并的单词视频名称列表（对应上面的 words_whole_videos_dir 目录下的文件名）
# 根据自行需要，写入要合并的单词视频名称
words_whole_videos = [
    '2022_02_08',
    '2022_03_08'
]

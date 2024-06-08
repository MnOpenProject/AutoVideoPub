import platform
from .module_root import __MODULEROOTPATH__

# 是否生成 .log 文件
out_log_file = False

# ffmpeg 的 release 包的bin目录
# mac 安装 ffmpeg 参考资料：https://www.jianshu.com/p/f6990aee6c7f
macos_ffmpeg_bin_dir = '' # macos 需要通过 brew install ffmpeg 进行安装，好像会自动配置环境变量 path，如果使用时发现没有成功，则手动通过 vim ~/.bash_profile 配置 path
win_ffmpeg_bin_dir = 'C:/ffmpeg-5.0-essentials_build/bin' # TODO：这里请自行配置自己 ffmpeg 的 path 路径，此值仅供参考而已
ffmpeg_bin_dir = win_ffmpeg_bin_dir if 'windows' in platform.platform().lower() else macos_ffmpeg_bin_dir

# 申请的有道 API 相关参数
# TODO:以下注释中均为案例参考而已，请自行申请后，写入此处
youdao_api_daily_eng = {
    "APP_KEY": "", # "76366c365a7b565c"
    "APP_SECRET": "", # "6jsiC8sZEO0P641tdTPTUVhLwH5ARWnG",
    "header": {
        "Content-Type": "" # "application/x-www-form-xxxxx"
    }
}

# 从文章中提取单词会根据这里设定的字符数进行提取，凡是长度低于这个数值的单词都不会进行提取
difficult_word_len_min = 6

# 字符集存放目录（字符集 即 字体的样式，比如 宋体之类的）
fonts_dir = f'{__MODULEROOTPATH__}/fonts'
# 【可根据自行需求更改】字符集文件名称，可以自行在网络上下载字符集文件，然后放到上面的 /fonts 目录下
# 注：目前实际测下来，并非支持所有的字符集，有的会导致无法绘制（如果更换了字符集之后，发现在合成视频的步骤里发生问题，并没有输出合成视频，就说明并不支持当前设置的字符集）

# 【 英语音标字符集】用于渲染 英语音标的 字符集（切勿改动，这个字符集不太好找，换错了就会无法渲染出音标中的特殊符号，就会出现乱码）
eng_symbol_ttc_file_full_name = 'arial.ttf'
# 【英文字符集】（英文字符集是往往不会包含中文字符集的，所以英文字符集不要用在中文字符集上）
eng_ttc_file_full_name = 'repairbold.ttf' # 'sitkab.ttc' # 宋体：'simsun.ttc'
# 【中文字符集】
zh_ttc_file_full_name = 'GenRyuMinTWBold.ttf' #  演示夏行楷 'xiaxingkai.ttf'  # 'msyh.ttc' # 宋体：'simsun.ttc'

# 视频背景图片存储目录
screen_bg_image_dir = f'{__MODULEROOTPATH__}/bg_dir'
# 视频背景图片名称(包含后缀名)，若需要修改，请把要修改的图片放到上面的 /bg_dir 目录下
screen_bg_image_full_name = 'demo.jpg'

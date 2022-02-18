''' 下载自己<B站 稿件管理 已审核>的投稿视频，并自动处理后，自动上传到自己账号登录的其他视频平台上 '''
import os,importlib
from .collect_aid_data import collect_aid_data
from .download_video import download_and_convert2mp4,download_video,video_flv_convert2mp4,create_xiaohongshu_upload_video_menu
from .upload2xiaohongshu import upload2xiaohongshu
from .redeal_video import split_video_to_tsfiles,recombine2new,redeal_video
from .common_config import download_file_dir,covert_file_dir,video_download_exclude_dir,video_download_exclude_txt,personal_info_path,cookie_txt_path
from .common_util import is_int_str,input_selection,get_video_name_by_title,check_personal_info,clear_all_folderfiles_of_autocreate
from .common_web_auto import check_bilibli_cookie_and_create

def init_dir():
    # 初始化下载时要排除的视频目录和文件
    if not os.path.exists(video_download_exclude_dir):
        os.makedirs(video_download_exclude_dir)
    if not os.path.exists(video_download_exclude_txt):
        fp = open(video_download_exclude_txt,"w",encoding="utf-8")
        fp.write('')
        fp.close()
    # 初始化下载和转换所需目录
    if not os.path.exists(download_file_dir):
        os.makedirs(download_file_dir)
    if not os.path.exists(covert_file_dir):
        os.makedirs(covert_file_dir)

def main_func():
    init_dir()
    if not check_personal_info():
        print(f'---- 【*】请先在该脚本中填写完整其中的个人参数，否则程序无法执行，脚本位置如下：\n{personal_info_path}')
        return
    # 检查本地存储的B站的 cookie 是否有效，无效则会自动获取新的并存入本地
    if not check_bilibli_cookie_and_create():
        print(f'---- 【*】请确保 B站cookie 已存储到本地，本地 cookie 文本位置如下：\n{cookie_txt_path}')
        return
    hints = [
        '[0] - 视频标题转为视频文件名称\n    |-- （这个选项用于测试 视频标题 转 文件名 的功能）\n    |-- （由于文件存在命名规则，请求的视频标题需要进行处理后才能用于文件名）',
        '[1] - 请求<B站 我的稿件>列表数据，把视频标题输出到文本里，便于查看',
        '[2] - 下载<B站 我的稿件>列表的视频',
        '[3] - video_flv中的选择文件转MP4',
        '[4] - 下载并直接转MP4 -- 即 联合步骤 [2]->[3]',
        '[5] - 分解 video_mp4/ 目录下的视频为 .ts 切片文件\n    |-- （通过 ffmpeg 分解成 .ts 切片文件）',
        '[6] - 重组 video_mp4/ 目录下的视频 -- 进行掐头去尾再重组成新的MP4文件\n    |-- （掐头去尾后，重组成新的 .mp4 文件）\n    |-- （全局的重组配置参数在 /common_config.py 脚本的顶部，若有需要可自行修改）',
        '[7] - 重新处理 video_mp4/ 目录下的视频：分解原始视频，掐头去尾后，再重组 -- 即联合步骤 [5]->[6]\n    |-- （全局的重组配置参数在 /common_config.py 脚本的顶部，若有需要可自行修改）',
        '[8] - 生成一份针对《小红书 平台》的上传视频的配置文件\n    |-- （这部操作请一定要最起码保证需要上传的视频已经下载完成的前提下执行）',
        '[9] - [*]自动下载并生成新视频 -- 即 联合步骤：[4]->[7]\n    |-- （备注：该过程结束后，会生成一份视频上传菜单，若需要自定义上传顺序，或自定义上传参数，请先更改该视频菜单后，再执行上传操作）',
        '[10] - [*]上传 video_mp4/ 目录下的所有视频到<小红书平台>',
        '[11] - B站视频搬运到<小红书平台> -- 即 联合步骤 [8]-[9]\n    |-- （若只需要使用默认的上传顺序操作的，可直接用该项功能，若想要自定义上传顺序，请使用 [8] 和 [9]）',
        '[108] - 移除所有自动创建的文件夹和文件(谨慎使用，删除后视频需要重新下载)\n    |-- （会移除一些自动创建的目录和文件，会使得整个项目回到几乎初始时的状态（但不会清理掉 video_exclude/, video_upload_menu/, video_redeal_config/ 这类记录型的文件）\n    |-- （会移除的目录有：logs/, request_video_all/, video_flv/, video_mp4/, video_tsfiles/, video_new_mp4/, personal_info/, /b_cookie.txt, /xhs_cookie.txt）'
    ]
    print('[*] - 选择你要的操作（默认项：[1]）：\n-----【标记[*]星号的是推荐操作】-----')
    [print(i) for i in hints]
    selection = input_selection()
    if selection == 0:
        print('输入视频标题：')
        video_title = input()
        video_file_name = get_video_name_by_title(video_title)
        print(f'输出的视频文件名为：{video_file_name}')
    if selection == 1:
        collect_aid_data()
    if selection == 2:
        download_video()
    if selection == 3:
        video_flv_convert2mp4()
    if selection == 4:
        download_and_convert2mp4()
    elif selection == 5:
        split_video_to_tsfiles()
    elif selection == 6:
        recombine2new()
    elif selection == 7:
        redeal_video()
    elif selection == 8:
        create_xiaohongshu_upload_video_menu()
    elif selection == 9:
        download_and_convert2mp4()
        redeal_video()
    elif selection == 10:
        upload2xiaohongshu()
    elif selection == 11:
        download_and_convert2mp4()
        redeal_video()
        upload2xiaohongshu()
    elif selection == 108:
        clear_all_folderfiles_of_autocreate()
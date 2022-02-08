''' 视频集锦制作：在 video/ 下选择多个分段视频，然后合并成一个集锦视频 '''

from globalvars import __ROOTPATH__
from datetime import datetime
import os
from .combine_video_by_ffmpeg import combine_video_by_ffmpeg

# 自定义的 log 输出方法
cur_timestamp = str(datetime.now().timestamp()).replace('.','')
def log_print(str_content):
    # 在终端打印
    print(str_content)
    # 输出到日志文件
    logs_dir = '{0}auto_clip_video_byandroid/logs'.format(__ROOTPATH__)
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    # _log 前面改成当前的脚本文件名称
    f_path = '{0}/auto_video_collection_{1}.log'.format(logs_dir,cur_timestamp)
    # 写入文本
    fp = open(f_path,"a",encoding="utf-8")
    fp.write('{0}\n'.format(str_content))  
    fp.close()

# 将本次选择项记录到本地
collection_remember_dir = '{0}auto_clip_video_byandroid/collection_remember'.format(__ROOTPATH__)
def write_selection_to_remember(selection_idx_list):
    if not os.path.exists(collection_remember_dir):
        os.makedirs(collection_remember_dir)
    f_path = remember_file_path
    str_content = ''
    for i,selected_idx in enumerate(selection_idx_list):
        # selection_idx_list 记录的都是数组的真实索引值（从0开始），而使用者输入的是从1开始的，所以记录数据时要+1
        if i == 0:
            str_content += f'{selected_idx+1}'
        else:
            str_content += f',{selected_idx+1}'
    # 写入文本
    fp = open(f_path,"a",encoding="utf-8")
    fp.write('{0}\n'.format(str_content))  
    fp.close()

# 读取最近的 N 条输入记录
def read_selection_remember():
    last_num = 3
    f_path = remember_file_path
    if not os.path.exists(f_path):
        log_print('{} --> 不存在'.format(f_path))
        return []
    line_list = []
    for remember_line_ in open(f_path):
        remember_line = remember_line_.replace('\r','').replace('\n','')
        line_list.append(remember_line)
    if len(line_list) <= last_num:
        return line_list
    return line_list[len(line_list)-last_num,len(line_list)]

def ask_video_selection():
    video_selection = []
    video_dir = '{0}auto_clip_video_byandroid/video'.format(__ROOTPATH__)
    if not os.path.exists(video_dir):
        log_print('当前没有任何视频片段可以制作集锦！！！')
        return video_selection
    log_print('\n------------------------ 以下是现有的视频片段 -----------------------------')
    # 收集本地已存在的视频文件(存放的是文件的完整绝对路径)
    video_paragraph_file_list = []
    # 读取 video\ 目录下的所有视频文件
    selection_idx = 1
    video_show_dir_1_list = os.listdir(f'{video_dir}')
    for video_show_floder_1 in video_show_dir_1_list:
        video_show_dir_2_path = f'{video_dir}/{video_show_floder_1}'
        video_show_dir_2_list = os.listdir(video_show_dir_2_path)
        for video_show_floder_2 in video_show_dir_2_list:
            video_show_dir_fullfiles_path = f'{video_show_dir_2_path}/{video_show_floder_2}/fullfiles'
            video_show_dir_fullfiles_list = os.listdir(video_show_dir_fullfiles_path)
            for video_show_file_floder in video_show_dir_fullfiles_list:
                video_file_full_name = f'{video_show_file_floder}{video_file_Format}'
                video_show_file_path = f'{video_show_dir_fullfiles_path}/{video_show_file_floder}/{video_file_full_name}'
                # 若视频文件存在，则进行收集
                if os.path.exists(video_show_file_path):
                    video_show_file_path = video_show_file_path.replace('\\','/')
                    video_paragraph_file_list.append(video_show_file_path) # 收集到数组中
                    log_print(f'[{selection_idx}] - {video_file_full_name} --（绝对路径）--> {video_show_file_path}')
                    selection_idx += 1

    log_print('\n---------- 请输入要组合成集锦的视频片段序号（逗号隔开，如 5,3,1,...）： ----------')
    log_print('（提示：序号可以重复，如 5,1,2,1,3; 也就是说可以自己放一个用于过渡的视频片段，然后自行组合，避免不同的视频之间变换僵硬）')
    # 读取近期输入过的组合编号记录，以便重复使用，也可以自己去记录文件中查阅所有记录
    input_history = read_selection_remember()
    if len(input_history) > 0:
        log_print('【*】近期输入记录如下：')
        for r_i,remember in enumerate(input_history):
            log_print(f'[{r_i}] - {remember}')
        log_print('-----------------------\n')
    try:
        video_paragraph_file_list_end_idx = len(video_paragraph_file_list) - 1
        selection_input = input()
        selection_idx_list = [int(i) - 1 for i in selection_input.split(',') if (int(i)-1) >= 0 and (int(i)-1) <= video_paragraph_file_list_end_idx]
        log_print('----- 已选择：')
        # 将本次选择项记录到本地
        write_selection_to_remember(selection_idx_list)
        for selection_idx in selection_idx_list:
            selected_video_file_path = video_paragraph_file_list[selection_idx]
            video_selection.append(video_paragraph_file_list[selection_idx])
            # 输出告知当前已选择的视频片段
            log_print(f'[{selection_idx+1}] --（绝对路径）--> {selected_video_file_path}')
    except Exception as ex:
        log_print('输入值不合法，请按照提示规范进行输入')
        return []
    log_print(f'\n----- video_selection:\n {video_selection}')
    return video_selection

# 将已选择的视频分段文件合并成一个完整的视频文件
def combine_selection_to_video(video_selection):
    # 开始合并并输出视频文件
    videoRoot = f'{__ROOTPATH__}auto_clip_video_byandroid/video'
    for cfg in video_upload_config_list:
        # 创建文件的输出目录
        output_path_1 =  f'{videoRoot}/{cfg["first_name"]}'
        if not os.path.exists(output_path_1):
            os.makedirs(output_path_1)
        output_path_2 =  f'{output_path_1}/{cfg["second_name"]}'
        if not os.path.exists(output_path_2):
            os.makedirs(output_path_2)
        output_path_3 =  f'{output_path_2}/fullfiles'
        if not os.path.exists(output_path_3):
            os.makedirs(output_path_3)
        output_file_name = f'{cfg["second_name"]}_{cfg["episode_list"]}_{cfg["paragraph_serials"]}'
        output_path_4 =  f'{output_path_3}/{output_file_name}'
        if not os.path.exists(output_path_4):
            os.makedirs(output_path_4)
        
        # 进行合并输出
        video_file_dir = output_path_4
        video_file_list = video_selection
        output_file_full_name = f'{output_file_name}{video_file_Format}'
        saveFilePath = f'{output_path_4}/{output_file_full_name}'
        combine_video_by_ffmpeg(video_file_dir, video_file_list, saveFilePath, log_print)

# 制作视频集锦
def create_collection():
    video_selection = ask_video_selection()
    if len(video_selection) > 0:
        combine_selection_to_video(video_selection)


''' 提供给外界调用的主入口函数 '''
def main_func(upload_config_module):
    global video_file_Format
    global video_show_name
    global remember_file_path
    global video_upload_config_list

    video_file_Format = upload_config_module.video_file_Format
    video_show_name = upload_config_module.second_name # 这将作为 记录 使用者终端输入的 视频分段号 的记录文件的 唯一ID使用
    remember_file_path = f'{collection_remember_dir}/{video_show_name}.txt'
    video_upload_config_list = upload_config_module.video_upload_config_list

    create_collection()
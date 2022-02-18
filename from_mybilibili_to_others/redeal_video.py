''' 对 video_mp4/ 目录下的视频进行二次处理：掐头去尾（通过 ffmpeg 先分解成 .ts 切片文件，再掐头去尾后，重组成新的 .mp4 文件） '''
''' 输出到 video_new_mp4/ 目录下 '''

import os
from .common_config import ffmpeg_bin_dir,covert_file_dir,tsfiles_root_dir,video_new_dir,video_redeal_rm_ht_time_long
from .common_util import del_files,get_duration_from_ffmpeg,log_print as cm_log_print,read_redeal_config
from .split_tsfiles_by_ffmpeg import video_split_tsfiles_by_ffmpeg
from .combine_ts_by_ffmpeg import combine_ts_by_ffmpeg

def log_print(content_str):
    cm_log_print(content_str,'upload2xiaohongshu')

def split_video_to_tsfiles():
    video_file_dir = covert_file_dir
    video_files = os.listdir(video_file_dir)
    if len(video_files) > 0:
        for video_file_full_name in video_files:
            # video_file_path = f'{video_file_dir}/{video_file_name}'
            video_file_format = '.mp4'
            video_file_name = video_file_full_name.replace(video_file_format,'')
            # 先把视频分集成 .ts 切片文件
            video_split_tsfiles_by_ffmpeg(video_file_dir,video_file_name,video_file_format)

# 掐头去尾，重组 .ts 文件成 新的 .mp4 文件
def recombine2new():
    # 设置对视频剪辑后，取视频的时间范围(只收集从 开头时刻~结尾时刻 这个范围内的 .ts 切片文件进行重组合并成新的 .mp4 文件)
    rm_ht_time_long_list = video_redeal_rm_ht_time_long.split(',')
    # 默认情况下使用全局配置参数值
    rm_start_time_long = rm_ht_time_long_list[0] # 要裁剪去掉的 开头时长
    rm_end_time_long = rm_ht_time_long_list[1] # 要裁剪去掉的 结尾时长
    
    tsfiles_video_dir_list = os.listdir(tsfiles_root_dir) # video_tsfiles/ 目录下的子目录(节目文件夹)列表
    if len(tsfiles_video_dir_list) > 0:
        for video_name_dir in tsfiles_video_dir_list:
            # 先获取原始视频文件的时长，从而通过减去 rm_end_sec_total(要裁剪去掉的视频结尾时长) 来计算出 当前要收集的 .ts 切片文件的 结束时刻
            source_video_path = f'{covert_file_dir}/{video_name_dir}.mp4'
            print(f'原始文件：{source_video_path}')
            # 必须确保原始视频文件存在的前提下，才进行重组，避免误删除了原始文件的情况下
            if os.path.exists(source_video_path):                
                # 先根据当前视频title，尝试去读取配置参数，若读取到的 rm_header_tail_time_long 参数值为空，那么 rm_start_time_long 和 rm_end_time_long 默认使用全局的参数值
                redeal_json = read_redeal_config(video_name_dir)
                if not redeal_json == None and not redeal_json['rm_header_tail_time_long'] == '':
                    rm_ht_time_long_list = redeal_json['rm_header_tail_time_long'].split(',')
                    rm_start_time_long = rm_ht_time_long_list[0] # 要裁剪去掉的 开头时长
                    rm_end_time_long = rm_ht_time_long_list[1] # 要裁剪去掉的 结尾时长
                
                log_print('------- 开始重组成新视频 ------')
                log_print(f'要裁剪去掉的 开头时长 为: {rm_start_time_long}')
                log_print(f'要裁剪去掉的 结尾时长 为: {rm_end_time_long}')

                # 计算要 秒级 开始时长
                start_time_list = rm_start_time_long.split(':')
                start_time_h = int(start_time_list[0]) # 时
                start_time_m = int(start_time_list[1]) # 分
                start_time_s = int(start_time_list[2]) # 秒
                start_sec_total = start_time_h * 60 * 60 + start_time_m * 60 + start_time_s # 计算总秒数
                # 计算要删除的 秒级 结束时长
                end_time_list = rm_end_time_long.split(':')
                end_time_h = int(end_time_list[0]) # 时
                end_time_m = int(end_time_list[1]) # 分
                end_time_s = int(end_time_list[2]) # 秒
                rm_end_sec_total = end_time_h * 60 * 60 + end_time_m * 60 + end_time_s # 计算总秒数

                tsfiles_dir = f'{tsfiles_root_dir}/{video_name_dir}'
                ts_duration_total_sec = 0 # 记录直到当前遍历到的 .ts 切片文件的总时长（以此来判定收集合适的 .ts 文件）
                # 开始遍历 .ts 切片文件并收集
                tsfile_list = os.listdir(tsfiles_dir)
                source_video_duration_total_s = get_duration_from_ffmpeg(source_video_path)
                # 保留2位小数
                source_video_duration_total_s = round(float(source_video_duration_total_s),2)
                end_sec_total = source_video_duration_total_s - rm_end_sec_total
                collect_tsfile_list = []
                if len(tsfile_list) > 0:
                    for tsfile_name in tsfile_list:
                        tsfile_path = f'{tsfiles_dir}/{tsfile_name}'
                        duration_s = get_duration_from_ffmpeg(tsfile_path)
                        # 保留2位小数
                        duration_s = round(float(duration_s),2)
                        # 累计当前遍历的 .ts 切片文件总时长
                        ts_duration_total_sec += duration_s
                        if ts_duration_total_sec >= start_sec_total and ts_duration_total_sec <= end_sec_total:
                            collect_tsfile_list.append(tsfile_path)
                    saveFileDir = video_new_dir
                    saveFilePath = f'{saveFileDir}/{video_name_dir}.mp4'
                    combine_ts_by_ffmpeg(tsfiles_dir,collect_tsfile_list,saveFileDir, saveFilePath, log_print)
                    
def init_dirs():
    if not os.path.exists(video_new_dir):
        os.makedirs(video_new_dir)

def redeal_video():
    init_dirs()
    # 先分解视频
    split_video_to_tsfiles()
    # 再掐头去尾，重组 .ts 文件成 新的 .mp4 文件
    recombine2new()
    
''' 把 video_mp4/ 目录下的视频分解成 .ts 视频切片文件，输出到 video_tsfiles/ 目录下 '''
# ffmpeg将 视频文件 (比如.mp4)分解为ts
# 参考：https://www.cnblogs.com/c-x-a/p/14076911.html

import os
from .common_config import ffmpeg_bin_dir,tsfiles_root_dir
from .common_util import del_files

# video_dir：要分解的视频文件所在目录 如 D:\spidervideo\downloadvideo\dsns\dsns1\fullvideo
# video_file_name：要分解的视频文件名 如 dsns1_01
# video_format：要分解的视频文件类型扩展名 如 .mp4
# tsfiles_out_dir：分解后 .ts 文件的输出目录 如 D:\spidervideo\downloadvideo\dsns\dsns1\tsfiles_local
# ts_unit_long_s：分解后每个 .ts 视频文件的时长控制（单位：秒）但实际拆分出来的并不一定，会有偏差，比如 虽然设置了3秒，但实际有的 .ts 视频文件会是2秒
def video_split_tsfiles_by_ffmpeg(video_dir,video_file_name,video_format,ts_unit_long_s=3):
    # 切片生成m3u8列表命令：
    # ffmpeg -i 1.mp4 -c:v libx264 -c:a copy -f hls -threads 8 -hls_time 3 -hls_list_size 12 index.m3u8
    # C:/ffmpeg-5.0-essentials_build/bin/ffmpeg -i D:\spidervideo\downloadvideo\tmp\fullfiles\dsns1_01_01.mp4 -c:v libx264 -c:a copy -f hls -threads 8 -start_number 1 -hls_time 3 -hls_list_size 0 D:\spidervideo\downloadvideo\tmp\tsfiles_local\index.m3u8
    # 使用FFmpeg命令进行hls切片，得到的ts文件时长不准确，解决方案参考：https://blog.csdn.net/u014552102/article/details/103302731
    # 产生上述现象的原因是：ts文件的切割还跟视频的GoP大小(两个I帧之间的间隔）有关，并不是指定1秒切一个ts文件就能保证1秒切一个ts文件的。任何一个视频流在播放端要能获取到完整的GoP才能播放，所以一个ts文件所实际包含的时间是GoP的整数倍
    # 解决方法：
    # 知道问题产生的原因就好办了，只要我们在FFmpeg命令中设置I帧间隔就可以了。我们将切片的命令修改为如下命令：
    # C:/ffmpeg-5.0-essentials_build/bin/ffmpeg -i D:\spidervideo\downloadvideo\tmp\fullfiles\dsns1_01_01.mp4 -force_key_frames "expr:gte(t,n_forced*3)" -c:v libx264 -c:a copy -f hls -threads 8 -start_number 1 -hls_time 3 -hls_list_size 0 D:\spidervideo\downloadvideo\tmp\tsfiles_local\index.m3u8
    # 其中，参数-force_key_frames "expr:gte(t,n_forced*3)"表示强制每3秒一个关键帧

    # # 若输出文件夹存在，则清空其中的所有文件
    # if os.path.exists(tsfiles_out_dir):
    #     del_files(tsfiles_out_dir)
    # 若输出文件夹不存在，则创建
    if not os.path.exists(tsfiles_root_dir):
        os.makedirs(tsfiles_root_dir)
    
    # 为每个视频创建一个独立的文件夹，放置对应的 .ts 视频切片文件
    tsfiles_out_dir = f'{tsfiles_root_dir}/{video_file_name}'
    if not os.path.exists(tsfiles_out_dir):
        os.makedirs(tsfiles_out_dir)
    else:
        # 若已存在，则删除上一次分解的所有 .ts 视频切片文件
        del_files(tsfiles_out_dir)
    
    # ffmpeg 分解视频时，会先生成该文件，然后再根据该文件逐个分解出 .ts 文件，所以这个文件的输出目录也是控制 .ts 文件的输出目录
    out_indexfile_path = f'{tsfiles_out_dir}/index.m3u8'
    # ts_unit_long_s = 3 # 分解后每个 .ts 视频文件的时长控制（单位：秒）但实际拆分出来的并不一定，会有偏差，比如实际有的 .ts 视频文件会是2秒
    cmd_str = f'{ffmpeg_bin_dir}/ffmpeg -i {video_dir}/{video_file_name}{video_format} -force_key_frames "expr:gte(t,n_forced*{ts_unit_long_s})" -c:v libx264 -c:a copy -f hls -threads 8 -start_number 1 -hls_time {ts_unit_long_s} -hls_list_size 0 {out_indexfile_path}'
    print(' --------分解指令------------\n')
    print(cmd_str)
    os.system(cmd_str)

    # 指令完成后，删除 index.m3u8 文件
    os.remove(out_indexfile_path)
    # 对所有生成的 .ts 文件进行重命名，去除文件名中的 index 前缀
    # 由于生成的 .ts 文件名都会带有跟 index.m3u8 一样的前缀（这并不符合该项目的使用规则），如 index1.ts,index2.ts,...
    tsfile_name_list = os.listdir(tsfiles_out_dir)
    for ts_name in tsfile_name_list:
        ts_file_path_source = f'{tsfiles_out_dir}/{ts_name}'
        ts_name_new = ts_name.replace('index','')
        ts_file_path_target = f'{tsfiles_out_dir}/{ts_name_new}'
        os.rename(ts_file_path_source,ts_file_path_target)
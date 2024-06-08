''' 图片转为视频 '''

import os,shutil
from .config import ffmpeg_bin_dir
from .common.common_util import debug_input,del_files
from moviepy.editor import concatenate_videoclips,VideoFileClip


# 将一批图片转换为一份视频文件（.mp4）
def img_to_video(imgs_dir, out_video_dir,out_video_path,file_name,fps=25,duration=10,img_format='.png',video_size=(1080,720)):
    # params imgs_dir: 图片目录下的图片命名必须遵循该规则 -- f'{file_name}_{num}.jpg' 这里的 num 必须是从1开始逐一递增的编号
    # params fps = 1 # fps 决定使用多少张图片作为1帧（如果设置为10，则1帧 [这里1帧时长为1秒]），希望生成的视频时长N秒，则需要N张图片 (比如 fps_unit_img_count = 20 # 1帧所需的图片数量是20，经实际实验测试，1帧使用的图片多一些，最终形成的播放时越细腻)
    # params video_size: 【*****】 【非常重要】这个参数非常重要，输出视频的分辨率尺寸(宽x高)，宽和高的值一定要是2的倍数

    img_root = f'{imgs_dir}/{file_name}_%d{img_format}'
    out_video = f'{out_video_path}'

    # print(f'img_root = {img_root}')
    print(f'out_video = {out_video}')

    source_img_path_list = []
    source_img_filefullname_list = os.listdir(imgs_dir)
    for img_full_name in source_img_filefullname_list:
        source_img_path = f'{imgs_dir}/{img_full_name}'
        source_img_path_list.append(source_img_path)

    print('把要合并的所有图片文件依次排列好的写入到一个 txt 文件中----------------------------')
    filelist_path = f'{out_video_dir}/combinelist.txt'
    print(f'video_file_list = {source_img_path_list}')
    write_filelist_into_txt(filelist_path,source_img_path_list)

    ffmpeg_bin_dir_ = f'{ffmpeg_bin_dir}/' if not ffmpeg_bin_dir == '' else ''
    # 下面的指令中的这些参数非常关键 -s 1080x720 -pix_fmt yuv420p -c:v libx264 若不设置就会遇到下面贴上的问题，其中的 -s 1080x720 信息是输出视频的分辨率，宽高一定要是2的倍数，否则ffmpeg合成的视频会有损坏，无法解码
    # 使用ffmpeg工具想把图片生成视频，发现用windows media player无法播放（移动设备里也无法正常播放）,暴风影音和PotPlayer可以播放
    # 参考链接：https://www.jianshu.com/p/a49f2236df9a
    # FFmpeg视频解码中的YUV420P格式 -- 参考资料：https://blog.csdn.net/ericbar/article/details/80505658
    # FFmpeg中的libx264编码流程 -- 参考资料：https://www.jianshu.com/p/cff67a47b504
    command = f"{ffmpeg_bin_dir_}ffmpeg -r {fps} -t {duration} -i {img_root} -s {video_size[0]}x{video_size[1]} -pix_fmt yuv420p -c:v libx264 {out_video}"
    print('***************************************')
    print(command)
    print('***************************************')
    # call(command.split())
    os.system(command)

    # 合并完成后，清理掉图片，因为图片太占空间了，用完了要清理掉，再说了下次合成视频这些图片还会自动生成
    del_files(imgs_dir)
    if os.path.exists(imgs_dir):
        os.rmdir(imgs_dir)

# ------------ 这套方案保留在这里进行，已暂时废弃，因为绘制出来的文字区域有背景色，且各种尝试和查询资料都不知如何直接控制合成视频的时长 start -------------------------------------------

# import cv2
# from cv2 import VideoWriter_fourcc
# from subprocess import call
# # 将一批图片转换为一份视频文件（.mp4）
# def img_to_video(imgs_dir,out_video_path,file_name,img_size=(640, 480),fps=1):
#     # params imgs_dir: 图片目录下的图片命名必须遵循该规则 -- f'{file_name}_{num}.jpg' 这里的 num 必须是从1开始逐一递增的编号
#     # params fps = 1 # fps 决定使用多少张图片作为1帧（如果设置为10，则1帧 [这里1帧时长为1秒]），希望生成的视频时长N秒，则需要N张图片 (比如 fps_unit_img_count = 20 # 1帧所需的图片数量是20，经实际实验测试，1帧使用的图片多一些，最终形成的播放时越细腻)
#
#     img_root = f'{imgs_dir}'
#     out_avi = f'{out_video_path.strip(".mp4")}.avi'
#
#     fourcc = VideoWriter_fourcc(*"MJPG")  # 支持jpg
#     videoWriter = cv2.VideoWriter(out_avi, fourcc, fps, img_size)
#     im_names = os.listdir(img_root)
#     print(len(im_names))
#     for im_idx in range(len(im_names)):
#         img_path = f'{img_root}/{file_name}_{im_idx+1}.jpg' # 从图片文件下按照这里定好的命名规则进行读取图片，如果报错很有可能是图片命名规则不对
#         print(img_path)
#         frame = cv2.imread(img_path)
#         frame = cv2.resize(frame, img_size)
#         videoWriter.write(frame)
#
#     videoWriter.release()
#
#     # 把 .avi 文件压缩成 .mp4
#     # dir = out_root.strip(".avi")
#     # out_mp4_path = out_video_path
#     ffmpeg_bin_dir_ = ffmpeg_bin_dir if not ffmpeg_bin_dir == '' else ''
#     command = f"{ffmpeg_bin_dir_}/ffmpeg -i {out_avi} {out_video_path}"
#     call(command.split())
#     # 删除临时使用的 .avi 文件
#     if os.path.exists(out_avi):
#         os.remove(out_avi)

# ------------ 这套方案保留在这里进行，已暂时废弃，因为绘制出来的文字区域有背景色，且各种尝试和查询资料都不知如何直接控制合成视频的时长 end -------------------------------------------

# ffmpeg 将音频和视频进行合成（这与视频合并不同，音频和视频是并行的，通过使用 ffmpeg 不同的参数实现该功能）
# ffmpeg 官网：http://ffmpeg.org/download.html#build-windows
# 【注意】：使用该方案的前提是：windows 环境中已经安装好了 ffmpeg 环境，安装参考：http://www.360doc.com/content/21/0204/15/54508727_960674843.shtml
# ffmpeg 合并文件方案参考（这里选用的就是参考地址里的 <方案三>）：https://www.cnblogs.com/duanxiaojun/articles/6904878.html
# FFmpeg concat 分离器 合并文件方案
# 这种方法成功率很高，也是最好的，但是需要 FFmpeg 1.1 以上版本。先创建一个文本文件filelist.txt
def combine_audio_video_by_ffmpeg(source_audio_path:str,source_video_path:str,out_video_path:str):
    # out_video_path = f'{out_video_dir}/{file_name}.mp4'
    if os.path.exists(out_video_path):
        os.remove(out_video_path)
    ffmpeg_bin_dir_ = f'{ffmpeg_bin_dir}/' if not ffmpeg_bin_dir == '' else ''
    cmdStr = f'{ffmpeg_bin_dir_}ffmpeg -i {source_audio_path} -i {source_video_path} -acodec copy -vcodec copy {out_video_path}'
    print("CMD合成指令：{}".format(cmdStr))
    os.system(cmdStr)
    print("{}视频合成完成".format(out_video_path))

# ffmpeg 将多个视频合并成一个视频文件（.mp4）
# ffmpeg 官网：http://ffmpeg.org/download.html#build-windows
# 【注意】：使用该方案的前提是：windows 环境中已经安装好了 ffmpeg 环境，安装参考：http://www.360doc.com/content/21/0204/15/54508727_960674843.shtml
# ffmpeg 合并文件方案参考（这里选用的就是参考地址里的 <方案三>）：https://www.cnblogs.com/duanxiaojun/articles/6904878.html
# FFmpeg concat 分离器 合并文件方案
# 这种方法成功率很高，也是最好的，但是需要 FFmpeg 1.1 以上版本。先创建一个文本文件filelist.txt
def combine_videos_by_ffmpeg(source_video_path_list:list[str],out_video_path:str):
    # out_video_path = f'{out_video_dir}/{file_name}.mp4'
    if os.path.exists(out_video_path):
        os.remove(out_video_path)
    print('准备合并的文件列表----------------------------')
    # ffmpeg 合并视频之前，把要合并的所有视频文件都预先排列好的写入到一个 txt 文件中，后续会读取该文本按照此文本中记录的视频文件顺序进行合并
    print('把要合并的所有视频文件依次排列好的写入到一个 txt 文件中----------------------------')

    print(f'video_file_list = {source_video_path_list}')

    # ********************* 旧合并视频方案：由于当前的合并视频解码有问题，有些情况下视频合并后，部分视频片段的声音会变快或变慢 ***************************************
    # filelist_path = f'{out_video_path.replace(".mp4","")}_combinelist.txt'
    # write_filelist_into_txt(filelist_path,source_video_path_list)
    # # 然后通过 ffmpeg 指令合并文件
    # ffmpeg_bin_dir_ = f'{ffmpeg_bin_dir}/' if not ffmpeg_bin_dir == '' else ''
    # cmdStr = f'{ffmpeg_bin_dir_}ffmpeg -f concat -safe 0 -i {filelist_path} -qscale 0 -r 25 -y -c copy {out_video_path}'
    # print("CMD合成指令：{}".format(cmdStr))
    # os.system(cmdStr)
    # *************************************************************
    # 新合并视频方案：尝试使用 moviepy 库看能否解决上面提到的视频片段声音速度变化的问题
    # 参考资料：https://cubox.pro/web/reader/ff8080817fbf2655017fcef29f6c5552
    # 收集视频对象
    video_clips = []
    for vpath in source_video_path_list:
        vclip = VideoFileClip(vpath)
        video_clips.append(vclip)
    # 拼接视频
    final_clip = concatenate_videoclips(video_clips)
    # 生成目标视频文件
    final_clip.to_videofile(out_video_path, fps=25, remove_temp=True)
    print("{} -- 视频合成完成".format(out_video_path))
    
    # 移除合并文件时，临时使用的 filelist.txt 文件
    # if os.path.exists(filelist_path):
    #     os.remove(filelist_path)

# ffmpeg 合并视频之前，把要合并的所有视频文件都预先排列好的写入到一个 txt 文件中，后续会读取该文本按照此文本中记录的视频文件顺序进行合并
def write_filelist_into_txt(filelist_path,video_file_list):
    if os.path.exists(filelist_path):
        os.remove(filelist_path)
    str_content = ''   
    f_path = filelist_path
    for file_idx,file_path in enumerate(video_file_list):
        # 写入文本
        str_content = f"file {file_path}" if file_idx == 0 else f'{str_content}\nfile {file_path}'
    fp = open(f_path,"w",encoding="utf-8")
    fp.write(str_content)
    fp.close()
''' 把合并好的分段视频 复制到 手机磁盘空间里 '''

import os
from globalvars import __ROOTPATH__
# from .config.upload_config import mobile_drive_path,mobile_storage_folder,video_upload_config_list
from .auto_combine_video import video_root_path_name
import shutil
from datetime import datetime
import sys

# TODO: 注意：目前这个脚本是有问题的，还不知道电脑怎么访问到 手机存储空间，现在这样写认为是当前工程根目录下的

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
    f_path = '{0}/move_video_to_mobile_storage_log_{1}.log'.format(logs_dir,cur_timestamp)
    # 写入文本
    fp = open(f_path,"a",encoding="utf-8")
    fp.write('{0}\n'.format(str_content))  
    fp.close()

# 删除一个文件夹下的所有文件
# EXAMPLE_PATH = r'C:\Users\shenping\PycharmProjects\Shenping_TEST\day_5\Testfolder'
def del_files(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_files(c_path)
        else:
            os.remove(c_path)

def copy_video_to_mobile_storage():
  log_print("\n------------------ 把合并好的分段视频 复制到 手机磁盘空间里 -------------------\n")
  # 手机存储区视频存放根目录
  storage_video_folder = '{0}/{1}'.format(mobile_drive_path,mobile_storage_folder)
  if not os.path.exists(storage_video_folder):
    os.makedirs(storage_video_folder)
  log_print('手机存储区视频存放根目录：\n{0}'.format(storage_video_folder))
  
  # 在上面的目录下，再创建一个与当前工程中保持一致的一个存储视频的固定名称的文件夹
  mobile_video_path = '{0}/{1}'.format(storage_video_folder,video_root_path_name)
  log_print('手机存储区，与当前工程中保持一致的一个存储视频的固定名称的文件夹：\n{0}'.format(mobile_video_path))

  # 当前工程中，存放已输出的分段视频文件的文件夹（从这个文件夹里 复制 所需视频到 手机存储区中）
  source_video_root_path = '{0}auto_clip_video_byandroid/{1}'.format(__ROOTPATH__,video_root_path_name)
  log_print('当前工程中，存放已输出的分段视频文件的文件夹（从这个文件夹里 复制 所需视频到 手机存储区中）：\n{0}'.format(source_video_root_path))
  
  # 读取要上传
  index_num = 1
  for upload_param_item in video_upload_config_list:
    source_video_show_1th = '{0}/{1}'.format(source_video_root_path,upload_param_item['first_name'])
    source_video_show_2th = '{0}/{1}/fullfiles'.format(source_video_show_1th,upload_param_item['second_name'])
    source_video_show_file_list = os.listdir(source_video_show_2th)

    # 手机存储空间中检查是否存在对应的目录，不存在则创建一个空的
    target_video_show_1th = '{0}/{1}'.format(mobile_video_path,upload_param_item['first_name'])
    target_video_show_2th = '{0}/{1}'.format(target_video_show_1th,upload_param_item['second_name'])
    target_video_show_2th_fullfiles = '{0}/fullfiles'.format(target_video_show_2th,upload_param_item['second_name'])
    if not os.path.exists(target_video_show_1th):
      os.makedirs(target_video_show_1th)
    if not os.path.exists(target_video_show_2th):
      os.makedirs(target_video_show_2th)
    if not os.path.exists(target_video_show_2th_fullfiles):
      os.makedirs(target_video_show_2th_fullfiles)

    # 需要上传的分段视频的序号 数组
    need_upload_video_serial_list = upload_param_item['paragraph_serials'].split(',')
    for need_upload_video_serial in need_upload_video_serial_list:
      video_show_file_full_name = '{0}_{1}'.format(upload_param_item['second_name'],need_upload_video_serial)
      # 判定如果本工程输出的分段视频是否真实存在，存在的话才进行复制操作
      for source_video_show_file_name in source_video_show_file_list:
        if video_show_file_full_name in source_video_show_file_name:
          # 进行复制操作
          log_print('\n--------- 第 {} 轮 复制操作 ---------'.format(index_num))

          source_video_show_file_path = '{0}/{1}'.format(source_video_show_2th,source_video_show_file_name)
          log_print('当前工程中，找到的分段视频文件：\n{0}'.format(source_video_show_file_path))
          index_num += 1
          try:
            # source = 'current/test/test.py'
            # target = '/prod/new'
            copy_source = source_video_show_file_path.replace('/','\\')
            copy_target = target_video_show_2th_fullfiles.replace('/','\\')
            log_print('copy_source：\n{0}'.format(copy_source))
            log_print('copy_target：\n{0}'.format(copy_target))
            shutil.copy(copy_source, copy_target)
            log_print("复制成功")
          except IOError as e:
            log_print("Unable to copy file. %s" % e)
          except:
            log_print("Unexpected error:", sys.exc_info())

''' 提供给外界调用的主入口函数 '''
def main_func(upload_config_module):
    global mobile_drive_path
    global mobile_storage_folder
    global video_upload_config_list

    mobile_drive_path = upload_config_module.mobile_drive_path
    mobile_storage_folder = upload_config_module.mobile_storage_folder
    video_upload_config_list = upload_config_module.video_upload_config_list

    log_print('请手动把 auto_clip_video_byandroid/{} 这个文件夹手动复制到【手机存储空间的根目录】下'.format(video_root_path_name))
    log_print('(注意：目前这个脚本是有问题的，还不知道电脑怎么访问到 手机存储空间，现在这样写认为是当前工程根目录下的)')
    # copy_video_to_mobile_storage()
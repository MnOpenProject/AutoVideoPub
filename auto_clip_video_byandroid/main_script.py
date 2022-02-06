import importlib,os
from globalvars import __ROOTPATH__
from .auto_combine_video import main_func as combine_main_func
from .auto_upload_video_to_blibli import main_func as upload_main_func,start_mkdir_full_video_folder,start_mkdir_video_folder
from .move_video_to_mobile_storage import main_func as move_video_main_func
from .auto_split_tsfiles import main_func as split_video_main_func

# 判定是否为纯整数字符串
def is_int_str(str):
    try:
        int(str)
        return True
    except:
        return False

''' 提供给外界调用的主入口函数 '''
def main_func():
  # ----------------------------- 选择要执行的功能 ----------------------------------
  print('\n----------------------------- 选择要执行的功能 ----------------------------------\n')
  hint_options = [
    '[1] - 视频分段剪辑',
    '[2] - （功能有问题，先别用）把合并好的分段视频 复制到 手机磁盘空间里',
    '[3] - 自动通过<必剪 app>上传分段视频',
    '[4] - 视频分解（比如将 .mp4 视频文件分解成 .ts 切片文件，输出目录在 downloadvideo/ 目录下）',
    '[5] - 创建用于存放*完整*视频文件的目录（如果要上传发布的视频文件还没有放到该项目的指定目录下，则请先执行该操作）',
    '[6] - 创建用于存放*分段*视频文件的目录（如果要上传发布的视频文件还没有放到该项目的指定目录下，则请先执行该操作）'
  ]
  print('请选择要操作的功能：(默认 [1])')
  for hint in hint_options:
    print(hint)
  user_selected = input()
  user_selected = '1' if not is_int_str(user_selected) else user_selected
  user_selected = '1' if int(user_selected) < 1 or int(user_selected) > len(hint_options) else str(user_selected)
  print('[*] - 已选择：{}\n'.format(hint_options[int(user_selected)-1]))

  # ----------------------------- 选择要视频配置脚本 ----------------------------------
  print('\n----------------------------- 选择要视频配置脚本 ----------------------------------\n')
  print('请选择要使用的配置脚本，不同的配置脚本对应不同的视频节目（默认选项： [1]）\n（输入对应的序号即可）')
  video_upload_config_params = []
  upload_config_files_name = 'upload_config_files'
  # 读取所有的配置脚本名称
  video_upload_config_list = os.listdir('{0}auto_clip_video_byandroid/config/{1}'.format(__ROOTPATH__,upload_config_files_name))
  video_upload_config_list_len = len(video_upload_config_list)
  # 根据文件名称，动态引入脚本
  idx = 1
  for upload_config_file_str in video_upload_config_list:
    if not '.py' in upload_config_file_str:
      continue
    # 动态引入脚本
    module_str = "auto_clip_video_byandroid.config.{0}.{1}".format(upload_config_files_name,upload_config_file_str.replace('.py',''))
    # print('动态引入脚本字符串：{}'.format(module_str))
    module_upload_config = importlib.import_module(module_str)
    upload_config_param = {
      'file_name': upload_config_file_str,
      'desc': module_upload_config.module_instruction,
      'module_obj': module_upload_config
    }
    video_upload_config_params.append(upload_config_param)
    print('[{0}] - {1} - {2}'.format(idx, upload_config_param['file_name'], upload_config_param['desc']))
    idx += 1
  # 用户选择
  user_selected_input = input()
  upload_config_module_idx = 0 if not (int(user_selected_input) >= 1 and int(user_selected_input) <= video_upload_config_list_len) else (int(user_selected_input) - 1)
  # 根据用户的选择，选用对应的 upload_config 配置脚本
  upload_config_param = video_upload_config_params[upload_config_module_idx]
  upload_config_module = upload_config_param['module_obj']
  print('[*] - 已选择的 upload_config 文件是：')
  print('    |-- [{0}] - {1} - {2}'.format((upload_config_module_idx+1), upload_config_param['file_name'], upload_config_param['desc']))

  if user_selected == '1':
    combine_main_func(upload_config_module)
  elif user_selected == '2':
    move_video_main_func(upload_config_module)
  elif user_selected == '3':
    upload_main_func(upload_config_module)
  elif user_selected == '4':
    split_video_main_func(upload_config_module)
  elif user_selected == '5':
    start_mkdir_full_video_folder(upload_config_module)
  elif user_selected == '6':
    start_mkdir_video_folder(upload_config_module)
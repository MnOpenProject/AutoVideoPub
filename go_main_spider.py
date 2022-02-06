import os
from globalvars import __ROOTPATH__

# 判定是否为纯整数字符串
def is_int_str(str):
    try:
        int(str)
        return True
    except:
        return False

if __name__ == '__main__':
    options = [
        '[1] - 启动上传视频脚本：通过手机自动上传视频'
        ]
    print('---- 请选择操作项 默认选项：[1] ----')
    for opt in options:
        print(opt)

    user_select = input()
    user_select = 1 if not is_int_str(user_select) else int(user_select)
    user_select = 1 if user_select < 1 or user_select > len(options) else user_select
    print('\n------------ 已选择选项：{}----------\n'.format(options[user_select-1]))
    print('-------------------------------------------------------------------------------------')

    drive_str = __ROOTPATH__[:2] # 从目录字符串中截取盘符
    cmd_cd_dir_str = '{0} && CD {1}'.format(drive_str,__ROOTPATH__)
    if user_select == 1:
         # 自动上传视频脚本
        cmd_str = '{} && py run_autoupload_bilibli.py'.format(cmd_cd_dir_str)
        print(cmd_str)
        os.system(cmd_str)

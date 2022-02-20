import os
from datetime import datetime
from auto_clip_video_byandroid.module_root import __MODULEROOTPATH__
from auto_clip_video_byandroid.config.connection_config import out_log_file

# 判断变量是否已定义
def isset(v):
    try:
        type (eval(v))
    except:
        return False
    else:
        return True

# 判定是否为纯整数字符串
def is_int_str(str):
    try:
        int(str)
        return True
    except:
        return False

# 通用的选项输入提示
def ask_for_selection(hint_options,log_print,default_num=1):
    log_print(f'请选择要操作的功能：(默认 [{default_num}])')
    for hint in hint_options:
        log_print(hint)
    user_selected = input()
    user_selected = str(default_num) if not is_int_str(user_selected) else user_selected
    user_selected = str(default_num) if int(user_selected) < 1 or int(user_selected) > len(hint_options) else str(user_selected)
    log_print('[*] - 已选择：{}\n'.format(hint_options[int(user_selected)-1]))
    log_print('--------------------------------------------------------------------------------------------------')
    return user_selected

# 自定义的 log 输出方法
cur_timestamp = str(datetime.now().timestamp()).replace('.','')
def common_log_print(str_content,script_name='common'):
    # 在终端打印
    print(str_content)
    if out_log_file:
        # 输出到日志文件
        logs_dir = '{0}/logs'.format(__MODULEROOTPATH__)
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        # _log 前面改成当前的脚本文件名称
        f_path = '{0}/{1}_{2}.log'.format(logs_dir,script_name,cur_timestamp)
        # 写入文本
        fp = open(f_path,"a",encoding="utf-8")
        fp.write('{0}\n'.format(str_content))
        fp.close()

def filter_listdir(dir_list):
    # 获取干净的子目录列表（排除那些类似自动生成的目录）
    return [i for i in dir_list if not i == '__pycache__']
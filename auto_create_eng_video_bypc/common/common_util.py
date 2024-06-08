import os,importlib
from datetime import datetime
from enum import Enum
from auto_create_eng_video_bypc.module_root import __MODULEROOTPATH__
from auto_create_eng_video_bypc.config import out_log_file

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
def ask_for_selection(hint_options,log_print__=None,default_num=1,hint_str=None):
    log_print = common_log_print
    if not log_print__ == None:
        log_print = log_print__
    log_print('--------------------------------------------------------------------------------------------------')
    # 打印选项信息列表
    for hint in hint_options:
        log_print(hint)
    # 打印输入提示
    hint_str_=f'请从上面选项中，选择要操作的功能：(默认 [{default_num}])'
    if not hint_str == None:
        hint_str_ = hint_str
    log_print(f'{hint_str_}')
    # 获取输入
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

# 调试的时候用于临时中断代码的函数
def debug_input(hint:str=''):
    hint_str = '中断代码了，人工审核后，再决定是否继续把~' if hint == '' or hint == None else hint
    print(hint_str)
    input()

# 删除一个文件夹下的所有文件
# EXAMPLE_PATH = r'C:\Users\shenping\PycharmProjects\Shenping_TEST\day_5\Testfolder'
def del_files(path,dir=None):
    print(f'正在删除...\n{path}')
    try:
        if not dir == None and os.path.exists(dir):
            os.rmdir(dir)
    except Exception as ex:
        # print(f'del_files ex = {ex}')
        pass
    if os.path.exists(path):
        ls = os.listdir(path)
        count = len(ls)
        for n,i in enumerate(ls):
            print(f'删除进度：{n+1}/{count}')
            c_path = os.path.join(path, i)
            if os.path.isdir(c_path):
                del_files(c_path,c_path)
            else:
                os.remove(c_path)

def get_seirals_by_rangestr(rangstr,str_len=None):
    # @param rangstr: 范围字符串参数(格式如 '1:16')
    # @param str_len: 控制序号字符串的长度，不足会自动补零，如果这个参数不写，会默认保持最大值的字符串长度，不足自动补零
    # 例如：
    # get_seirals_by_rangestr('3:6',2) 则输出 => ['03', '04', '05', '06']
    # get_seirals_by_rangestr('3:6',2) 则输出 => ['01', '02', '03']
    # get_seirals_by_rangestr('3:6',2) 则输出 => ['01', '02', '03']
    # get_seirals_by_rangestr('2:',2) 则输出 => ['02', '03']
    # get_seirals_by_rangestr(':',2) 则输出 => ['01', '02']
    # rangstr 参数不符合条件的 则返回 None
    
    result = []
    test_str = rangstr
    test_list = test_str.split(':')
    if not len(test_list) == 2:
        return None
    # print(test_list)
    start,end = test_list
    start = 1 if not start else start
    end = start + 1 if not end else end
    # print(start,end)
    str_max_len = len(end)
    if not str_len == None:
        str_max_len = str_len
    sub = int(end) - int(start)
    for sub_idx in range(sub+1):
        cur_ser = int(start) + sub_idx
        cur_ser_len = len(str(cur_ser))
        zero_fill_count = str_max_len-cur_ser_len
        zero_fill = '0'*(0 if zero_fill_count < 0 else zero_fill_count)
        out_str = '{0}{1}'.format(zero_fill,cur_ser)
        result.append(out_str)
    return result
from time import sleep
from datetime import datetime
from .common_config import __CURPATH__,logs_out_dir
import eventlet,os
import ffmpy3,json,subprocess

# 获取视频文件的时长
# 参考地址：https://blog.csdn.net/lilongsy/article/details/121206810
def get_duration_from_ffmpeg(url):
    # [url] 可以是本地文件的绝对路径，也可以是在线地址 https://xxx
    tup_resp = ffmpy3.FFprobe(
        inputs={url: None},
        global_options=[
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format', '-show_streams'
        ]
    ).run(stdout=subprocess.PIPE)

    meta = json.loads(tup_resp[0].decode('utf-8'))
    return meta['format']['duration']

# 判定是否为纯整数字符串
def is_int_str(str):
    try:
        int(str)
        return True
    except:
        return False

# 选项输入
def input_selection():
    selection = input()
    selection = 1 if not is_int_str(selection) else int(selection)
    return selection

def time_sleep(value):
    with eventlet.Timeout(30, False):  # 设置超时间
        sleep(value)

# 强制睡眠方法
def force_sleep(wait_sec,log_print_func=None):
    log_print__ = log_print_func
    if log_print__ == None:
        log_print__ = log_print
    log_print__(' ------ 强制等待，第 {} 秒 ----- '.format(wait_sec))
    time_sleep(wait_sec)

# 自定义的 log 输出方法
cur_timestamp = str(datetime.now().timestamp()).replace('.','')
def log_print(str_content,file_name='common'):
    # 在终端打印
    print(str_content)
    # 输出到日志文件
    logs_dir = logs_out_dir
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    # _log 前面改成当前的脚本文件名称
    f_path = f'{logs_dir}/{file_name}_{cur_timestamp}.log'
    # 写入文本
    fp = open(f_path,"a",encoding="utf-8")
    fp.write('{0}\n'.format(str_content))
    fp.close()

def filter_listdir(dir_list):
    # 获取干净的子目录列表（排除那些类似自动生成的目录）
    return [i for i in dir_list if not i == '__pycache__']

# 通用的选项输入提示
def ask_for_selection(hint_options,log_print__=None,default_num=1,hint_str='请选择要操作的功能'):
    cur_log_print = log_print
    if not log_print__ == None:
        cur_log_print = log_print__
    cur_log_print(f'{hint_str}：(默认 [{default_num}])')
    for hint in hint_options:
        cur_log_print(hint)
    user_selected = input()
    user_selected = str(default_num) if not is_int_str(user_selected) else user_selected
    user_selected = str(default_num) if int(user_selected) < 1 or int(user_selected) > len(hint_options) else str(user_selected)
    cur_log_print('[*] - 已选择：{}\n'.format(hint_options[int(user_selected)-1]))
    cur_log_print('--------------------------------------------------------------------------------------------------')
    return user_selected

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
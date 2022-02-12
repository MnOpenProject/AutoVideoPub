''' 自动组合已爬取到本地的.ts视频切片 --  '''
''' 通过 appium + python 的实现的自动化操作'''
# 参考地址：https://www.cnblogs.com/lsdb/p/10108165.html

# 【*】appium 工具上的连接参数
# appiumGuiParams = {
# 必要参数
#   'platformName': 'Android',
#   'deviceName': 'A33m', # 设备名称
#   'appPackage': 'com.dragon.read', # app 的包名
#   'appActivity': '.pages.splash.SplashActivity', # app 要启动的活动 id
# 以下是非必要参数，不填也行的
#   'platformVersion': '10', # Android 版本号
#   'noReset': 'true',
#   'newCommandTimeout': 6000,
#   'automationName': 'UiAutomator2'
# }

# 【*】以上必要参数的获取方式如下
# Android 设备连接电脑后，在 Android 设备中只启动想要操作的 app
# 然后在电脑的 cmd 里输入以下指令，查询出 Android 设备中当前正在运行的 app 信息，其中就包含 app 的包名称（即上面的 appPackage 的参数值）
# adb shell dumpsys activity | findstr "intent={"
# 例如这个 番茄小说 app 的信息如下（其中 cmp=对应的内容表示 【 app包名/第一展示的刷新活动页，即 appPackage参数值/appActivity参数值 】）
# intent={act=android.intent.action.MAIN cat=[android.intent.category.LAUNCHER] flg=0x10200000 cmp=com.dragon.read/.pages.splash.SplashActivity}

from globalvars import __ROOTPATH__
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime
import os
import importlib
import shutil
import json
from .combine_ts_by_ffmpeg import combine_ts_by_ffmpeg
from .config.connection_config import out_log_file
from .combine_ts_by_ffmpeg import combine_ts_by_ffmpeg,combine_ts_by_ffmpeg2
from .common.ffmpeg_util import get_duration_from_ffmpeg

''' ======================== 无限递归的解决方案 start ========================== '''
# 这个值的大小取决你自己，最好适中即可，执行完递归再降低，毕竟递归深度太大，如果是其他未知的操作引起，可能会造成内存溢出
import sys
sys.setrecursionlimit(1000000)

# 以后要想实现尾递归都时候就复制上面装饰器以上都代码，然后将递归函数加上该装饰器就OK。
# @tail_call_optimized

class TailCallException(BaseException):
    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs


def tail_call_optimized(func):
    def _wrapper(*args, **kwargs):
        f = sys._getframe()
        if f.f_back and f.f_back.f_back and f.f_code == f.f_back.f_back.f_code:
            raise TailCallException(args, kwargs)

        else:
            while True:
                try:
                    return func(*args, **kwargs)
                except TailCallException as e:
                    args = e.args
                    kwargs = e.kwargs
    return _wrapper


''' ======================== 无限递归的解决方案 end ========================== '''

# 自定义的 log 输出方法
cur_timestamp = str(datetime.now().timestamp()).replace('.','')
def log_print(str_content):
    # 在终端打印
    print(str_content)
    if out_log_file:
        # 输出到日志文件
        logs_dir = '{0}auto_clip_video_byandroid/logs'.format(__ROOTPATH__)
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        # _log 前面改成当前的脚本文件名称
        f_path = '{0}/auto_combine_video_log_{1}.log'.format(logs_dir,cur_timestamp)
        # 写入文本
        fp = open(f_path,"a",encoding="utf-8")
        fp.write('{0}\n'.format(str_content))  
        fp.close()

# @param rangstr: 范围字符串参数(格式如 '1:16')
# @param str_len: 控制序号字符串的长度，不足会自动补零，如果这个参数不写，会默认保持最大值的字符串长度，不足自动补零
# 例如：
# get_seirals_by_rangestr('3:6',2) 则输出 => ['03', '04', '05', '06']
# get_seirals_by_rangestr('3:6',2) 则输出 => ['01', '02', '03']
# get_seirals_by_rangestr('3:6',2) 则输出 => ['01', '02', '03']
# get_seirals_by_rangestr('2:',2) 则输出 => ['02', '03']
# get_seirals_by_rangestr(':',2) 则输出 => ['01', '02']
# rangstr 参数不符合条件的 则返回 None
def get_seirals_by_rangestr(rangstr,str_len=None):
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

# 初始化所有所需目录
video_root_path_name = 'video' # 最终视频输出的文件夹名称，该文件夹也会被直接复制到手机的指定目录下
video_root_path = '{0}auto_clip_video_byandroid/{1}'.format(__ROOTPATH__,video_root_path_name)
def initAllDir():
    if not os.path.exists(video_root_path):
        os.makedirs(video_root_path)

# 为 .ts 文件的（1.ts,2.ts,3.ts,...,101.ts,...）这样的文件列表进行从小到大排序
def bubbleSortTsFile(arr):
    n = len(arr)
    # 遍历所有数组元素
    for i in range(n):
        # Last i elements are already in place
        for j in range(0, n-i-1):
            if int(arr[j].replace('.ts','')) > int(arr[j+1].replace('.ts','')) :
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# .ts 文件合并成 一个完整的 视频文件 比如 .mp4
def combine_ts_list_to_video(tsvideoRoot, tsFileDir, saveFilePath):
    tsvideoRoot = tsvideoRoot.replace('/','\\')
    tsFileDir = tsFileDir.replace('/','\\')
    saveFilePath = saveFilePath.replace('/','\\')
    # drive 参数是设定的输出的磁盘
    drive_name = tsvideoRoot[0] # 输出的盘符就是当前工程所在的盘符
    log_print('开始合并文件\n{0}/{1}/{2}\n'.format(tsvideoRoot,tsFileDir,saveFilePath))

    # 利用 windows 的 cmd 指令完成合并
    copy_source_cmd_str = ''
    ts_dir_file_list = os.listdir(tsFileDir)
    ts_file_list = [i for i in ts_dir_file_list if '.ts' in i]
    ts_file_list = bubbleSortTsFile(ts_file_list)
    for file_idx,ts_file in enumerate(ts_file_list):
        # relative_ts_dir = '{0}{1}'.format(tsFileDir.replace(tsvideoRoot,''), ts_file)
        relative_ts_dir = '{0}\\{1}'.format(tsFileDir, ts_file)
        print('relative_ts_dir => {}'.format(relative_ts_dir))
        if file_idx == 0:
            copy_source_cmd_str = '{0}'.format(relative_ts_dir)
        else:
            copy_source_cmd_str = '{0}+{1}'.format(copy_source_cmd_str,relative_ts_dir)

    tsvideoDirCmdStr = drive_name + ": && cd " + tsvideoRoot
    # cmdStr = tsvideoDirCmdStr + " && copy /b " + tsFileDir + "\\*.ts " + saveFilePath
    cmdStr = tsvideoDirCmdStr + " && copy /b " + copy_source_cmd_str + " " + saveFilePath
    log_print("CMD合成指令：{}".format(cmdStr))
    os.system(cmdStr)
    log_print("{}视频合成完成".format(saveFilePath))

# 清空 tsfiles 文件夹
def clear_tsfiles_folder(p_second_dir_tsdir):
    tsfiles_dirs = os.listdir(p_second_dir_tsdir)
    for tsfiles_dir in tsfiles_dirs:
        tsfiles_dir_full = '{0}/{1}'.format(p_second_dir_tsdir,tsfiles_dir)
        del_files(tsfiles_dir_full) # 清空文件夹
        os.removedirs(tsfiles_dir_full) # 清空文件夹之后，就能删除该文件夹了
    log_print('已清空 tsfiles 文件夹:\n{0}'.format(p_second_dir_tsdir))

# 清空 fullfiles 文件夹
def clear_fullfiles_folder(p_second_dir_videodir):
    if not os.path.exists(p_second_dir_videodir):
        os.makedirs(p_second_dir_videodir)
    fullfiles_list = os.listdir(p_second_dir_videodir)
    for fullfiles_filename in fullfiles_list:
        path_file = '{0}/{1}'.format(p_second_dir_videodir,fullfiles_filename)
        del_files(path_file)
    del_files(p_second_dir_videodir) # 清空文件夹
    log_print('已清空 fullfiles 文件夹:\n{0}'.format(p_second_dir_videodir))

# [1] - 精确分段方案;
# 精确分段参数案例（必须满足该格式要求，否则程序会异常报错）：['00:01:25,00:02:59', '00:03:25,00:04:39']
def combine_ts_group_by_timeval(paragraph_time_list,ts_file_root_dir,ts_file_video_dir,p_second_dir_videodir,ts_folder_name):
    log_print('当前视频文件的根目录: \n{0}'.format(ts_file_root_dir))
    log_print('具体的 .ts 文件目录：\n{0}'.format(ts_file_video_dir))
    # 获取文件夹下的所有文件名
    ts_file_list = os.listdir(ts_file_video_dir)
    ts_file_list = bubbleSortTsFile(ts_file_list) # 一定要进行按序号名称从小到大排好序，才能确保后续操作
    # ts_file_list_len = len(ts_file_list)
    # 遍历时刻字符串数组，依次执行相应的分段操作
    for p_idx,time_range in enumerate(paragraph_time_list):
        log_print('请耐心稍等，精剪操作可能有点久...')
        time_list = str(time_range).split(',')
        # 开始时刻
        start_time_list = time_list[0].split(':')
        start_h = int(start_time_list[0]) # 时
        start_m = int(start_time_list[1]) # 分
        start_s = int(start_time_list[2]) # 秒
        start_total_sec = start_h * 60 * 60 + start_m * 60 + start_s # 开始时刻转换为 秒级 数值
        # 结束时刻
        end_time_list = time_list[1].split(':')
        end_h = int(end_time_list[0]) # 时
        end_m = int(end_time_list[1]) # 分
        end_s = int(end_time_list[2]) # 秒
        end_total_sec = end_h * 60 * 60 + end_m * 60 + end_s # 结束时刻转换为 秒级 数值

        # 根据以上计算所得 秒级 范围，收集对应要进行合并的 .ts 文件
        collect_ts_file_list = [] # 收集相应的 .ts 文件
        duration_total_s = 0 # 遍历 .ts 文件时的累加时长(单位：秒)
        for ts_file_name in ts_file_list:
            ts_file_path = f'{ts_file_video_dir}/{ts_file_name}'
            # 获取当前.ts文件的时长
            duration_s = get_duration_from_ffmpeg(ts_file_path)
            # 取整
            duration_s = int(round(float(duration_s),1))
            duration_total_s += duration_s
            # 若累加时长在 开始 和 结束 的范围内，则记录下这个范围内的 .ts 文件的绝对路径
            if duration_total_s >= start_total_sec and duration_total_s <= end_total_sec:
                collect_ts_file_list.append(ts_file_path)
        log_print(f'收集到的.ts列表：\n{collect_ts_file_list}')
        
        # 准备把上面整理好的 当前分段的所有 .ts 文件的所在文件夹 一起合并成一个 视频文件(如 .mp4)
        # 为了适应 <必剪 app> 的视频编辑时视频声音丢失的情况，这里特意把每个分段文件独立放到一个文件夹里，方便 app 里单独查找文件抽离声音
        # 对当前视频片段进行合并
        # 对当前分段的 .ts 视频进行分类放到不同的文件夹下，因为合并时需要对整个文件夹进行合并成一个 视频文件(如 .mp4)
        # 当前分段的所有 .ts 文件存放的文件夹路径
        p_idx_sfx = '0{0}'.format(p_idx + 1) if len(str(p_idx + 1)) < 2 else p_idx + 1
        p_video_name = '{0}_{1}'.format(ts_folder_name,p_idx_sfx)
        p_video_file_full_pre_dir = '{0}/{1}'.format(p_second_dir_videodir,p_video_name)
        if not os.path.exists(p_video_file_full_pre_dir):
            os.makedirs(p_video_file_full_pre_dir)
        p_video_file_full = '{0}/{1}{2}'.format(p_video_file_full_pre_dir,p_video_name,video_file_Format)
        log_print('当前片段 视频合成文件的完整路径: \n{0}'.format(p_video_file_full))
        # 开始合并并输出视频文件
        tsvideoRoot = ts_file_root_dir
        # tsFileDir = p_tsfiles_dir
        saveFileDir = p_video_file_full_pre_dir
        saveFilePath = p_video_file_full
        # 合并本次收集到的 .ts 文件，输出为一个分段视频
        log_print(f'【*】 tsvideoRoot = {tsvideoRoot}')
        # log_print(f'【*】 tsFileDir = {tsFileDir}')
        log_print(f'【*】 saveFileDir = {saveFileDir}')
        log_print(f'【*】 saveFilePath = {saveFilePath}')
        combine_ts_by_ffmpeg2(tsvideoRoot, collect_ts_file_list, saveFileDir, saveFilePath, log_print)

# 对 .ts 文件进行 片段剪辑 并进行分段合并成一个视频文件(比如 .mp4)
def combine_video():
    for cfg in video_file_config_list:
        # 先尝试是否为 '2:6' 类似这样的范围字符串，如果不是则会返回 None
        need_upload_video_episode_list = get_seirals_by_rangestr(cfg['episode_list'],2)
        if need_upload_video_episode_list == None:
            # 如果不是范围字符串，那就只能是 '01,02,03' 类似这样的 都好分隔的字符串
            need_upload_video_episode_list = cfg['episode_list'].split(',')

        # 先创建存放的文件夹
        p_first_dir = '{0}/{1}'.format(video_root_path,cfg['first_name'])
        p_second_dir = '{0}/{1}'.format(p_first_dir,cfg['second_name'])
        # 分好段的 .ts 文件夹
        p_second_dir_tsdir = '{0}/tsfiles'.format(p_second_dir)
        # 对分好段的 .ts 文件进行合并输出的 视频目录
        p_second_dir_videodir = '{0}/fullfiles'.format(p_second_dir)
        if not os.path.exists(p_first_dir):
            os.makedirs(p_first_dir)
        if not os.path.exists(p_second_dir):
            os.makedirs(p_second_dir)
        if not os.path.exists(p_second_dir_tsdir):
            os.makedirs(p_second_dir_tsdir)
        # 清理 tsfiles 文件夹
        clear_tsfiles_folder(p_second_dir_tsdir)
        # 清理 fullfiles 文件夹
        clear_fullfiles_folder(p_second_dir_videodir)

        for episode in need_upload_video_episode_list:
            ts_folder_name = '{0}_{1}'.format(cfg['second_name'],episode)
            # 找到视频的所有 .ts 文件
            ts_file_root_dir = '{0}{1}/{2}/{3}'.format(__ROOTPATH__, video_download_file_root_dir, cfg['first_name'],cfg['second_name'])
            ts_file_dir = '{0}/tsfiles'.format(ts_file_root_dir)
            ts_file_video_dir = '{0}/{1}'.format(ts_file_dir,ts_folder_name)

            # 根据配置参数，只处理配置参数中需要的视频分集
            # 要上传的视频文件名
            need_upload_video_episode_filename_list = []
            # 要上传的视频分集号数组
            need_upload_video_episode_list = []
            # 先尝试是否为 '2:6' 类似这样的范围字符串，如果不是则会返回 None
            need_upload_video_episode_list = get_seirals_by_rangestr(cfg['episode_list'],2)
            if need_upload_video_episode_list == None:
                # 如果不是范围字符串，那就只能是 '01,02,03' 类似这样的 都好分隔的字符串
                need_upload_video_episode_list = cfg['episode_list'].split(',')
            # 拼接需要上的视频分集文件名称
            for esp in need_upload_video_episode_list:
                need_upload_video_episode_filename = '{0}_{1}'.format(cfg['second_name'],esp)
                need_upload_video_episode_filename_list.append(need_upload_video_episode_filename)
            print('需要进行分段的视频为：\n{}'.format(json.dumps(need_upload_video_episode_filename_list)))
            # 若当前文件不需要上传，则不进行分段操作
            if not ts_folder_name in need_upload_video_episode_filename_list:
                print('当前文件不需要进行上传，所以无需分段：\n{}'.format(ts_folder_name))
                continue
            # 只找实际存在的文件夹（ .ts 文件所在目录）
            elif os.path.exists(ts_file_video_dir):
                # 判定选择分段方案：分段剪辑方案：[1] - 精确分段方案; [2] - 粗略分段方案;
                # 当 paragraph_time_list（精确分段参数）为时刻字符串数组时，会默认执行[1] - 精确分段方案；当 paragraph_time_list（精确分段参数）为空数组时，程序会选择 [2] - 粗略分段方案; 去执行分段剪辑；
                paragraph_time_list = cfg['paragraph_time_list']
                if isinstance(paragraph_time_list,list) and len(paragraph_time_list) > 0:
                    # [1] - 精确分段方案;
                    # 精确分段参数案例（必须满足该格式要求，否则程序会异常报错）：['00:01:25,00:02:59', '00:03:25,00:04:39']
                    combine_ts_group_by_timeval(paragraph_time_list,ts_file_root_dir,ts_file_video_dir,p_second_dir_videodir,ts_folder_name)
                    continue
                # 一个 .ts 文件的时长(单位：秒)
                unit_ts_long_s = cfg['ts_unit_long_s']

                log_print('当前视频文件的根目录: \n{0}'.format(ts_file_root_dir))
                log_print('具体的 .ts 文件目录：\n{0}'.format(ts_file_video_dir))
                # 获取文件夹下的所有文件名
                ts_file_list = os.listdir(ts_file_video_dir)
                ts_file_list = bubbleSortTsFile(ts_file_list) # 一定要进行按序号名称从小到大排好序，才能确保后续操作
                ts_file_list_len = len(ts_file_list)
                # ts_file_list_end_index = ts_file_list_len - 1

                # 当前一整集的总体剪辑 开始索引 和 结束索引
                # start_index = int(cfg['start_percent'] / 100 * ts_file_list_len)
                start_time_list = str(cfg['start_percent']).split(':')
                start_time_h = int(start_time_list[0]) # 时
                start_time_m = int(start_time_list[1]) # 分
                start_time_s = int(start_time_list[2]) # 秒
                start_sec_total = start_time_h * 60 * 60 + start_time_m * 60 + start_time_s # 计算总秒数
                start_index = int(start_sec_total / unit_ts_long_s)
                start_index = ts_file_list_len - 2 if start_index >= ts_file_list_len - 1 else start_index
                log_print('总开始索引: {0}；对应的 .ts 文件为：\n{1}'.format(start_index,ts_file_list[start_index]))
                # end_index = int(cfg['end_percent'] / 100 * ts_file_list_len)
                end_time_list = str(cfg['end_percent']).split(':')
                end_time_h = int(end_time_list[0]) # 时
                end_time_m = int(end_time_list[1]) # 分
                end_time_s = int(end_time_list[2]) # 秒
                end_sec_total = end_time_h * 60 * 60 + end_time_m * 60 + end_time_s # 计算总秒数
                end_index = int(end_sec_total / unit_ts_long_s)
                end_index = start_index + 2 if end_index <= start_index else end_index
                end_index = ts_file_list_len - 1 if end_index >= ts_file_list_len - 1 else end_index
                log_print('总结束索引: {0}；对应的 .ts 文件为：\n{1}'.format(end_index,ts_file_list[end_index]))

                file_count = end_index - start_index
                log_print('该区间存在的文件数量:\n{0}'.format(file_count))
                
                # 开始根据设定的分段进行剪辑并合并视频
                
                # 每一段的 .ts 文件数量
                paragraph = cfg['paragraph']
                # 每一段的时长（单位：秒）
                paragraph_long_s = cfg['paragraph_long_m'] * 60
                # every_p_file_count = int(file_count / paragraph) - 2 # 保险起见，避免索引溢出，多减去n个单位的文件
                # 每一段视频应该包含的 .ts 文件数量(这是标准数量，非实际数量) = 总时长(一个分段的时长) / 单位时长(一个 .ts 的时长)
                every_p_file_count = int(paragraph_long_s / unit_ts_long_s)
                log_print('每一段视频包含 {0} 个 .ts 文件'.format(every_p_file_count))
                # 计算设定的 间隔百分比 参数 实际对应 多少个 .ts 文件
                # paragraph_span_count = int(cfg['paragraph_span'] / 100 * ts_file_list_len)
                paragraph_span_count = int(cfg['paragraph_span'] / unit_ts_long_s)
                log_print('每一段视频之间间隔 {0} 个 .ts 文件'.format(paragraph_span_count))
                # 初始化视频片段剪辑循环参数
                p_start_index = start_index
                p_end_index = p_start_index
                for p_idx in range(paragraph):
                    log_print('\n--------- 第 {0} 段 ----------'.format(p_idx + 1))
                    paragraph_span_count_tmp = 0 if p_idx == 0 else paragraph_span_count
                    p_start_index = p_end_index + paragraph_span_count_tmp
                    p_start_index = end_index if p_start_index > end_index else p_start_index
                    log_print('当前片段 开始索引: {0}；对应的 .ts 文件为：\n{1}'.format(p_start_index,ts_file_list[p_start_index]))
                    p_end_index = p_start_index + every_p_file_count
                    p_end_index = end_index if p_end_index > end_index else p_end_index
                    log_print('当前片段 结束索引: {0}；对应的 .ts 文件为：\n{1}'.format(p_end_index,ts_file_list[p_end_index]))
                    # 计算出当前分段实际包含的 .ts 文件数量
                    p_files_count = p_end_index - p_start_index
                    p_files_count = 0 if p_files_count < 0 else p_files_count
                    log_print('当前片段 实际包含 {0} 个 .ts 文件'.format(p_files_count))
                    # 计算当前分段的视频实际时长
                    p_minutes_long_m = p_files_count * unit_ts_long_s / 60
                    log_print('当前片段 实际时长大约: \n {0}(分钟)'.format(p_minutes_long_m))
                    log_print('每一分段实际时长必须至少：{0}(分钟)\n'.format(paragraph_min_long_m))
                    if p_minutes_long_m < paragraph_min_long_m:
                        log_print('【！！！】当前分段实际时长不满足条件，不予输出视频文件')
                    # 必须确保当前片段的时长满足设定的 分段时长最小值，才进行以下输出操作
                    else:                        
                        # 对当前视频片段进行合并
                        # 对当前分段的 .ts 视频进行分类放到不同的文件夹下，因为合并时需要对整个文件夹进行合并成一个 视频文件(如 .mp4)
                        # 当前分段的所有 .ts 文件存放的文件夹路径
                        p_idx_sfx = '0{0}'.format(p_idx + 1) if len(str(p_idx + 1)) < 2 else p_idx + 1
                        p_video_name = '{0}_{1}'.format(ts_folder_name,p_idx_sfx)
                        p_tsfiles_dir = '{0}/{1}'.format(p_second_dir_tsdir,p_video_name)
                        if not os.path.exists(p_tsfiles_dir):
                            os.makedirs(p_tsfiles_dir)
                        log_print('当前片段 .ts 文件集合存放的文件夹目录: \n{0}'.format(p_tsfiles_dir))
                        # 把对应的 .ts 文件复制到 这个 p_tsfiles_dir 目录下
                        p_ts_file_list = ts_file_list[p_start_index:p_end_index]
                        # log_print('当前片段 包含这些 .ts 文件\n{0}\n'.format(p_ts_file_list))
                        log_print('正在复制当前片段所需的 .ts 文件...')
                        for p_ts in p_ts_file_list:
                            # adding exception handling
                            try:
                                # source = 'current/test/test.py'
                                # target = '/prod/new'
                                copy_source = '{0}/{1}'.format(ts_file_video_dir,p_ts)
                                copy_target = p_tsfiles_dir
                                shutil.copy(copy_source, copy_target)
                            except IOError as e:
                                log_print("Unable to copy file. %s" % e)
                            except:
                                log_print("Unexpected error:", sys.exc_info())
                        log_print('复制完成')

                        # 准备把上面整理好的 当前分段的所有 .ts 文件的所在文件夹 一起合并成一个 视频文件(如 .mp4)
                        # 为了适应 <必剪 app> 的视频编辑时视频声音丢失的情况，这里特意把每个分段文件独立放到一个文件夹里，方便 app 里单独查找文件抽离声音
                        p_video_file_full_pre_dir = '{0}/{1}'.format(p_second_dir_videodir,p_video_name)
                        if not os.path.exists(p_video_file_full_pre_dir):
                            os.makedirs(p_video_file_full_pre_dir)
                        p_video_file_full = '{0}/{1}{2}'.format(p_video_file_full_pre_dir,p_video_name,video_file_Format)
                        log_print('当前片段 视频合成文件的完整路径: \n{0}'.format(p_video_file_full))
                        # 开始合并并输出视频文件
                        tsvideoRoot = ts_file_root_dir
                        tsFileDir = p_tsfiles_dir
                        saveFileDir = p_video_file_full_pre_dir
                        saveFilePath = p_video_file_full
                        # combine_ts_list_to_video(tsvideoRoot, tsFileDir, saveFilePath)
                        combine_ts_by_ffmpeg(tsvideoRoot, tsFileDir, saveFileDir, saveFilePath, log_print)
                
                # 合成视频文件而完成后，清理 tsfiles 文件夹
                clear_tsfiles_folder(p_second_dir_tsdir)

                # 具体的 .ts 文件
                # for ts_name in ts_file_list:
                #     log_print('.ts 文件:\n{0}'.format(ts_name))
                log_print('共有 {0} 个 .ts 文件'.format(ts_file_list_len))


''' 提供给外界调用的主入口函数 '''
def main_func(upload_config_module):
    global video_py_file_root_dir
    global video_download_file_root_dir
    global paragraph_min_long_m
    global video_file_Format
    global video_file_config_list

    video_py_file_root_dir = upload_config_module.video_py_file_root_dir
    video_download_file_root_dir = upload_config_module.video_download_file_root_dir
    paragraph_min_long_m = upload_config_module.paragraph_min_long_m
    video_file_Format = upload_config_module.video_file_Format
    video_file_config_list = upload_config_module.video_file_config_list

    initAllDir()
    combine_video()

# if __name__ == '__main__':
#   initAllDir()
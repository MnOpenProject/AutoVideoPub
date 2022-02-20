from globalvars import __ROOTPATH__
from .video_split_tsfiles_by_ffmpeg import video_split_tsfiles_by_ffmpeg

# 控制分解成 .ts 切片文件每一个切片文件的最大时长（单位：秒）
# 误差1秒，即 分解出来的有的 .ts 切片文件时长会相比设定的值少1秒，如果设置 1 秒，那么实际上分解出的有的 .ts 切片文件时长会试 0 秒，但经测试，这并不会对合并造成影响，反而可以让自动截取视频重组更精确
video_ts_unit_long_s = 1

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

def split_video():
    for cfg in video_file_config_list:
        # 先尝试是否为 '2:6' 类似这样的范围字符串，如果不是则会返回 None
        need_upload_video_episode_list = get_seirals_by_rangestr(cfg['episode_list'],2)
        if need_upload_video_episode_list == None:
            # 如果不是范围字符串，那就只能是 '01,02,03' 类似这样的 都好分隔的字符串
            need_upload_video_episode_list = cfg['episode_list'].split(',')
        for episode in need_upload_video_episode_list:
            ts_file_root_dir = '{0}{1}/{2}/{3}'.format(__ROOTPATH__, video_download_file_root_dir, cfg['first_name'],cfg['second_name'])
            video_dir = f'{ts_file_root_dir}/fullvideo'
            video_file_name = f'{cfg["second_name"]}_{episode}'
            video_format = video_file_Format
            tsfiles_out_dir = f'{ts_file_root_dir}/tsfiles'
            ts_unit_long_s=video_ts_unit_long_s
            video_split_tsfiles_by_ffmpeg(ts_file_root_dir,video_dir,video_file_name,video_format,tsfiles_out_dir,ts_unit_long_s)

# 这个视频分解功能目前就是为了开源项目而做的，这里没有实际运用
# 因为我自己的项目里的视频资源（.ts 文件），但是开源项目中不能参杂这种功能，涉及侵权
# 所以为了使得开源项目中能有用处，加入视频分解功能，使用者可以先自己的视频文件放到对应目录下，然后分解，再重新分段合并，如此一来开源项目也能够有实际用途了
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

    split_video()
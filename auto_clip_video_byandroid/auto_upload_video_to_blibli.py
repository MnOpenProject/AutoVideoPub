''' 自动组合已爬取到本地的.ts视频切片，并通过移动端<必剪 app>自动上传视频 --  '''
''' 通过 appium + python 的实现的自动化操作 '''
'''
【注】：
目前代码仅支持 华为nava8 屏幕尺寸及以上的移动设备，小于该尺寸的，很有可能导致很多 UI 的 element 找不到，因为 Appiumn 查找 element 仅限当前可视区域，
后续我将加入支持更多屏幕尺寸的设备，方案目前就是尝试查找 element ,找不到则认为当前可视区域没有，那么滚动屏幕再尝试查找
'''
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

from appium.webdriver.common.appiumby import AppiumBy
from globalvars import __ROOTPATH__
from appium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# TouchAction 已经过时了，用 drive.xxx 是最新的方案，其中封装的就是 W3C 方案
# TouchAction 使用参考：https://www.cnblogs.com/liuhui0308/p/12033199.html#_lab2_0_2
# from appium.webdriver.common.touch_action import TouchAction
from time import sleep
from datetime import datetime
import os
import json
import importlib
import eventlet
from PIL import Image

from .config.connection_config import config_server, config_desired_caps_bijian_app
# from .config.upload_config import mobile_storage_folder,video_file_config_list,video_upload_config_list
from .auto_combine_video import del_files, video_root_path_name
from .edit_action.insert_visual_role import start_create_by_virsual_role_channel
from .edit_pubcover_action.main import main_func as edit_pubcover

config_desired_caps = config_desired_caps_bijian_app

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
    # 输出到日志文件
    logs_dir = '{0}auto_clip_video_byandroid/logs'.format(__ROOTPATH__)
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    # _log 前面改成当前的脚本文件名称
    f_path = '{0}/auto_upload_video_to_blibli_log_{1}.log'.format(logs_dir,cur_timestamp)
    # 写入文本
    fp = open(f_path,"a",encoding="utf-8")
    fp.write('{0}\n'.format(str_content))
    fp.close()

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

# @param rangstr: 范围字符串参数(格式如 '1:16')
# @param str_len: 控制序号字符串的长度，不足会自动补零，如果这个参数不写，会默认保持最大值的字符串长度，不足自动补零
# 例如：
# get_seirals_by_rangestr('3:6',2) 则输出 => ['03', '04', '05', '06']
# get_seirals_by_rangestr('3:6',2) 则输出 => ['01', '02', '03']
# get_seirals_by_rangestr('3:6',2) 则输出 => ['01', '02', '03']
# get_seirals_by_rangestr('2:',2) 则输出 => ['02', '03']
# get_seirals_by_rangestr(':',2) 则输出 => ['01', '02']
# rangstr 参数不符合条件的 则返回 None
# is_fill_zero 参数确定是否需要根据位数控制补零
def get_seirals_by_rangestr(rangstr,str_len=None,is_fill_zero=True):
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
        zero_fill = '0'*(0 if zero_fill_count < 0 else zero_fill_count) if is_fill_zero else ''
        out_str = '{0}{1}'.format(zero_fill,cur_ser)
        result.append(out_str)
    return result

def time_sleep(value):
    with eventlet.Timeout(30, False):  # 设置超时间
        sleep(value)

# 强制睡眠方法
def force_sleep(wait_sec):
    log_print(' ------ 强制等待，第 {} 秒 ----- '.format(wait_sec))
    time_sleep(wait_sec)

# 连接 appium 服务端 和 Android 设备
def connnect_android_device():
    log_print('开始连接 Android 设备...\n')

    global server
    global desired_caps
    global driver
    global wait

    # appium服务监听地址
    server = config_server
    # app启动参数
    desired_caps = config_desired_caps
    # 驱动
    driver = webdriver.Remote(server, desired_caps)
    wait = WebDriverWait(driver, 15)

# 读取已上传的视频记录文件，并判定当前视频是否已经上传过
# upload_video_file_name_full 是一个分段视频文件的完成名称(可包含扩展名)，如 silliconvalley1_01_01.mp4
def read_uploaded_remember_to_judge_isuploaded(upload_video_1th_name,upload_video_file_name_full):
    # log_print('--> 读取已上传的视频记录文件，并判定当前视频是否已经上传过 read_uploaded_remember_to_judge_isuploaded')
    # log_print('--> upload_video_1th_name => {} '.format(upload_video_1th_name))
    # log_print('--> upload_video_file_name_full => {} '.format(upload_video_file_name_full))
    # txt记录文件已 视频的 一级名称命名
    remember_file_name = upload_video_1th_name
    f_path = '{0}/{1}.txt'.format(upload_rember_path,remember_file_name)
    if not os.path.exists(f_path):
        log_print('{} --> 不存在'.format(f_path))
        return False
    for remember_line_ in open(f_path):
        remember_line = remember_line_.replace('\n','').replace('\r','').replace(error_black_video_suffix_flag,'').replace(error_suffix_flag,'')
        if remember_line == upload_video_file_name_full or remember_line in upload_video_file_name_full:
            log_print('-- 视频 【{}】 已经上传过了，此次不再上传 ---'.format(upload_video_file_name_full))
            return True
    log_print('{} --> 没有上传记录'.format(upload_video_file_name_full))
    return False

# 编辑发布时发生错误异常的视频文件，则存储记录时会打上这个错误记号(后缀)
error_suffix_flag = '_error'
error_black_video_suffix_flag = '_error_black'
# 将当前已成功发布到B站的视频记录下来，下次再执行程序时，会读取记录，并排除已发布过的视频
def write_uploaded_remember_txt(upload_video_1th_name,upload_video_2th_name,upload_video_episode,upload_video_paragraph_serial,error_file=False,is_black_video=False):
    # txt记录文件已 视频的 一级名称命名
    remember_file_name = upload_video_1th_name
    # 输出记录文件的目录
    # upload_rember_path
    if not os.path.exists(upload_rember_path):
        os.makedirs(upload_rember_path)

    # 如果是编辑发布时发生错误异常的视频文件，则存储记录时会打上错误记号(后缀)
    error_suffix = '' if error_file == False else (error_suffix_flag if not is_black_video else error_black_video_suffix_flag)
    # 每一行记录的名称，都跟要上传的视频分段文件名称保持一致，这样方便读取的时候可以直接进行比对
    video_file_name = '{0}_{1}_{2}{3}'.format(upload_video_2th_name,upload_video_episode,upload_video_paragraph_serial,error_suffix)
    
    # 如果记录已存在，那么不再重复记录
    if read_uploaded_remember_to_judge_isuploaded(upload_video_1th_name, video_file_name):
        return
    # _log 前面改成当前的脚本文件名称
    f_path = '{0}/{1}.txt'.format(upload_rember_path,remember_file_name)
    # 写入文本
    # 每一行记录的名称，都跟要上传的视频分段文件名称保持一致，这样方便读取的时候可以直接进行比对
    str_content = video_file_name
    fp = open(f_path,"a",encoding="utf-8") # 以追加模式写入
    fp.write('{0}\n'.format(str_content))  
    fp.close()

# 初始化所有所需目录
# 存放视频上传记录文件的目录
upload_rember_path = '{}auto_clip_video_byandroid/upload_rember'.format(__ROOTPATH__)
# 存放屏幕截图的目录
screen_shot_path = '{}auto_clip_video_byandroid/screen_shot'.format(__ROOTPATH__)
def initAllDir():
    if not os.path.exists(upload_rember_path):
        os.makedirs(upload_rember_path)
    if not os.path.exists(screen_shot_path):
        os.makedirs(screen_shot_path)

# 关闭提示弹窗 <已恢复上次编辑的草稿，是否继续编辑>
def close_last_edit_dialog():
    log_print('【*】检查是否存在提示弹窗 -- <已恢复上次编辑的草稿，是否继续编辑>')
    # 判定是否有提示弹窗 <已恢复上次编辑的草稿，是否继续编辑>
    last_edit_dialog = None
    try:
        last_edit_dialog = wait.until(EC.presence_of_element_located((By.ID, "{}ll_content".format(elementIdPrefix))))
        log_print('----- 发现弹窗，即将关闭')
    except:
        last_edit_dialog = None
        log_print('----- 未发现弹窗')
    if last_edit_dialog != None:
        # 关闭弹窗
        last_edit_dialog_cancel_btn = driver.find_element(AppiumBy.ID, "{}btn_negative".format(elementIdPrefix))
        last_edit_dialog_cancel_btn.click()

# 首页切换 底部的 tab 页签（根据页签标题切换）
def change_homepage_tab(tab_title):
    log_print(f'准备切换到<{tab_title}>页签')
    if tab_title == '我的':
        driver.tap([(936,2256)],10)
    elif tab_title == '学院':
        driver.tap([(673,2256)],10)
    elif tab_title == '素材集市':
        driver.tap([(395,2256)],10)
    elif tab_title == '创作':
        driver.tap([(132,2256)],10)
    log_print(f'已切换到<{tab_title}>页签')

# 开始创作视频的开始方式（终端提供选择）
def start_create():
    global editor_tool_audio_import_position
    global editor_tool_paster_position

    editor_tool_audio_import_position = {'val':None}
    editor_tool_paster_position = {'val':None}
    # 切换到页签 '我的' 画面
    change_homepage_tab('创作')
    force_sleep(1)
    
    if create_videw_type_selected['val'] == 2:
        result_params = start_create_by_virsual_role_channel(log_print,driver,force_sleep,elementIdPrefix)
        editor_tool_audio_import_position['val'] = result_params[0]
        editor_tool_paster_position['val'] = result_params[1]
    else:
        # 点击按钮 <开始创作>
        create_btn = driver.find_element(AppiumBy.ID, "{}card_video_clip".format(elementIdPrefix))
        create_btn.click()

''' 开始通过 <必剪 app> 上传视频 '''
def start_upload_video():
    force_sleep(3)
    # 判定是否有提示弹窗并关闭 <已恢复上次编辑的草稿，是否继续编辑>
    close_last_edit_dialog()
    force_sleep(3)

    # 开始创作视频的开始方式（终端提供选择）
    start_create()

    # 点击选项卡 <最近项目 - 文件夹>
    project_folder_tab = driver.find_element(AppiumBy.ID, "{}tab_folder".format(elementIdPrefix))
    project_folder_tab.click()
    # 点击列表项 <内部存储>
    inner_storage_item = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().textContains("内部存储")')
    inner_storage_item.click()
    # 点击特定存放要上传的视频文件的 特定文件夹 的选项
    video_folder_item = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().textContains("{}")'.format(mobile_storage_folder))
    video_folder_item.click()
    # [***] 正式开始 根据配置参数 选择视频文件，并进行编辑上传操作
    # [1] - 点击存放视频文件的 一级文件夹(即 auto_combine_video.py 最终输出的视频文件的文件夹)
    video_folder_root_item = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().textContains("{}")'.format(video_root_path_name))
    video_folder_root_item.click()
    # 存放所有要上传的视频文件的文件夹名称
    video_root_path = '{0}auto_clip_video_byandroid/{1}'.format(__ROOTPATH__,video_root_path_name)
    # 视频的一级目录（例如 一部美剧的名称 silliconvalley）
    video_show_list_1th = os.listdir(video_root_path)
    log_print('视频节目的 一级目录：\n{0}'.format(json.dumps(video_show_list_1th)))
    for video_show_1th_name in video_show_list_1th:
        try:
            # [2] - 点击存放视频文件的 一级节目文件夹
            log_print('# [2] - 点击存放视频文件的 一级节目文件夹')
            video_show_1th_item = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().textContains("{}")'.format(video_show_1th_name))
            video_show_1th_item.click()
            video_show_1th_path = '{0}/{1}'.format(video_root_path,video_show_1th_name)
        except Exception as ex:
            log_print('所需视频已全部上传完毕，如需上传更多片段，请更改 config/upload_config_files/ 目录下相应配置文件的 paragraph_serials 参数值')
            continue
        # 视频的一级目录（例如 一部美剧的名称分季名称 silliconvalley1 表示 silliconvalley第一季）
        video_show_list_2th = os.listdir(video_show_1th_path)
        log_print('视频节目的 二级目录：\n{0}'.format(json.dumps(video_show_list_2th)))
        for video_show_2th_name in video_show_list_2th:
            # [3] - 点击存放视频文件的 二级节目文件夹
            log_print('# [3] - 点击存放视频文件的 二级节目文件夹')
            video_show_2th_item = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().textContains("{}")'.format(video_show_2th_name))
            video_show_2th_item.click()
            # [4] - 点击存放视频文件的 输出视频文件夹 这个文件夹名称是固定不变的
            log_print('# [4] - 点击存放视频文件的 输出视频文件夹 这个文件夹名称是固定不变的 fullfiles')
            fullfiles_folder = 'fullfiles'
            video_show_fullfiles_folder_item = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().textContains("{}")'.format(fullfiles_folder))
            video_show_fullfiles_folder_item.click()
            # 读取具体的视频文件名称列表
            video_show_files_path = '{0}/{1}/{2}'.format(video_show_1th_path,video_show_2th_name,fullfiles_folder)
            video_show_files_list = os.listdir(video_show_files_path)
            log_print('视频节目的 具体的视频文件列表：\n{0}'.format(json.dumps(video_show_files_list)))
            for video_show_file in video_show_files_list:
                is_need_upload = False # 此次是否需要上传的标识
                # 视频一级名称
                upload_video_1th_name = ''
                # 视频二级名称
                upload_video_2th_name = ''
                # 视频分集号
                upload_video_episode = ''
                # 视频某一集的分段号
                upload_video_paragraph_serial = ''
                # 分区
                upload_channel = '' #: '生活,日常',
                # 标题（这个标题决定固定的前缀，实际标题后面会动态追加当前上传的视频 第几集 第几段 的参数）
                upload_title = '' #: '坚持学习英语口语--练习材料--《美剧：硅谷》--第{0}季，第{1}集，材料{2}',
                # 类型
                upload_type = '' #: '自制',
                # 标签
                upload_tags = '' #: '生活,学习,分享',
                # 标签--参与话题
                upload_tags_subject = '' #: '打工人职场生态图鉴',
                # 简介
                instroduction = ''
                # 动态
                upload_dynamic = '' #: '加油！坚持学习英语口语--练习材料--《美剧：硅谷》'
                cover_type = ''
                cover_item = ''
                cover_text_list = ''
                # if not 'silliconvalley1_03' in video_show_file:
                #     continue
                # 遍历 视频上传配置参数 只有在配置参数里有配置的视频，才进行上传
                need_upload_video_file_name = ''
                for need_upload_config_item in video_upload_config_list:
                    if need_upload_config_item['first_name'] == video_show_1th_name and need_upload_config_item['second_name'] == video_show_2th_name:
                        # 要上传的视频分集号数组
                        need_upload_video_episode_list = []
                        # 先尝试是否为 '2:6' 类似这样的范围字符串，如果不是则会返回 None
                        need_upload_video_episode_list = get_seirals_by_rangestr(need_upload_config_item['episode_list'],2)
                        if need_upload_video_episode_list == None:
                            # 如果不是范围字符串，那就只能是 '01,02,03' 类似这样的 都好分隔的字符串
                            need_upload_video_episode_list = need_upload_config_item['episode_list'].split(',')
                        # 要上传的视频某一集的分段号数组
                        need_upload_video_paragraph_serials_list = []
                        # 先尝试是否为 '2:6' 类似这样的范围字符串，如果不是则会返回 None
                        need_upload_video_paragraph_serials_list = get_seirals_by_rangestr(need_upload_config_item['paragraph_serials'],2)
                        if need_upload_video_paragraph_serials_list == None:
                            # 如果不是范围字符串，那就只能是 '01,02,03' 类似这样的 都好分隔的字符串
                            need_upload_video_paragraph_serials_list = need_upload_config_item['paragraph_serials'].split(',')
                        for need_upload_video_episode in need_upload_video_episode_list:
                            for need_upload_video_paragraph_serial in need_upload_video_paragraph_serials_list:
                                need_upload_video_file_name = '{0}_{1}_{2}'.format(need_upload_config_item['second_name'],need_upload_video_episode,need_upload_video_paragraph_serial)
                                if need_upload_video_file_name in video_show_file:
                                    is_need_upload = True
                                    # 视频一级名称
                                    upload_video_1th_name = need_upload_config_item['first_name']
                                    # 视频二级名称
                                    upload_video_2th_name = need_upload_config_item['second_name']
                                    # 视频分集号
                                    upload_video_episode = need_upload_video_episode
                                    # 视频某一集的分段号
                                    upload_video_paragraph_serial = need_upload_video_paragraph_serial
                                    # 分区
                                    upload_channel = need_upload_config_item['upload_channel'] #: '生活,日常',
                                    # 标题（这个标题决定固定的前缀，实际标题后面会动态追加当前上传的视频 第几集 第几段 的参数）
                                    upload_title = need_upload_config_item['upload_title'] #: '坚持学习英语口语--练习材料--《美剧：硅谷》--第{0}季，第{1}集，材料{2}',
                                    # 类型
                                    upload_type = need_upload_config_item['upload_type'] #: '自制',
                                    # 标签
                                    upload_tags = need_upload_config_item['upload_tags'] #: '生活,学习,分享',
                                    # 标签--参与话题
                                    upload_tags_subject = need_upload_config_item['upload_tags_subject'] #: '打工人职场生态图鉴',
                                    # 简介
                                    instroduction = need_upload_config_item['instroduction']
                                    # 动态
                                    upload_dynamic = need_upload_config_item['upload_dynamic'] #: '加油！坚持学习英语口语--练习材料--《美剧：硅谷》'
                                    cover_type = need_upload_config_item['cover_type']
                                    cover_item = need_upload_config_item['cover_item']
                                    cover_text_list = need_upload_config_item['cover_text_list']
                                    break
                            if is_need_upload:
                                break
                # 配置参数里没有的，或者，当前视频片段已经上传过了 -- 都不会进行上传
                if read_uploaded_remember_to_judge_isuploaded(video_show_1th_name,need_upload_video_file_name):
                    is_need_upload = False
                    continue
                elif not is_need_upload:
                    continue
                log_print('\n------- 选择视频文件 ------\n{0}\n'.format(video_show_file))
                # [5] - 点击存放视频文件的 二级节目文件夹（这一级是特意加的跟文件名同名的一层文件夹）
                log_print('# [5] - 点击存放视频文件的 二级节目文件夹（这一级是特意加的跟文件名同名的一层文件夹）')
                video_show_file_floder_item = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().textContains("{}")'.format(video_show_file))
                video_show_file_floder_item.click()
                # [5.1] - 点击存放视频文件的 二级节目文件夹（这一级则是具体的视频文件了）
                log_print('[5.1] - 点击存放视频文件的 二级节目文件夹（这一级则是具体的视频文件了）')
                video_show_file_item = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().textContains("{}")'.format(video_show_file))
                video_show_file_item.click()
                # [6] - 点击按钮 <下一步>
                log_print('[6] - 点击按钮 <下一步>')
                video_select_next_step_btn = driver.find_element(AppiumBy.ID, "{}activity_material_next_tv".format(elementIdPrefix))
                video_select_next_step_btn.click()
                force_sleep(10)
                try:
                    # --------- 进入视频编辑画面 -------------
                    log_print('\n------- 进入视频编辑画面，开始编辑视频 ------\n{0}\n'.format(video_show_file))
                    # [***] - (不同的视频可以对应不同的剪辑脚本)动态引入对应当前视频的剪辑操作模块，并调用其中的执行函数
                    # 动态引入脚本
                    edit_action_module_str = "auto_clip_video_byandroid.video_action.{0}.{1}".format(upload_video_1th_name,upload_video_2th_name)
                    edit_action_module = importlib.import_module(edit_action_module_str)
                    edit_action_module.edit_video_action(log_print,driver,force_sleep,video_file_config_list,video_show_1th_name,video_show_2th_name,elementIdPrefix,video_show_file,editor_tool_audio_import_position['val'],editor_tool_paster_position['val'])
                    
                    # ------------------------- 发布视频 -------------
                    log_print('\n--------------------- 正在进行 【发布视频】 ------------------------\n')

                    # 执行在 发布视频 画面 填写发布信息的操作
                    pub_video_action(elementIdPrefix,upload_channel,upload_title,upload_video_2th_name,upload_video_1th_name,upload_video_episode,upload_video_paragraph_serial,upload_type,upload_tags_subject,upload_tags,instroduction,upload_dynamic,cover_type,cover_item,cover_text_list)
                except Exception as ex:
                    upload_title_full = upload_title.format(upload_video_2th_name.replace(upload_video_1th_name,''),upload_video_episode,upload_video_paragraph_serial)
                    sufix_list = str(ex).split(',')
                    is_black_video = True if len(sufix_list) > 0 and sufix_list[0] == 'black' else False
                    log_print(f'【{upload_title_full}】视频编辑发布上传发生异常: {ex}')
                    # [***] - 将当前未成功发布到B站的视频记录下来，作为错误文件，打上错误标记，下次再执行程序时，会读取记录，并排除已发布过的视频
                    write_uploaded_remember_txt(upload_video_1th_name,upload_video_2th_name,upload_video_episode,upload_video_paragraph_serial,True,is_black_video)
                    log_print(f'操作完成 【[{upload_title_full}] - 错误无法发布视频到B站，即将重启任务】\n')
                    force_sleep(6)
                    # 重启任务（不用单选需要重新选择，程序已记录下前面的选择项，静静等待即可)
                    log_print('---------- 重启任务（不用单选需要重新选择，程序已记录下前面的选择项，静静等待即可) ---------------')
                    start_program()
                # ------------------------- 视频已进行发布，此时返回到了主菜单画面，且定位在 <我的> 页签上，需要切换到 <创作> 页签的画面 -------------
                log_print('\n------- 正在进行 【视频已进行发布，此时返回到了主菜单画面，且定位在 <我的> 页签上，需要切换到 <创作> 页签的画面】 ------\n')
                
                log_print('操作完成 【切换到 <创作> 页签的画面】\n')
                log_print('\n即将进行下一轮视频的上传操作\n')
                force_sleep(30)
                # [30] - 点击页签 <创作>
                driver.tap([(126,2260)],10)
                # 重新开始新一轮的视频上传操作
                start_upload_video()
                return

# 图片吸色
# 参考地址：https://blog.csdn.net/qq_21478261/article/details/107052418
def getImgColor(img_path):
    # img_path = 'mh.jpg'
    image = Image.open(img_path)
    
    # 要提取的主要颜色数量
    num_colors = 1 
    small_image = image.resize((80, 80))
    result = small_image.convert('P', palette=Image.ADAPTIVE, colors=num_colors)
    result = result.convert('RGB')
    main_colors = result.getcolors()

    log_print("吸到的颜色：{}".format(main_colors))
    # log_print("吸到的颜色：{}".format(main_colors[0][1]))
    return main_colors

# 对视频导出检查操作的屏幕截图进行裁剪出可以用于检查的图片部分
def cut_img_for_check_video_shot(img_path,video_shot_img_tmp_path,video_shot_img_name):
    img = Image.open(img_path)
    img_size = img.size
    img_w = img_size[0]
    img_h = img_size[1]
    log_print(f'图片的尺寸{img.size}')
    sub_val_w = int(img_w * 0.2)
    sub_val_h = int(img_h * 0.16)
    crop_h = int(img_h * 0.26)
    cropped = img.crop((sub_val_w, sub_val_h, (img_w - sub_val_w), crop_h)) # (left, upper, right, lower)
    cut_img_path = f'{video_shot_img_tmp_path}/{video_shot_img_name}_cut.png'
    cropped.save(cut_img_path)
    return cut_img_path

# 检测视频是否正常（经常出现有的视频发布的时候，导出时一片黑的情况，凡是出现这种情况均直接跳过该视频）
def check_video_action():
    log_print('\n------------------- 检查视频是否导出正常：有无出现黑屏现象（请确保当前一定在发布页面） -------------------\n')
    
    # 存放临时截图的目录
    video_shot_img_tmp_path = f'{screen_shot_path}/tmp'
    if not os.path.exists(video_shot_img_tmp_path):
        os.makedirs(video_shot_img_tmp_path)

    # 屏幕截图
    video_shot_img_name = 'video_shot_img'
    video_shot_img = f'{video_shot_img_name}.png'
    video_shot_img_path = f'{video_shot_img_tmp_path}/{video_shot_img}'
    driver.save_screenshot(video_shot_img_path)
    # 获取截图
    driver.get_screenshot_as_file(video_shot_img_path)

    # 对图片进行裁剪，裁剪出可以用于检测视频的区域
    cut_img_path = cut_img_for_check_video_shot(video_shot_img_path,video_shot_img_tmp_path,video_shot_img_name)

    # 读取刚才的截图，判定其主要颜色是否为黑色，若是黑色则认为出现了黑屏现象
    # 判定是否大多数主要颜色都是黑色
    main_colors = getImgColor(cut_img_path)
    if (main_colors[0][1][0] == 0 and main_colors[0][1][1] == 0 and main_colors[0][1][2] == 0) \
        or (main_colors[0][1][0] == 23 and main_colors[0][1][1] == 21 and main_colors[0][1][2] == 28):
        return False

    return True

def pub_video_action(elementIdPrefix,upload_channel,upload_title,upload_video_2th_name,upload_video_1th_name,upload_video_episode,upload_video_paragraph_serial,upload_type,upload_tags_subject,upload_tags,instroduction,upload_dynamic,cover_type,cover_item,cover_text_list):
    # 检测视频是否正常（经常出现有的视频发布的时候，导出时一片黑的情况，凡是出现这种情况均直接跳过该视频）
    valid_pass = check_video_action()
    if not valid_pass:
        raise Exception('black,视频导出异常 -- 出现黑屏情况')
    else:
        pub_video_action_func(elementIdPrefix,upload_channel,upload_title,upload_video_2th_name,upload_video_1th_name,upload_video_episode,upload_video_paragraph_serial,upload_type,upload_tags_subject,upload_tags,instroduction,upload_dynamic,cover_type,cover_item,cover_text_list)

# 执行在 发布视频 画面 填写发布信息的操作
def pub_video_action_func(elementIdPrefix,upload_channel,upload_title,upload_video_2th_name,upload_video_1th_name,upload_video_episode,upload_video_paragraph_serial,upload_type,upload_tags_subject,upload_tags,instroduction,upload_dynamic,cover_type,cover_item,cover_text_list):
    log_print('\n------- 执行在发布视频画面的填写发布信息的操作 ------\n')
    # [23] - 点击区域 <分区>
    pub_channel_layout = driver.find_element(AppiumBy.ID, "{}publish_district_area_cl".format(elementIdPrefix))
    pub_channel_layout.click()
    # 根据配置参数 选择具体分区
    for upload_channel_item in upload_channel.split(','):
        # [23.1] - 选择具体分区
        pub_channel_select_layout = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().textContains("{}")'.format(upload_channel_item))
        pub_channel_select_layout.click()
    # [24] - 输入 <标题>
    #: '坚持学习英语口语--练习材料--《美剧：硅谷》--第{0}季，第{1}集，材料{2}'
    upload_title_full = upload_title.format(upload_video_2th_name.replace(upload_video_1th_name,''),upload_video_episode,upload_video_paragraph_serial)
    log_print('输入 <标题>\n{}'.format(upload_title_full))
    pub_title_input = driver.find_element(AppiumBy.ID, "{}publish_title_area_title_et".format(elementIdPrefix))
    pub_title_input.send_keys(u'{}'.format(upload_title_full))
    # [24.1] - 输入内容 <动态> 由于点击下面的操作后，画面很可能就不够显示了，所以趁现在先把动态填写好
    pub_dynamic_input = driver.find_element(AppiumBy.ID, "{}publish_feed_area_et".format(elementIdPrefix))
    pub_dynamic_input.send_keys(upload_dynamic)
    # [24.2] - 点击链接按钮 <查看更多选项> 
    pub_see_more_link = driver.find_element(AppiumBy.ID, "{}publish_more_area_show_more_tv".format(elementIdPrefix))
    pub_see_more_link.click()
    # [24.3] - 输入内容 <简介> 此时画面中正好能看到简介的输入区域（由于点击下面的操作后，画面很可能就不够显示了，所以趁现在先把简介填写好）
    pub_introduction_input = driver.find_element(AppiumBy.ID, "{}publish_more_area_intro_et".format(elementIdPrefix))
    pub_introduction_input.send_keys(instroduction)
    # [25] - 点击单选 根据配置参数 选择视频类型
    pub_type_radio = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().textContains("{}")'.format(upload_type))
    pub_type_radio.click()
    # [26] - 点击开关 <禁止转载>
    pub_reprint_switch = driver.find_element(AppiumBy.ID, "{}publish_type_area_self_made_permit_reprint_cb".format(elementIdPrefix))
    pub_reprint_switch.click()
    # [27] - 点击标签区域
    pub_tags_layout = driver.find_element(AppiumBy.ID, "{}publish_tags_area_cl".format(elementIdPrefix))
    pub_tags_layout.click()
    force_sleep(6)
    # 根据配置参数，输入标签
    # [27.1] - 标签 <参与话题> 选择
    for pub_tag_str in upload_tags_subject.split(','):
        # [27.1.1] - 点击按钮 参与话题的 <搜索>
        pub_tag_subject_select_search_btn = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().textContains("搜索")')
        pub_tag_subject_select_search_btn.click()
        log_print('[27.1.1] - 点击按钮 参与话题的 <搜索>')
        force_sleep(3)
        # [27.1.2] - 在搜索输入框里输入内容
        pub_tag_subject_select_search_input = driver.find_element(AppiumBy.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.webkit.WebView/android.webkit.WebView/android.view.View/android.view.View[5]/android.view.View[1]/android.view.View[1]/android.widget.EditText')
        pub_tag_subject_select_search_input.click()
        log_print('[27.1.2] - 点击输入框，获取焦点，弹出软键盘')
        force_sleep(3)
        pub_tag_subject_select_search_input.send_keys(u'{0}'.format(pub_tag_str))
        log_print('[27.1.2] - 在搜索输入框里输入内容: \n{}\n'.format(pub_tag_str))
        force_sleep(3)
        # 按下回车键
        driver.press_keycode(66)
        log_print('[27.1.2] - 按下回车键')
        force_sleep(2)
        try:
            # [27.1.3] - 点击搜到的 话题 选项 (选择第一条，最匹配的一条即可)
            pub_tag_subject_select_layout = driver.find_element(AppiumBy.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.webkit.WebView/android.webkit.WebView/android.view.View/android.view.View[5]/android.view.View[2]/android.widget.ListView/android.view.View[1]/android.view.View[1]')
            pub_tag_subject_select_layout.click()
            log_print('[27.1.3] - 点击搜到的 话题 选项:\n{}\n'.format(pub_tag_str))
            
            # [27.1.4] - 此时话题搜索弹窗会自动关闭，只要继续下一轮循环就能，进行下一轮的话题参与搜索选择了
            log_print('[27.1.4] - 此时话题搜索弹窗会自动关闭，只要继续下一轮循环就能，进行下一轮的话题参与搜索选择了')
            force_sleep(2)
        except:
            log_print('标签 <参与话题：{0}> 选择失败，可能是没找到'.format(pub_tag_str))
    force_sleep(2)
    # # [27.1.4] - 点击按钮 <取消> 撤出 话题选择弹窗
    # pub_tag_subject_select_back_btn = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().textContains("取消")')
    # pub_tag_subject_select_back_btn.click()
    # log_print('[27.1.4] - 点击按钮 <取消> 撤出 话题选择弹窗')
    # [27.2] - 标签 <普通话题> 输入
    for pub_tag_str in upload_tags.split(','):
        # [27.2.1] - 在搜索输入框里输入内容
        pub_tag_input = driver.find_element(AppiumBy.CLASS_NAME,'android.widget.EditText')
        pub_tag_input.send_keys(u'{0}'.format(pub_tag_str))
        force_sleep(2)
        # 焦点定位在输入框里，让手机弹出软键盘
        pub_tag_input.click()
        force_sleep(2)
        # [27.2.2] - 点击按钮 <添加>
        # pub_tag_add_btn = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().textContains("添加")')
        # pub_tag_add_btn.click()
        # driver.tap([(802,564)],10)
        driver.press_keycode(66) # 回车键
        force_sleep(2)
    force_sleep(2)
    # [28] - 点击按钮 <完成> 标签设定完成
    pub_tag_confirm_btn = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().textContains("完成")')
    pub_tag_confirm_btn.click()

    # 修改封面操作
    edit_pubcover(log_print,driver,force_sleep,elementIdPrefix,cover_type,cover_item,cover_text_list)

    log_print('操作完成 【导出视频】\n')
    # ------------------------- 发布视频到B站 -------------
    log_print('\n------- 正在进行 【发布视频到B站】 ------\n')
    # [29] - 点击按钮 <发布B站 每日瓜分奖金> 标签设定完成
    # try:
    #     pub_video_to_bilibili_btn = driver.find_element(AppiumBy.ID,"{}activity_publish_publish_tv".format(elementIdPrefix))
    #     pub_video_to_bilibili_btn.click()
    # except:
    #     driver.tap([(655,2216)],10)
    driver.tap([(655,2216)],10)
    # [30] - 将当前已成功发布到B站的视频记录下来，下次再执行程序时，会读取记录，并排除已发布过的视频
    write_uploaded_remember_txt(upload_video_1th_name,upload_video_2th_name,upload_video_episode,upload_video_paragraph_serial)
    log_print(f'操作完成 【[{upload_title_full}] - 已发布视频到B站】\n')
    force_sleep(6)

# 终端询问选择哪个视频节目的配置参数
def ask_select_upload_config(multi_select_enabled=False,is_pub=True):
    # 视频一级名称
    upload_video_1th_name = ''
    # 视频二级名称
    upload_video_2th_name = ''
    # 视频分集号
    upload_video_episode = ''
    # 视频某一集的分段号
    upload_video_paragraph_serial = ''
    # 分区
    upload_channel = '' #: '生活,日常',
    # 标题（这个标题决定固定的前缀，实际标题后面会动态追加当前上传的视频 第几集 第几段 的参数）
    upload_title = '' #: '坚持学习英语口语--练习材料--《美剧：硅谷》--第{0}季，第{1}集，材料{2}',
    # 类型
    upload_type = '' #: '自制',
    # 标签
    upload_tags = '' #: '生活,学习,分享',
    # 标签--参与话题
    upload_tags_subject = '' #: '打工人职场生态图鉴',
    # 简介
    instroduction = ''
    # 动态
    upload_dynamic = '' #: '加油！坚持学习英语口语--练习材料--《美剧：硅谷》'
    cover_type = ''
    cover_item = ''
    cover_text_list = ''

    if is_pub:
        log_print('\n----------------【注意：】 请确保已经提前定位在视频的发布画面 --------------------\n')
    log_print('\n---------------- 请选择你要填写的配置参数（请根据 title 选择）： --------------------')
    if multi_select_enabled:
        log_print('---- 需多选的话，请按照这种格式进行输入（必须英文状态下输入）：\n1:5\n---------------------------------------')

    # 收集根据分集和分段拆分后的完整的发布参数配置列表
    select_video_params_list = []
    select_idx = 1 # 提供选择的序号
    for params in video_upload_config_list:
        # 视频一级名称
        upload_video_1th_name = params['first_name']
        # 视频二级名称
        upload_video_2th_name = params['second_name']
        # # 视频分集号
        # upload_video_episode = need_upload_video_episode
        # # 视频某一集的分段号
        # upload_video_paragraph_serial = need_upload_video_paragraph_serial
        # 分区
        upload_channel = params['upload_channel'] #: '生活,日常',
        # 标题（这个标题决定固定的前缀，实际标题后面会动态追加当前上传的视频 第几集 第几段 的参数）
        upload_title = params['upload_title'] #: '坚持学习英语口语--练习材料--《美剧：硅谷》--第{0}季，第{1}集，材料{2}',
        # 类型
        upload_type = params['upload_type'] #: '自制',
        # 标签
        upload_tags = params['upload_tags'] #: '生活,学习,分享',
        # 标签--参与话题
        upload_tags_subject = params['upload_tags_subject'] #: '打工人职场生态图鉴',
        # 简介
        instroduction = params['instroduction']
        # 动态
        upload_dynamic = params['upload_dynamic'] #: '加油！坚持学习英语口语--练习材料--《美剧：硅谷》'
        cover_type = params['cover_type']
        cover_item = params['cover_item']
        cover_text_list = params['cover_text_list']

        # [*] - 要上传的视频分集号数组
        need_upload_video_episode_list = []
        # 先尝试是否为 '2:6' 类似这样的范围字符串，如果不是则会返回 None
        need_upload_video_episode_list = get_seirals_by_rangestr(params['episode_list'],2)
        if need_upload_video_episode_list == None:
            # 如果不是范围字符串，那就只能是 '01,02,03' 类似这样的 都好分隔的字符串
            need_upload_video_episode_list = params['episode_list'].split(',')

        # [*] - 要上传的视频某一集的分段号数组
        need_upload_video_paragraph_serials_list = []
        # 先尝试是否为 '2:6' 类似这样的范围字符串，如果不是则会返回 None
        need_upload_video_paragraph_serials_list = get_seirals_by_rangestr(params['paragraph_serials'],2)
        if need_upload_video_paragraph_serials_list == None:
            # 如果不是范围字符串，那就只能是 '01,02,03' 类似这样的 都好分隔的字符串
            need_upload_video_paragraph_serials_list = params['paragraph_serials'].split(',')

        # [**] - 遍历 分集 和 分段 数组拆分出所有的填写列表
        for episode in need_upload_video_episode_list:
            for paragraph_serial in need_upload_video_paragraph_serials_list:
                video_params_item = {
                    # 一级目录(文件夹名)
                    'first_name':  params['first_name'],
                    # 二级目录脚本文件(.py 脚本文件名) [即上面一个目录下的具体文件]
                    'second_name':  params['second_name'], # 表示 第 N 季
                    # 第N集
                    "episode": episode,
                    # 要上传的视频分段的序号（视频分段文件的完整名称例如 silliconvalley1_01.mp4 只要知道分段序号就能拼接出完整的视频文件路径）
                    'paragraph_serial':paragraph_serial,
                    # ------ <必剪 app> 导出画面里要填写的相关参数 start -----------
                    # 分区
                    'upload_channel':  params['upload_channel'],
                    # 标题（这个标题决定固定的前缀，实际标题后面会动态追加当前上传的视频 第几集 第几段 的参数）
                    'upload_title':  params['upload_title'],
                    # 类型
                    'upload_type':  params['upload_type'],
                    # 标签
                    'upload_tags':  params['upload_tags'],
                    # 标签--参与话题（请只设置一项即可）（注：经测试话题参与只能选一项，虽然我程序里支持多项，但是就设置了多项，<必剪 app>也会把后一项覆盖前一项）
                    # 'upload_tags_subject': '2022年新年锦鲤,2022第一次打卡',
                    'upload_tags_subject':  params['upload_tags_subject'],
                    # 简介
                    'instroduction': params['instroduction'],
                    # 动态
                    'upload_dynamic':  params['upload_dynamic'],
                    # 封面修改功能
                    # 封面类型页签（目前仅支持这个）
                    'cover_type': params['cover_type'],
                    # 封面类型页签下的 具体封面选项（行号，列号）（目前仅支持这个）
                    'cover_item': params['cover_item'],
                    # 封面中文本的内容，不同的封面选项有不同数量的文本，需要使用者自己清楚要修改哪些文本，如果为空的，则不会修改原来的文本
                    # 填入规则是：从上到下 > 从左到右 依次把 cover_text_list 列表中的内容进行填入（cover_text_list 中若内容数量缺少则不修改，若有多余的则不管）
                    'cover_text_list': params['cover_text_list'],
                }
                select_video_params_list.append(video_params_item)
                #: '坚持学习英语口语--练习材料--《美剧：硅谷》--第{0}季，第{1}集，材料{2}'
                video_title = params['upload_title'].format(params['second_name'].replace(params['first_name'],''),episode,paragraph_serial)
                log_print(f'[{select_idx}] - {video_title}')
                select_idx += 1
    len_select_video_params_list = len(select_video_params_list)
    video_select = input()

    # 记录多选的内容
    multi_selected = []
    if multi_select_enabled and not is_int_str(video_select):
        # 判定是否为范围字符串（1:5）
        video_select = str(video_select)
        select_result = []
        range_ary = video_select.split(':')
        if len(range_ary) == 2:
            start_idx = 0 if not is_int_str(range_ary[0]) or int(range_ary[0]) > len_select_video_params_list else int(range_ary[0]) - 1
            end_idx = start_idx + 1 if not is_int_str(range_ary[1]) or int(range_ary[1]) > len_select_video_params_list else int(range_ary[1])
            multi_selected = select_video_params_list[start_idx:end_idx]
            for p_idx,params in enumerate(multi_selected):
                # 已选择
                video_title = params['upload_title'].format(params['second_name'].replace(params['first_name'],''),params['episode'],params['paragraph_serial'])
                log_print(f'已选择：[{p_idx+1}] - {video_title}')

                # 视频一级名称
                upload_video_1th_name = params['first_name']
                # 视频二级名称
                upload_video_2th_name = params['second_name']
                # 视频分集号
                upload_video_episode = params['episode']
                # 视频某一集的分段号
                upload_video_paragraph_serial = params['paragraph_serial']
                # 分区
                upload_channel = params['upload_channel'] #: '生活,日常',
                # 标题（这个标题决定固定的前缀，实际标题后面会动态追加当前上传的视频 第几集 第几段 的参数）
                upload_title = params['upload_title'] #: '坚持学习英语口语--练习材料--《美剧：硅谷》--第{0}季，第{1}集，材料{2}',
                # 类型
                upload_type = params['upload_type'] #: '自制',
                # 标签
                upload_tags = params['upload_tags'] #: '生活,学习,分享',
                # 标签--参与话题
                upload_tags_subject = params['upload_tags_subject'] #: '打工人职场生态图鉴',
                # 简介
                instroduction = params['instroduction']
                # 动态
                upload_dynamic = params['upload_dynamic'] #: '加油！坚持学习英语口语--练习材料--《美剧：硅谷》'
                cover_type = params['cover_type']
                cover_item = params['cover_item']
                cover_text_list = params['cover_text_list']
                # 把多选的参数都收集起来
                select_result.append([upload_channel,upload_title,upload_video_2th_name,upload_video_1th_name,upload_video_episode,upload_video_paragraph_serial,upload_type,upload_tags_subject,upload_tags,instroduction,upload_dynamic,cover_type,cover_item,cover_text_list])
        return select_result
    else:
        video_select = 1 if not is_int_str(video_select) or int(video_select) < 1 or int(video_select) > len_select_video_params_list else int(video_select)
        # 已选择
        params = select_video_params_list[video_select-1]
        video_title = params['upload_title'].format(params['second_name'].replace(params['first_name'],''),params['episode'],params['paragraph_serial'])
        log_print(f'已选择：[{video_select}] - {video_title}')

        # 视频一级名称
        upload_video_1th_name = params['first_name']
        # 视频二级名称
        upload_video_2th_name = params['second_name']
        # 视频分集号
        upload_video_episode = params['episode']
        # 视频某一集的分段号
        upload_video_paragraph_serial = params['paragraph_serial']
        # 分区
        upload_channel = params['upload_channel'] #: '生活,日常',
        # 标题（这个标题决定固定的前缀，实际标题后面会动态追加当前上传的视频 第几集 第几段 的参数）
        upload_title = params['upload_title'] #: '坚持学习英语口语--练习材料--《美剧：硅谷》--第{0}季，第{1}集，材料{2}',
        # 类型
        upload_type = params['upload_type'] #: '自制',
        # 标签
        upload_tags = params['upload_tags'] #: '生活,学习,分享',
        # 标签--参与话题
        upload_tags_subject = params['upload_tags_subject'] #: '打工人职场生态图鉴',
        # 简介
        instroduction = params['instroduction']
        # 动态
        upload_dynamic = params['upload_dynamic'] #: '加油！坚持学习英语口语--练习材料--《美剧：硅谷》'
        cover_type = params['cover_type']
        cover_item = params['cover_item']
        cover_text_list = params['cover_text_list']

        return [upload_channel,upload_title,upload_video_2th_name,upload_video_1th_name,upload_video_episode,upload_video_paragraph_serial,upload_type,upload_tags_subject,upload_tags,instroduction,upload_dynamic,cover_type,cover_item,cover_text_list]

# 仅执行在 发布视频画面 填写表单的操作
def start_fill_pub_forms():
    force_sleep(3)
    # 判定是否有提示弹窗并关闭 <已恢复上次编辑的草稿，是否继续编辑>
    close_last_edit_dialog()
    force_sleep(3)

    # 切换到页签 '我的' 画面
    change_homepage_tab('我的')
    
    # 终端询问选择哪个视频节目的配置参数
    upload_channel,upload_title,upload_video_2th_name,upload_video_1th_name,upload_video_episode,upload_video_paragraph_serial,upload_type,upload_tags_subject,upload_tags,instroduction,upload_dynamic,cover_type,cover_item,cover_text_list = ask_select_upload_config()
    # 执行在 发布视频 画面 填写发布信息的操作
    pub_video_action(elementIdPrefix,upload_channel,upload_title,upload_video_2th_name,upload_video_1th_name,upload_video_episode,upload_video_paragraph_serial,upload_type,upload_tags_subject,upload_tags,instroduction,upload_dynamic,cover_type,cover_item,cover_text_list)

# =================== 生成放置 分段 视频文件的目录 start ==============

# 创建放置视频的文件夹目录的具体操作
def mkdir_video_folder_one(params):
    # 终端询问选择哪个视频节目的配置参数
    upload_channel,upload_title,upload_video_2th_name,upload_video_1th_name,upload_video_episode,upload_video_paragraph_serial,upload_type,upload_tags_subject,upload_tags,instroduction,upload_dynamic,cover_type,cover_item,cover_text_list = params
    # auto_clip_video_byandroid/video/
    video_dir = f'{__ROOTPATH__}auto_clip_video_byandroid/video'
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)
    # 节目名称 目录
    video_1th_name_dir = f'{video_dir}/{upload_video_1th_name}'
    if not os.path.exists(video_1th_name_dir):
        os.makedirs(video_1th_name_dir)
    # 节目 分季的名称 目录
    video_2th_name_dir = f'{video_1th_name_dir}/{upload_video_2th_name}'
    if not os.path.exists(video_2th_name_dir):
        os.makedirs(video_2th_name_dir)
    # 节目 视频文件的存放 目录
    upload_video_episode = f'0{upload_video_episode}' if len(str(upload_video_episode)) < 2 else str(upload_video_episode)
    upload_video_paragraph_serial = f'0{upload_video_paragraph_serial}' if len(str(upload_video_paragraph_serial)) < 2 else str(upload_video_paragraph_serial)
    video_file_dir = f'{video_2th_name_dir}/fullfiles/{upload_video_2th_name}_{upload_video_episode}_{upload_video_paragraph_serial}'
    if not os.path.exists(video_file_dir):
        os.makedirs(video_file_dir)

# 创建放置视频的文件夹目录（判定是否为批量创建）
def mkdir_video_folder():
    # 终端询问选择哪个视频节目的配置参数
    ask_select_upload_config_result = ask_select_upload_config(True,False)
    if isinstance(ask_select_upload_config_result[0],list):
        # 如果返回的参数时二维数组，则说明用户进行了多选，则进行批量创建目录
        for params in ask_select_upload_config_result:
            mkdir_video_folder_one(params)
    else:
        mkdir_video_folder_one(ask_select_upload_config_result)

# =================== 生成放置 分段 视频文件的目录 end =============

# =================== 生成放置 完整 视频文件的目录 start ==============

# 终端询问选择哪个视频节目的配置参数
def ask_select_mkfullvideodir_config(multi_select_enabled=False):
    # 视频一级名称
    upload_video_1th_name = ''
    # 视频二级名称
    upload_video_2th_name = ''
    # 视频分集号
    upload_video_episode = ''
    # 视频某一集的分段号
    upload_video_paragraph_serial = ''
    # 分区
    upload_channel = '' #: '生活,日常',
    # 标题（这个标题决定固定的前缀，实际标题后面会动态追加当前上传的视频 第几集 第几段 的参数）
    upload_title = '' #: '坚持学习英语口语--练习材料--《美剧：硅谷》--第{0}季，第{1}集，材料{2}',
    # 类型
    upload_type = '' #: '自制',
    # 标签
    upload_tags = '' #: '生活,学习,分享',
    # 标签--参与话题
    upload_tags_subject = '' #: '打工人职场生态图鉴',
    # 简介
    instroduction = ''
    # 动态
    upload_dynamic = '' #: '加油！坚持学习英语口语--练习材料--《美剧：硅谷》'
    cover_type = ''
    cover_item = ''
    cover_text_list = ''

    log_print('\n---------------- 请选择你要填写的配置参数（请根据 title 选择）： --------------------')
    if multi_select_enabled:
        log_print('---- 需多选的话，请按照这种格式进行输入（必须英文状态下输入）：\n1:5\n---------------------------------------')

    # 收集根据分集和分段拆分后的完整的发布参数配置列表
    select_video_params_list = []
    select_idx = 1 # 提供选择的序号
    for params in video_upload_config_list:
        # 视频一级名称
        upload_video_1th_name = params['first_name']
        # 视频二级名称
        upload_video_2th_name = params['second_name']
        # # 视频分集号
        # upload_video_episode = need_upload_video_episode
        # # 视频某一集的分段号
        # upload_video_paragraph_serial = need_upload_video_paragraph_serial
        # 分区
        upload_channel = params['upload_channel'] #: '生活,日常',
        # 标题（这个标题决定固定的前缀，实际标题后面会动态追加当前上传的视频 第几集 第几段 的参数）
        upload_title = params['upload_title'] #: '坚持学习英语口语--练习材料--《美剧：硅谷》--第{0}季，第{1}集，材料{2}',
        # 类型
        upload_type = params['upload_type'] #: '自制',
        # 标签
        upload_tags = params['upload_tags'] #: '生活,学习,分享',
        # 标签--参与话题
        upload_tags_subject = params['upload_tags_subject'] #: '打工人职场生态图鉴',
        # 简介
        instroduction = params['instroduction']
        # 动态
        upload_dynamic = params['upload_dynamic'] #: '加油！坚持学习英语口语--练习材料--《美剧：硅谷》'
        cover_type = params['cover_type']
        cover_item = params['cover_item']
        cover_text_list = params['cover_text_list']

        # [*] - 要上传的视频分集号数组
        need_upload_video_episode_list = []
        # 先尝试是否为 '2:6' 类似这样的范围字符串，如果不是则会返回 None
        need_upload_video_episode_list = get_seirals_by_rangestr(params['episode_list'],2)
        if need_upload_video_episode_list == None:
            # 如果不是范围字符串，那就只能是 '01,02,03' 类似这样的 都好分隔的字符串
            need_upload_video_episode_list = params['episode_list'].split(',')

        # [*] - 要上传的视频某一集的分段号数组
        need_upload_video_paragraph_serials_list = []
        # 先尝试是否为 '2:6' 类似这样的范围字符串，如果不是则会返回 None
        need_upload_video_paragraph_serials_list = get_seirals_by_rangestr(params['paragraph_serials'],2)
        if need_upload_video_paragraph_serials_list == None:
            # 如果不是范围字符串，那就只能是 '01,02,03' 类似这样的 都好分隔的字符串
            need_upload_video_paragraph_serials_list = params['paragraph_serials'].split(',')
        # 创建 完整 视频目录只需要选择分集就行，这里片段只需默认第一个即可
        need_upload_video_paragraph_serials_list = [need_upload_video_paragraph_serials_list[0]]

        # [**] - 遍历 分集 和 分段 数组拆分出所有的填写列表
        for episode in need_upload_video_episode_list:
            for paragraph_serial in need_upload_video_paragraph_serials_list:
                video_params_item = {
                    # 一级目录(文件夹名)
                    'first_name':  params['first_name'],
                    # 二级目录脚本文件(.py 脚本文件名) [即上面一个目录下的具体文件]
                    'second_name':  params['second_name'], # 表示 第 N 季
                    # 第N集
                    "episode": episode,
                    # 要上传的视频分段的序号（视频分段文件的完整名称例如 silliconvalley1_01.mp4 只要知道分段序号就能拼接出完整的视频文件路径）
                    'paragraph_serial':paragraph_serial,
                    # ------ <必剪 app> 导出画面里要填写的相关参数 start -----------
                    # 分区
                    'upload_channel':  params['upload_channel'],
                    # 标题（这个标题决定固定的前缀，实际标题后面会动态追加当前上传的视频 第几集 第几段 的参数）
                    'upload_title':  params['upload_title'],
                    # 类型
                    'upload_type':  params['upload_type'],
                    # 标签
                    'upload_tags':  params['upload_tags'],
                    # 标签--参与话题（请只设置一项即可）（注：经测试话题参与只能选一项，虽然我程序里支持多项，但是就设置了多项，<必剪 app>也会把后一项覆盖前一项）
                    # 'upload_tags_subject': '2022年新年锦鲤,2022第一次打卡',
                    'upload_tags_subject':  params['upload_tags_subject'],
                    # 简介
                    'instroduction': params['instroduction'],
                    # 动态
                    'upload_dynamic':  params['upload_dynamic'],
                    # 封面修改功能
                    # 封面类型页签（目前仅支持这个）
                    'cover_type': params['cover_type'],
                    # 封面类型页签下的 具体封面选项（行号，列号）（目前仅支持这个）
                    'cover_item': params['cover_item'],
                    # 封面中文本的内容，不同的封面选项有不同数量的文本，需要使用者自己清楚要修改哪些文本，如果为空的，则不会修改原来的文本
                    # 填入规则是：从上到下 > 从左到右 依次把 cover_text_list 列表中的内容进行填入（cover_text_list 中若内容数量缺少则不修改，若有多余的则不管）
                    'cover_text_list': params['cover_text_list'],
                }
                select_video_params_list.append(video_params_item)
                #: '坚持学习英语口语--练习材料--《美剧：硅谷》--第{0}季，第{1}集，材料{2}'
                video_title = params['upload_title'].format(params['second_name'].replace(params['first_name'],''),episode,paragraph_serial)
                log_print(f'[{select_idx}] - {video_title}')
                select_idx += 1
    len_select_video_params_list = len(select_video_params_list)
    video_select = input()

    # 记录多选的内容
    multi_selected = []
    if multi_select_enabled and not is_int_str(video_select):
        # 判定是否为范围字符串（1:5）
        video_select = str(video_select)
        select_result = []
        range_ary = video_select.split(':')
        if len(range_ary) == 2:
            start_idx = 0 if not is_int_str(range_ary[0]) or int(range_ary[0]) > len_select_video_params_list else int(range_ary[0]) - 1
            end_idx = start_idx + 1 if not is_int_str(range_ary[1]) or int(range_ary[1]) > len_select_video_params_list else int(range_ary[1])
            multi_selected = select_video_params_list[start_idx:end_idx]
            for p_idx,params in enumerate(multi_selected):
                # 已选择
                video_title = params['upload_title'].format(params['second_name'].replace(params['first_name'],''),params['episode'],params['paragraph_serial'])
                log_print(f'已选择：[{p_idx+1}] - {video_title}')

                # 视频一级名称
                upload_video_1th_name = params['first_name']
                # 视频二级名称
                upload_video_2th_name = params['second_name']
                # 视频分集号
                upload_video_episode = params['episode']
                # 视频某一集的分段号
                upload_video_paragraph_serial = params['paragraph_serial']
                # 分区
                upload_channel = params['upload_channel'] #: '生活,日常',
                # 标题（这个标题决定固定的前缀，实际标题后面会动态追加当前上传的视频 第几集 第几段 的参数）
                upload_title = params['upload_title'] #: '坚持学习英语口语--练习材料--《美剧：硅谷》--第{0}季，第{1}集，材料{2}',
                # 类型
                upload_type = params['upload_type'] #: '自制',
                # 标签
                upload_tags = params['upload_tags'] #: '生活,学习,分享',
                # 标签--参与话题
                upload_tags_subject = params['upload_tags_subject'] #: '打工人职场生态图鉴',
                # 简介
                instroduction = params['instroduction']
                # 动态
                upload_dynamic = params['upload_dynamic'] #: '加油！坚持学习英语口语--练习材料--《美剧：硅谷》'
                cover_type = params['cover_type']
                cover_item = params['cover_item']
                cover_text_list = params['cover_text_list']
                # 把多选的参数都收集起来
                select_result.append([upload_channel,upload_title,upload_video_2th_name,upload_video_1th_name,upload_video_episode,upload_video_paragraph_serial,upload_type,upload_tags_subject,upload_tags,instroduction,upload_dynamic,cover_type,cover_item,cover_text_list])
        return select_result
    else:
        video_select = 1 if not is_int_str(video_select) or int(video_select) < 1 or int(video_select) > len_select_video_params_list else int(video_select)
        # 已选择
        params = select_video_params_list[video_select-1]
        video_title = params['upload_title'].format(params['second_name'].replace(params['first_name'],''),params['episode'],params['paragraph_serial'])
        log_print(f'已选择：[{video_select}] - {video_title}')

        # 视频一级名称
        upload_video_1th_name = params['first_name']
        # 视频二级名称
        upload_video_2th_name = params['second_name']
        # 视频分集号
        upload_video_episode = params['episode']
        # 视频某一集的分段号
        upload_video_paragraph_serial = params['paragraph_serial']
        # 分区
        upload_channel = params['upload_channel'] #: '生活,日常',
        # 标题（这个标题决定固定的前缀，实际标题后面会动态追加当前上传的视频 第几集 第几段 的参数）
        upload_title = params['upload_title'] #: '坚持学习英语口语--练习材料--《美剧：硅谷》--第{0}季，第{1}集，材料{2}',
        # 类型
        upload_type = params['upload_type'] #: '自制',
        # 标签
        upload_tags = params['upload_tags'] #: '生活,学习,分享',
        # 标签--参与话题
        upload_tags_subject = params['upload_tags_subject'] #: '打工人职场生态图鉴',
        # 简介
        instroduction = params['instroduction']
        # 动态
        upload_dynamic = params['upload_dynamic'] #: '加油！坚持学习英语口语--练习材料--《美剧：硅谷》'
        cover_type = params['cover_type']
        cover_item = params['cover_item']
        cover_text_list = params['cover_text_list']

        return [upload_channel,upload_title,upload_video_2th_name,upload_video_1th_name,upload_video_episode,upload_video_paragraph_serial,upload_type,upload_tags_subject,upload_tags,instroduction,upload_dynamic,cover_type,cover_item,cover_text_list]


# 创建放置视频的文件夹目录的具体操作
def mkdir_full_video_folder_one(params):
    # 终端询问选择哪个视频节目的配置参数
    upload_channel,upload_title,upload_video_2th_name,upload_video_1th_name,upload_video_episode,upload_video_paragraph_serial,upload_type,upload_tags_subject,upload_tags,instroduction,upload_dynamic,cover_type,cover_item,cover_text_list = params
    # downloadvideo/
    video_dir = f'{__ROOTPATH__}/downloadvideo'
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)
    # 节目名称 目录
    video_1th_name_dir = f'{video_dir}/{upload_video_1th_name}'
    if not os.path.exists(video_1th_name_dir):
        os.makedirs(video_1th_name_dir)
    # 节目 分季的名称 目录
    video_2th_name_dir = f'{video_1th_name_dir}/{upload_video_2th_name}'
    if not os.path.exists(video_2th_name_dir):
        os.makedirs(video_2th_name_dir)
    # 节目 视频文件的 tsfiles 存放 目录
    upload_video_episode = f'0{upload_video_episode}' if len(str(upload_video_episode)) < 2 else str(upload_video_episode)
    upload_video_paragraph_serial = f'0{upload_video_paragraph_serial}' if len(str(upload_video_paragraph_serial)) < 2 else str(upload_video_paragraph_serial)
    video_tsfiles_dir = f'{video_2th_name_dir}/tsfiles'
    if not os.path.exists(video_tsfiles_dir):
        os.makedirs(video_tsfiles_dir)
    video_file_dir = f'{video_tsfiles_dir}/{upload_video_2th_name}_{upload_video_episode}'
    if not os.path.exists(video_file_dir):
        os.makedirs(video_file_dir)
    # 节目 视频文件的 存放 目录
    video_file_dir = f'{video_2th_name_dir}/fullvideo'
    if not os.path.exists(video_file_dir):
        os.makedirs(video_file_dir)
    # 节目 视频文件的 index.m3u8 存放 目录
    video_file_dir = f'{video_2th_name_dir}/indextxt'
    if not os.path.exists(video_file_dir):
        os.makedirs(video_file_dir)

# 创建放置视频的文件夹目录（判定是否为批量创建）
def mkdir_full_video_folder():
    # 终端询问选择哪个视频节目的配置参数
    ask_select_upload_config_result = ask_select_mkfullvideodir_config(True)
    if isinstance(ask_select_upload_config_result[0],list):
        # 如果返回的参数时二维数组，则说明用户进行了多选，则进行批量创建目录
        for params in ask_select_upload_config_result:
            mkdir_full_video_folder_one(params)
    else:
        mkdir_full_video_folder_one(ask_select_upload_config_result)

# =================== 生成放置 完整 视频文件的目录 end =============

def start_program():
    global elementIdPrefix
    # 初始化创建需要的目录
    initAllDir()
    # 上传视频之前，选择执行的具体操作
    log_print('\n----- 请选择操作类型（默认选项：[1]）： -----\n')
    hint_options = [
        '[1] - 执行剪辑视频和发布视频的完整操作',
        '[2] - 仅执行该视频节目的发布操作（即仅在发布页面填写表单）'
        # '[3] - 创建用于存放视频文件的目录（如果要上传发布的视频文件还没有放到该项目的指定目录下，则请先执行该操作）'
    ]
    for opt in hint_options:
        log_print(opt)
    if action_type_selected['val'] == None:
        action_type_input = input()
    else:
        action_type_input = action_type_selected['val']
    action_type_input = 1 if not is_int_str(action_type_input) else int(action_type_input)
    action_type_input = 1 if action_type_input < 1 or action_type_input > len(hint_options) else action_type_input
    # action_type_input = 1 if not is_int_str(action_type_input) or (not action_type_input == '2' and not action_type_input == '3') else int(action_type_input)
    action_type_selected['val'] = action_type_input
    log_print(f'已选择：{hint_options[action_type_input-1]}\n')

    if action_type_input == 1:
        log_print('\n----------- 请选择创作方式（默认选项：[1]）： --------------\n')
        hint_options = [
            '[1] - 普通创作',
            '[2] - 以虚拟形象开始创作'
        ]
        for opt in hint_options:
            log_print(opt)
        if create_videw_type_selected['val'] == None:
            select_idx = input()
        else:
            select_idx = create_videw_type_selected['val']
        select_idx = 1 if not is_int_str(select_idx) else int(select_idx)
        select_idx = 1 if select_idx < 1 or select_idx > len(hint_options) else select_idx
        # select_idx = 1 if not is_int_str(select_idx) or not int(select_idx) == 2 else int(select_idx)
        create_videw_type_selected['val'] = select_idx
        log_print(f'已选择:{hint_options[select_idx-1]}\n')

    # 非选项3都需要操作移动设备
    if not action_type_input == 3:
        # 先确保断开连接
        if isset('driver'):
            driver.quit()
        # 连接移动设备
        connnect_android_device()
        # 元素 id 前缀
        elementIdPrefix = "{}:id/".format(desired_caps["appPackage"])
        if action_type_input == 1:
            start_upload_video()
        elif action_type_input == 2:
            start_fill_pub_forms()
        
        wait_sec = 60
        log_print(f'该轮任务已完成，{wait_sec}秒后将自动退出app')
        force_sleep(wait_sec)
        driver.quit()
    # else:
    #     # 选项3无需操作移动设备
    #     mkdir_video_folder()

def start_mkdir_video_folder(upload_config_module):
    global upload_config_module_remember
    global mobile_storage_folder
    global video_file_config_list
    global video_upload_config_list
    global action_type_selected
    global create_videw_type_selected
    
    upload_config_module_remember = upload_config_module
    mobile_storage_folder = upload_config_module.mobile_storage_folder
    video_file_config_list = upload_config_module.video_file_config_list
    video_upload_config_list = upload_config_module.video_upload_config_list
    action_type_selected = {'val':None}
    create_videw_type_selected = {'val':None}

    mkdir_video_folder()

def start_mkdir_full_video_folder(upload_config_module):
    global upload_config_module_remember
    global mobile_storage_folder
    global video_file_config_list
    global video_upload_config_list
    global action_type_selected
    global create_videw_type_selected
    
    upload_config_module_remember = upload_config_module
    mobile_storage_folder = upload_config_module.mobile_storage_folder
    video_file_config_list = upload_config_module.video_file_config_list
    video_upload_config_list = upload_config_module.video_upload_config_list
    action_type_selected = {'val':None}
    create_videw_type_selected = {'val':None}

    mkdir_full_video_folder()

''' 提供给外界调用的主入口函数 '''
def main_func(upload_config_module):
    global upload_config_module_remember
    global mobile_storage_folder
    global video_file_config_list
    global video_upload_config_list
    global action_type_selected
    global create_videw_type_selected
    
    upload_config_module_remember = upload_config_module
    mobile_storage_folder = upload_config_module.mobile_storage_folder
    video_file_config_list = upload_config_module.video_file_config_list
    video_upload_config_list = upload_config_module.video_upload_config_list
    action_type_selected = {'val':None}
    create_videw_type_selected = {'val':None}

    start_program()

# if __name__ == '__main__':
#   initAllDir()
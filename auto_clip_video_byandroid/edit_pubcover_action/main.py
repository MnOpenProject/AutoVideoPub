from appium.webdriver import Remote as Webdriver
import importlib
from appium.webdriver.common.appiumby import AppiumBy
from auto_clip_video_byandroid.common.swipe_util import swipeUp,swipLeft

# 根据封面类型获取对应脚本的前缀
def get_cover_script_prefix_by_type(cover_type):
    if '搞笑2' in cover_type:
        return 'funny2'
    if '搞笑' in cover_type:
        return 'funny'

# 根据封面参数获取对应脚本的位置名称(行号，列号)
def get_cover_script_positionstr_by_positionparams(cover_position):
    return f'r{cover_position[0]}c{cover_position[1]}'

# 更换封面底图
def replace_cover_img(log_print,driver:Webdriver,force_sleep,elementIdPrefix):
    # 点击按钮 <更换底图>
    log_print('点击按钮 <更换底图>')
    replace_img_btn = driver.find_element(AppiumBy.ID, "{}cover_functions_change".format(elementIdPrefix))
    replace_img_btn.click()
    force_sleep(2)

    # 向左滑动视频，更换封面图片
    log_print('向左滑动视频，更换封面图片')
    for i in range(10):
        swipLeft(driver,100,position=(696,1985))
        force_sleep(1)
    
    # 点击按钮 <下一步>
    log_print('点击按钮 <下一步>')
    next_step_btn = driver.find_element(AppiumBy.ID, "{}tv_next".format(elementIdPrefix))
    next_step_btn.click()
    force_sleep(6)

    # 点击按钮 <确认底图>
    log_print('点击按钮 <确认底图>')
    confirm_btn = driver.find_element(AppiumBy.ID, "{}cover_crop_next".format(elementIdPrefix))
    confirm_btn.click()
    force_sleep(6)
    log_print('此时，应该回到了封面编辑画面')

def main_func(log_print,driver:Webdriver,force_sleep,elementIdPrefix,cover_type,cover_item,cover_text_list=[],need_replace_cover_img=False):
    log_print('---------------- 开始修改封面 ---------------')
    # 由于点击封面按钮是通过坐标点击的，为了确保坐标的准确，一定要把画面保证滚动在最顶部
    log_print('屏幕向上滑 -- 由于点击封面按钮是通过坐标点击的，为了确保坐标的准确，一定要把画面保证滚动在最顶部')
    for i in range(10):
        swipeUp(driver,100)
        force_sleep(1)
    force_sleep(2)

    # 点击按钮 <修改封面>
    driver.tap([(344,825)],10)
    force_sleep(2)

    log_print('[*] - 根据配置参数动态引入对应的封面编辑脚本')
    # 根据配置参数动态引入对应的封面编辑脚本
    # 由于封面里的文本有很多个且位置都不同，设定一个规则进行填入：从上到下 > 从左到右 依次把 text_list 列表中的内容进行填入（text_list 中若内容数量缺少则不修改，若有多余的则不管）
    # 动态引入脚本
    prefix = get_cover_script_prefix_by_type(cover_type)
    positionstr = get_cover_script_positionstr_by_positionparams(cover_item)
    module = importlib.import_module(f'auto_clip_video_byandroid.edit_pubcover_action.{prefix}_{positionstr}')
    module.main_func(log_print,driver,force_sleep,elementIdPrefix,cover_text_list)

    # 更换封面底图
    if need_replace_cover_img:
        replace_cover_img(log_print,driver,force_sleep,elementIdPrefix)

    # 点击按钮 <完成> 退出封面编辑页面
    driver.tap([(943,167)],10)
    force_sleep(2)
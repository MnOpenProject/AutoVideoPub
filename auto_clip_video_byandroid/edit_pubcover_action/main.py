from appium.webdriver import Remote as Webdriver
import importlib

# 根据封面类型获取对应脚本的前缀
def get_cover_script_prefix_by_type(cover_type):
    if '搞笑2' in cover_type:
        return 'funny2'
    if '搞笑' in cover_type:
        return 'funny'

# 根据封面参数获取对应脚本的位置名称(行号，列号)
def get_cover_script_positionstr_by_positionparams(cover_position):
    return f'r{cover_position[0]}c{cover_position[1]}'

def main_func(log_print,driver:Webdriver,force_sleep,elementIdPrefix,cover_type,cover_item,cover_text_list=[]):
    log_print('---------------- 开始修改封面 ---------------')
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

    # 点击按钮 <完成> 退出封面编辑页面
    driver.tap([(943,167)],10)
    force_sleep(2)
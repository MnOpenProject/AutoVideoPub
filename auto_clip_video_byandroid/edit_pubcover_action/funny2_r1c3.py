from appium.webdriver import Remote as Webdriver
from appium.webdriver.common.appiumby import AppiumBy

def main_func(log_print,driver:Webdriver,force_sleep,elementIdPrefix,text_list=[]):
    log_print('---------- 搞笑类型：行1列3 <不要笑挑战 哈哈>（不移除 “哈哈” 贴纸） ---------')

    # 选择分类页签 <搞笑>
    driver.tap([(802,1366)],10)
    force_sleep(2)

    # 选择第1行的第3个 封面
    driver.tap([(880,1550)],10)
    force_sleep(2)

    # 把文本内容参数 依次修改到 封面文本里
    # 由于封面里的文本有很多个且位置都不同，设定一个规则进行填入：从上到下 > 从左到右 依次把 text_list 列表中的内容进行填入

    # # [*] - 移除 <哈哈> 贴纸
    # driver.tap([(883,577)],10)
    # force_sleep(2)
    # driver.tap([(683,395)],10)
    # force_sleep(2)

    # 修改封面文字
    if len(text_list) > 0 and not text_list[0] == '':
        # 点击文字
        driver.tap([(539,847)],10)
        force_sleep(2)
        # 下方弹出编辑区域，获取输入框UI
        edit_text_input = driver.find_element(AppiumBy.ID, "{}caption_input".format(elementIdPrefix))
        edit_text_input.click()
        force_sleep(1)
        driver.tap([(440,1255)],10)
        force_sleep(2)
        edit_text_input.send_keys(text_list[0]) # 输入文字
        # 点击打勾按钮，确定编辑，关闭编辑区域
        driver.tap([(1004,1255)],10)
        force_sleep(2)
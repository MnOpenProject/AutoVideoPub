''' 在视频编辑中，插入虚拟形象 '''
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver import Remote as Webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.mouse_button import MouseButton
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.action_builder import ActionBuilder

# 通过虚拟形象渠道 开始创作（请确保在首页的 <创作> 页签中）
def start_create_by_virsual_role_channel(log_print,driver:Webdriver,force_sleep,elementIdPrefix):
  # [1] - 点击按钮 <虚拟形象>
  log_print('[1] - 点击按钮 <虚拟形象>')
  # start_by_role_btn = driver.find_element(AppiumBy.ID, "{}sdv_bottom_virtual_idol_bg".format(elementIdPrefix))
  # start_by_role_btn.click()
  driver.tap([(900,630)],10)
  force_sleep(2)
  # [2] - 点击按钮 <使用当前形象去创作>
  log_print('[2] - 点击按钮 <使用当前形象去创作>')
  # start_create_video_btn = driver.find_element(AppiumBy.ID, "{}virtual_idol_preview_editor".format(elementIdPrefix))
  # start_create_video_btn.click()
  driver.tap([(520,2052)],10)
  force_sleep(2)
  # [3] - 点击按钮 <自定义创作>
  log_print('[3] - 点击按钮 <自定义创作>')
  # start_create_video_custom_btn = driver.find_element(AppiumBy.ID, "{}tv_custom_creation".format(elementIdPrefix))
  # start_create_video_custom_btn.click()
  driver.tap([(910,170)],10)
  force_sleep(2)
  # [4] - 缩放 <虚拟形象> 图像缩小
  log_print('[4] - 缩放 <虚拟形象> 图像缩小')    
  # （必剪 app 贴纸放大功能有缺陷，放大角度必然会转）缩放有点歪
  # TouchAction(driver)   .press(x=836, y=914)   .move_to(x=538, y=633)   .release()   .perform()
  driver.swipe(start_x=836, start_y=914, end_x=538, end_y=633)
  force_sleep(2)
  # 移动到左下角
  # TouchAction(driver)   .press(x=538, y=617)   .move_to(x=37, y=881)   .release()   .perform()
  driver.swipe(start_x=538, start_y=617, end_x=37, end_y=881)
  force_sleep(2)
  # [5] - 点击 视频区域 选中初始随机带出的视频片段
  log_print('[5] - 点击 视频区域 选中初始随机带出的视频片段')
  driver.tap([(550,630)],10)
  force_sleep(2)
  # [5.1] - 点击底部工具栏图标按钮 <垃圾桶> 删除选中的初始随机带出的视频片段
  log_print('[5.1] - 点击底部工具栏图标按钮 <垃圾桶> 删除选中的初始随机带出的视频片段')
  driver.tap([(852,2044)],10)
  force_sleep(2)
  # [6] - 点击按钮 <加号 添加视频> 就是屏幕中间编辑区域的右侧的 白色加号 图标
  log_print('[6] - 点击按钮 <加号 添加视频> 就是屏幕中间编辑区域的右侧的 白色加号 图标')
  driver.tap([(1000,1465)],10)
  force_sleep(2)

  # ------------ 接下来就是进入跟普通创建视频任务一样，开始进入视频素材选择画面了 -------------
  log_print('------------ 接下来就是进入跟普通创建视频任务一样，开始进入视频素材选择画面了 -------------')
  force_sleep(2)

  # 虚拟角色创作模式下，底部工具栏新增了一个 <虚拟形象> 菜单按钮在第一个，所以影响到了，后续操作中需要点击的 <音频> 菜单按钮的坐标
  editor_tool_audio_import_position = (500,2193)
  # 虚拟角色创作模式下，底部工具栏新增了一个 <虚拟形象> 菜单按钮在第一个，所以影响到了，后续操作中需要点击的 <贴纸> 菜单按钮的坐标
  editor_tool_paster_position = (865,2193)
  # 把一些 此创作模式下 特殊的属性反馈回去
  return [editor_tool_audio_import_position,editor_tool_paster_position]
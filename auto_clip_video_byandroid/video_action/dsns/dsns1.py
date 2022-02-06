from appium.webdriver.common.appiumby import AppiumBy

def edit_video_action(log_print,driver,force_sleep,video_file_config_list,video_show_1th_name,video_show_2th_name,elementIdPrefix,video_show_file,editor_tool_audio_import_position=None,editor_tool_paster_position=None):
    print('\n----------------------- 开始执行针对当前视频的剪辑操作 ---------------------------\n')
    # # [7.1] - 点击按钮 <开原声> 初始默认是开启原声的，初始状态下点一下这个按钮，则切换成 关闭原声
    # log_print('[7.1] - 点击按钮 <开原声> 初始默认是开启原声的，初始状态下点一下这个按钮，则切换成 关闭原声')
    # editor_video_audio_switch = driver.find_element(AppiumBy.ID, "{}tv_volume_switch_tips".format(elementIdPrefix))
    # editor_video_audio_switch.click()
    # force_sleep(5)

    # # 点击空白区域，确保没有选中任何元素，此时底部工具栏才是最基础的操作菜单
    # driver.tap([(199, 1796)], 10)
    # force_sleep(2)

    # # [7.1.2] - 点击底部工具栏按钮 <音频> 准备单独导入视频文件的声音
    # # （这一步操作很关键，因为目前实际操作中遇到问题：视频文件的声音出现丢失部分的情况，所以干脆把编辑时的声音都关闭原声，然后单独重新导入该视频的声音）
    # # editor_tool_audio_menu_btn = driver.find_element(AppiumBy.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.RelativeLayout[5]/android.widget.RelativeLayout[1]/android.widget.RelativeLayout/androidx.recyclerview.widget.RecyclerView/android.widget.LinearLayout[2]/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.ImageView')
    # # editor_tool_audio_menu_btn.click()
    # # driver.tap([(306, 2193)], 10)
    # # 由于某些创作模式下，底部工具栏菜单会有增减，所以 音频 菜单按钮的位置需要根据不同的创作模式而动态传入
    # editor_tool_audio_import_position_ = (306,2193) if editor_tool_audio_import_position == None else editor_tool_audio_import_position
    # driver.tap([editor_tool_audio_import_position_],10)
    # force_sleep(2)

    # # [7.1.3] - 点击底部工具栏按钮 <音频提取> 去选择要单独导入视频文件的声音
    # # editor_tool_audio_into_btn = driver.find_element(AppiumBy.XPATH,'/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.RelativeLayout[5]/android.widget.RelativeLayout[1]/android.widget.RelativeLayout/android.widget.RelativeLayout/androidx.recyclerview.widget.RecyclerView/android.widget.LinearLayout[2]/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.ImageView')
    # # editor_tool_audio_into_btn.click()
    # driver.tap([(382, 2193)], 10)
    # force_sleep(2)

    # # [7.1.4] - 点击顶部下拉选项 <视频> 去选择要单独导入视频文件的声音
    # editor_tool_audio_dropdown_tab = driver.find_element(AppiumBy.ID,
    #                                                      "{}video_extract_tab_video".format(elementIdPrefix))
    # editor_tool_audio_dropdown_tab.click()
    # force_sleep(2)

    # # [7.1.5] - 选择列表项 选中与当前这个视频相同名称的那视频的文件夹，单独导入视频文件的声音
    # video_show_file_floder_item = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
    #                                                   'new UiSelector().textContains("{}")'.format(video_show_file))
    # video_show_file_floder_item.click()
    # force_sleep(2)

    # # [7.1.6] - 选择卡片列表项 此时只会有一个视频文件（特意这么做的），点击第一个即可，使其变成选中状态
    # video_show_file_item = driver.find_element(AppiumBy.ID, "{}item_material_thumb_im".format(elementIdPrefix))
    # video_show_file_item.click()
    # force_sleep(1)

    # # [7.1.7] - 点击按钮 <仅导入视频的声音> 把视频文件的声音导入进去
    # log_print('[7.1.7] - 点击按钮 <仅导入视频的声音> 把视频文件的声音导入进去')
    # editor_tool_audio_into_start_btn = driver.find_element(AppiumBy.ID,
    #                                                        "{}tv_start_video_compile".format(elementIdPrefix))
    # editor_tool_audio_into_start_btn.click()
    # force_sleep(10)
    # # driver.tap([(526,2236)],10)

    # # [7.1.8] - 当前已返回视频编辑画面，点击空白位置，去除音频的选中状态
    # log_print('[7.1.8] - 当前已返回视频编辑画面，点击空白位置，去除音频的选中状态')
    # driver.tap([(263, 1788)], 10)
    # force_sleep(2)

    # # [7.1.9] - 点击底部工具栏图标按钮 最左侧的返回上一级按钮 返回原始的底部工具栏状态
    # log_print('[7.1.9] - 点击底部工具栏图标按钮 最左侧的返回上一级按钮 返回原始的底部工具栏状态')
    # driver.tap([(73, 2218)], 10)
    # force_sleep(2)

    # # [7.2] - 点击视频区域 选中视频区域
    # driver.tap([(500, 600)], 10)
    # force_sleep(5)

    # # [8.1] - 在底部滚动条 手指向右侧滑动 确保工具栏是滚在最左侧的，这才能确保下面点击的 <画面> 按钮坐标是准确的
    # # （这主要是为了应对 <必剪 app> 的bug，不知为了，此时再展示底部工具栏时，移位了）
    # log_print(
    #     '[8.1] - 在底部滚动条 手指向右侧滑动 确保工具栏是滚在最左侧的，这才能确保下面点击的 <画面> 按钮坐标是准确的\n（这主要是为了应对 <必剪 app> 的bug，不知为了，此时再展示底部工具栏时，移位了）')
    # driver.swipe(start_x=223, start_y=2193, end_x=986, end_y=2193)
    # force_sleep(2)

    log_print('操作完成 【遮盖右下角广告区域，这存在的话会导致视频无法过审】\n')

    # [22] - 点击按钮 <导出> 切换到视频导出发布画面
    export_btn = driver.find_element(AppiumBy.ID, "{}tv_export".format(elementIdPrefix))
    export_btn.click()
    log_print('\n---------------- 点击<导出>，切换到<发布>画面，请等待片刻，待视频导出完成后，开始填写发布信息 ---------------\n')
    wait_s = 50
    force_sleep(wait_s)
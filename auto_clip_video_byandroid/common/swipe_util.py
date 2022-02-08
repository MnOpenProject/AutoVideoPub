''' 模拟手指滑动功能 '''
# from appium import webdriver
# driver = webdriver.Remote(server, desired_caps)

# Appium处理滑动方法是swipe

# 滑动API：Swipe（int start x,int start y,int end x,int y,duration) 
# 解释： 
# int start x－开始滑动的x坐标；
# int start y －开始滑动的y坐标 ；
# int end x －结束点x坐标；
# int end y －结束点y坐标； 
# duration 滑动时间（默认5毫秒）。

# 获取屏幕尺寸
def getScreenSize(driver):
    x = int(driver.get_window_size()["width"])
    y = int(driver.get_window_size()["height"])
    return (x, y)

'''
参数说明
【1】driver [必须] 参数为（需要外界预先如下定义好，再传入）：
# from appium import webdriver
# driver = webdriver.Remote(server, desired_caps)

【2】distance [非必须] -- 模拟手指滑动的距离；（默认滑动距离为 100）

【3】position [非必须] -- 模拟手指滑动的 起始位置坐标 (x,y); （默认为屏幕中间位置开始滑动）

【4】duration [非必须] -- 模拟手指滑动时接触屏幕的持续时长；（默认为 5 毫秒）
'''

#屏幕向上滑动
def swipeUp(driver,distance=100,position=None,duration=5):
    screen_size = getScreenSize(driver)
    if position == None:
        position = (screen_size[0] / 2, screen_size[1] / 2)    
    # 起点坐标
    start = position
    # 终点坐标
    end = (start[0], position[1] + distance)
    # 调用滑动函数
    driver.swipe(start[0], start[1], end[0], end[1], duration)

#屏幕向下滑动
def swipeDown(driver,distance=100,position=None,duration=5):
    screen_size = getScreenSize(driver)
    if position == None:
        position = (screen_size[0] / 2, screen_size[1] / 2)    
    # 起点坐标
    start = position
    # 终点坐标
    end = (start[0], position[1] - distance)
    # 调用滑动函数
    driver.swipe(start[0], start[1], end[0], end[1], duration)

#屏幕向左滑动
def swipLeft(driver,distance=100,position=None,duration=5):
    screen_size = getScreenSize(driver)
    if position == None:
        position = (screen_size[0] / 2, screen_size[1] / 2)    
    # 起点坐标
    start = position
    # 终点坐标
    end = (start[0] - distance, position[1])
    # 调用滑动函数
    driver.swipe(start[0], start[1], end[0], end[1], duration)

#屏幕向右滑动
def swipRight(driver,distance=100,position=None,duration=5):
    screen_size = getScreenSize(driver)
    if position == None:
        position = (screen_size[0] / 2, screen_size[1] / 2)    
    # 起点坐标
    start = position
    # 终点坐标
    end = (start[0] + distance, position[1])
    # 调用滑动函数
    driver.swipe(start[0], start[1], end[0], end[1], duration)
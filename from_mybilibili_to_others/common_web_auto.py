# selenium API: https://www.selenium.dev/documentation/
# selenium 使用 参考地址：https://www.cnblogs.com/EthanHe97/p/11270528.html
# Chrome 引擎下载地址：http://chromedriver.storage.googleapis.com/index.html

from time import sleep
from xmlrpc.client import Boolean
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.edge.options import Options as EdgeOptions
from msedge.selenium_tools import EdgeOptions
from msedge.selenium_tools import Edge
from .common_config import __CURPATH__,cookie_txt_path,bilibili_request_headers,personal_info_path,cookie_xiaohongshu_txt_path
from .common_util import force_sleep, get_personal_info_module,write_blibli_cookie_into_txt,read_blibli_cookie_from_txt,check_bilibili_cookie_validity,read_xiaohongshu_cookie_from_txt,check_xiaohongshu_cookie_validity,write_xiaohongshu_cookie_into_txt
import os,requests

# Eage driver 下载地址：https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
# Eage driver 下载地址：https://msedgedriver.azureedge.net/96.0.1054.62/edgedriver_win64.zip

# B站登录地址
bilibili_login_url = 'https://passport.bilibili.com/login?from_spm_id=333.1007.top_bar.login'
# 小红书的 web 端视频发布地址
xiaohongshu_clip_tool_url = "https://creator.xiaohongshu.com/creator/post"

def create_dege_driver(init_url):
    # Chrome 引擎文件位置
    # driver_path = r"{}\driver_exe\chromedriver.exe".format(__CURPATH__)
    driver_path = r"{}\driver_exe\msedgedriver.exe".format(__CURPATH__)
    print("======= web driver path: {}".format(driver_path))

    # # 设置参数，并创建引擎对象
    # chrome_options = Options()
    # chrome_options.add_argument("–no-sandbox") # 解决DevToolsActivePort文件不存在的报错
    # chrome_options.add_argument("window-size=1920x3000") # 指定浏览器分辨率
    # chrome_options.add_argument("–disable-gpu") # 谷歌文档提到需要加上这个属性来规避bug
    # chrome_options.add_argument("–hide-scrollbars") # 隐藏滚动条, 应对一些特殊页面
    # chrome_options.add_argument("blink-settings=imagesEnabled=false") # 不加载图片, 提升速度
    # chrome_options.add_argument("–headless") # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    # # chrome_options.binary_location = chrome_driver # 手动指定使用的浏览器位置
    # driver = webdriver.Chrome(driver_path,options=chrome_options)
    
    edge_options = EdgeOptions()
    # 防止打印一些无用的日志
    edge_options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
    edge_options.use_chromium = True
    edge_options.add_argument('--disable-blink-features=AutomationControlled') # 解决Edge浏览器对selenium的检测问题
    # edge_options.add_argument("--disable-infobars")
    driver = Edge(driver_path,options=edge_options)
    # 创建等待对象
    # wait = WebDriverWait(driver, 60)
    driver.get(init_url)
    # driver.find_element(By.NAME, "q").send_keys("cheese" + Keys.RETURN)
    # first_result = wait.until(presence_of_element_located((By.CSS_SELECTOR, "h3")))
    # log_print(first_result.get_attribute("textContent"))

    # log_print("请手动登录，完成后，选择是否继续(Y/n)\n")
    # is_continue = input()
    # is_continue = 'Y' if is_continue == '' else is_continue
    # if not is_continue.upper() == 'Y':
    #     return False
    
    # log_print("确定已完成登录了吗？是否继续(Y/n)\n")
    # is_continue = input()
    # is_continue = 'Y' if is_continue == '' else is_continue
    # if not is_continue.upper() == 'Y':
    #     return False
    
    return driver

# B站登录功能，这里用于获取账号 cookie 数据，cookie 需要用于请求《稿件管理》的视频列表数据
def get_edge_bilibili_login_cookie():
    driver=create_dege_driver(bilibili_login_url)
    cookie_str=edge_bilibi_login_by_phone(driver)
    driver.close()
    return cookie_str

# cookie 文件由于属于敏感数据，该文件会在 .gitignore 中忽略，不会上传到远程仓库
# 检查B站的 cookie 是否存在和有效
def check_bilibli_cookie_and_create():
    print('----------------- 正在检查 B站 cookie 请稍后...')
    # 若不存在 cookie 文本，则创建一个，并通过登录功能创建一个cookie文本
    if not os.path.exists(cookie_txt_path):
        cookie_str = get_edge_bilibili_login_cookie()
        write_blibli_cookie_into_txt(cookie_str)
    else:
        # 若已存在，则读取，并测试有效性
        cookie_str = read_blibli_cookie_from_txt()
        # 检查 cookie 是否有效
        if not check_bilibili_cookie_validity(cookie_str):
            # 无效则获取最新的cookie，并存入本地
            os.remove(cookie_txt_path)
            # 如果当前存储的 cookie 无效，则重新写入一个新的 cookie
            cookie_str = get_edge_bilibili_login_cookie()
            write_blibli_cookie_into_txt(cookie_str)
    
    # 最后再检查一遍 cookie 是否有效
    if not check_bilibili_cookie_validity(cookie_str):
        print('----- B站 cookie 初始化失败，请检查代码后，再重试')
        return False
    else:
        print('----- B站 cookie 初始化完成')
        return True

# B站登录功能，这里用于获取账号 cookie 数据，cookie 需要用于请求《稿件管理》的视频列表数据
def edge_bilibi_login_by_phone(driver:Edge):
    print("start login by phone")
    # 动态获取个人信息
    personal_info_module = get_personal_info_module()
    b_phone = personal_info_module.b_phone

    # 点击页签 <短信登录>
    phone_login_tab = driver.find_element_by_xpath('//*[@id="geetest-wrap"]/div/div[1]/span[2]')
    phone_login_tab.click()

    # 输入手机号
    phone_input = driver.find_element_by_xpath('//*[@id="geetest-wrap"]/div/div[3]/div[1]/div/input')
    phone_input.send_keys(b_phone)

    # 点击按钮 <获取验证码>
    send_msg_code_btn = driver.find_element_by_xpath('//*[@id="geetest-wrap"]/div/div[3]/div[3]/button')
    send_msg_code_btn.click()

    # 输入验证码
    print("请在终端这里输入验证码（输入完成后回车即可）：")
    msg_code = input()
    msg_code_input = driver.find_element_by_xpath('//*[@id="geetest-wrap"]/div/div[3]/div[3]/div/input')
    msg_code_input.send_keys(msg_code)
    
    # 点击按钮 <登录>
    # login_btn = wait.until(presence_of_element_located((By.XPATH, '//*[@id="page"]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/button')))
    login_btn = driver.find_element_by_xpath('//*[@id="geetest-wrap"]/div/div[5]/a[1]')
    login_btn.click()

    print('稍等片刻，等登录成功后，自动收集 cookie 数据')
    force_sleep(6)
    # 获取浏览器 cookie
    cookie_items = driver.get_cookies()
    cookie_items = cookie_items[::-1] # 倒序排列
    cookie_str = ''
    # 拼接cookie字符串
    for item_cookie in cookie_items:
        item_str = item_cookie["name"]+"="+item_cookie["value"]+"; "
        cookie_str += item_str
        print(f'item_cookie = {item_cookie}')
    print(f'整理出的 cookie_str 如下：\n{cookie_str}')
    # if not check_bilibili_cookie_validity(cookie_str):
    #     return ''
    return cookie_str

# 小红书的自动登录功能（针对这个地址 xiaohongshu_clip_tool_url = "https://creator.xiaohongshu.com/creator/post"）
def edge_xiaohongshu_login_by_phone(driver:Edge):
    print("start login by phone")
    # 动态获取个人信息
    personal_info_module = get_personal_info_module()
    xiaohongshu_phone = personal_info_module.xiaohongshu_phone

    # 输入手机号
    phone_input = driver.find_element_by_xpath('//*[@id="page"]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div[1]/div[1]/input')
    phone_input.send_keys(xiaohongshu_phone)

    # 点击按钮 <发送验证码>
    send_msg_code_btn = driver.find_element_by_xpath('//*[@id="page"]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div[1]/div[2]/div[2]/div')
    send_msg_code_btn.click()

    # 请输入验证码
    print("请在终端这里输入验证码（输入完成后回车即可）：")
    msg_code = input()
    msg_code_input = driver.find_element_by_xpath('//*[@id="page"]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div[1]/div[2]/input')
    msg_code_input.send_keys(msg_code)
    
    # 点击按钮 <登录>
    # login_btn = wait.until(presence_of_element_located((By.XPATH, '//*[@id="page"]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/button')))
    login_btn = driver.find_element_by_xpath('//*[@id="page"]/div/div[2]/div[1]/div[2]/div/div/div/div/div[1]/button')
    login_btn.click()

    print('稍等片刻，等登录成功后，自动收集 cookie 数据')
    force_sleep(6)
    # 获取浏览器 cookie
    cookie_items = driver.get_cookies()
    cookie_items = cookie_items[::-1] # 倒序排列
    cookie_str = ''
    # 拼接cookie字符串
    for item_cookie in cookie_items:
        item_str = item_cookie["name"]+"="+item_cookie["value"]+"; "
        cookie_str += item_str
        print(f'item_cookie = {item_cookie}')
    #打印出来看一下
    print(f'整理出的 cookie_str 如下：\n{cookie_str}')
    return {'cookie_str':cookie_str,'cookie_items':cookie_items}

# 从本地文件读取 小红书 网址的 cookie
# 若不存在，或者已失效，则重新进行登录获取新的 cookie
def read_xiaohongshu_cookie(driver):
    print('----------------- 正在检查 小红书 cookie 请稍后...')
    check_pass = False
    cookie_str = ''
    cookie_items = []
    # 若不存在 cookie 文本，则创建一个，并通过登录功能创建一个cookie文本
    if not os.path.exists(cookie_xiaohongshu_txt_path):
        json_obj = edge_xiaohongshu_login_by_phone(driver)
        cookie_str = json_obj['cookie_str']
        cookie_items = json_obj['cookie_items']
        write_xiaohongshu_cookie_into_txt(cookie_str,cookie_items)
    else:
        # 若已存在，则读取，并测试有效性
        json_obj = read_xiaohongshu_cookie_from_txt()
        cookie_str = json_obj['cookie_str']
        cookie_items = json_obj['cookie_items']
        # 若读取到的 cookie 已经失效，则重新获取一个最新的
        if not check_xiaohongshu_cookie_validity(cookie_str):
            os.remove(cookie_xiaohongshu_txt_path)
            # 若当前存储的 cookie 无效，则重新写入一个新的 cookie
            json_obj = edge_xiaohongshu_login_by_phone(driver)
            cookie_str = json_obj['cookie_str']
            cookie_items = json_obj['cookie_items']
            write_xiaohongshu_cookie_into_txt(cookie_str,cookie_items)
    
    # 最后再检查一遍 cookie 是否有效
    if not check_xiaohongshu_cookie_validity(cookie_str):
        print('----- B站 cookie 初始化失败，请检查代码后，再重试')
        check_pass = False
    else:
        print('----- B站 cookie 初始化完成')
        check_pass = True
    return {'check_pass':check_pass,'cookie_str':cookie_str,'cookie_items':cookie_items}

# 把 cookie 填入当前浏览器的网站内
# 把有效的 cookie items 直接塞入网站，即可跳过登录验证，不用每次都进行登录了
# cookie items 时通过 selenium 的 webdriver 直接获取到的数据（即 driver.get_cookies()）
# 参考网址：https://blog.csdn.net/Ivansite/article/details/105025241
def add_cookie_item_into_web(driver:Edge,cookie_items):
    for cookie_item in cookie_items:
        # item_str = cookie_item["name"]+"="+cookie_item["value"]+"; "
        # cookie_dict = {'name' : str(cookie_item["name"]), 'value' : str(cookie_item["value"])}
        # print('查看 cookie_dict 的类型：{}'.format(type(cookie_dict)))
        # cookie_prefix = str(cookie_dict).replace("{","{'cookie':")
        # input()
        
        cookie_item['secure'] = bool(cookie_item['secure'])
        cookie_item['httpOnly'] = bool(cookie_item['httpOnly'])
        if 'expiry' in cookie_item:
            cookie_item['expiry'] = int(cookie_item['expiry'])
        # else:
        #     cookie_item['expiry'] = 0
        driver.add_cookie(cookie_item)
    # for cookie in cookie_items:
    #     if 'expiry' in cookie and 'expiry' is not None:
    #         cookie['expiry'] = int(cookie['expiry'])
    #     driver.add_cookie(cookie)

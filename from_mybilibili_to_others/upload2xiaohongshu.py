''' 自动上传视频到 《小红书》平台 '''

from lib2to3.pgen2 import driver
import os,requests,json
# selenium API: https://www.selenium.dev/documentation/
# selenium 使用 参考地址：https://www.cnblogs.com/EthanHe97/p/11270528.html
# Chrome 引擎下载地址：http://chromedriver.storage.googleapis.com/index.html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.edge.options import Options as EdgeOptions
from msedge.selenium_tools import EdgeOptions
from msedge.selenium_tools import Edge
from selenium.webdriver.common.action_chains import ActionChains
from .common_config import __CURPATH__, video_new_dir,video_upload_menu_xiaohongshu_txt_name,xiaohongshu_request_headers,upload_default_topics
from .common_util import force_sleep,log_print as cm_log_print,write_uploaded_remember_txt,read_upload_video_menu,get_video_source_title_by_name,read_uploaded_remember_to_judge_isuploaded
from .common_web_auto import xiaohongshu_clip_tool_url,create_dege_driver,edge_xiaohongshu_login_by_phone,read_xiaohongshu_cookie,add_cookie_item_into_web

# Eage driver 下载地址：https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
# Eage driver 下载地址：https://msedgedriver.azureedge.net/96.0.1054.62/edgedriver_win64.zip

clip_tool_url = xiaohongshu_clip_tool_url
# 点击发布按钮前的等待时长（单位：秒），避免视频没有上传完成
pub_wait_sec = 30
# 请求头
my_request_headers = xiaohongshu_request_headers

def log_print(content_str):
    cm_log_print(content_str,'upload2xiaohongshu')

def create_driver():
    return create_dege_driver(clip_tool_url)

def login_by_phone():
    return edge_xiaohongshu_login_by_phone(driver)

# 输入描述前面的话题
# 在 [描述]栏的最前面填写[话题]功能（注：这个话题功能一定要先填写在[描述]的最前面）
# 【这种方案取决于简述智能视频做的好不好，测试下来不行会出现不合理的情况，所以放弃该方案】（话题默认规则特别说明：如果数组中存在空字符串，比如 [''] 这样的数组，那么后续填写话题时，点击一下<话题>按钮，在对空字符串回车的情况下，小红书会根据标题自动识别出合适的话题）
# 【默认情况下，使用全局设置的话题变量，在 common_config.py 下可以自行修改】
def input_topic_into_el(upload_topic_list):
    # 去重，避免输入相同话题
    upload_topic_list = list(set(upload_topic_list))
    # 排除空字符串
    upload_topic_list = [i for i in upload_topic_list if not str(i).replace(' ','') == '']
    if len(upload_topic_list) < 1:
        default_topics = str(upload_default_topics).replace('，',',')
        upload_topic_list = default_topics.split(',')
        # 排除空字符串
        upload_topic_list = [i for i in upload_topic_list if not str(i).replace(' ','') == '']

    log_print(f'话题：upload_topic_list => {upload_topic_list}')
    # 为了等待异步加载数据，控制个间隔时间
    span_wait_sec = 1
    if len(upload_topic_list) > 0:
        for topic in upload_topic_list:
            # 先点击按钮<话题>
            topic_btn = driver.find_element_by_xpath('//*[@id="topicBtn"]/span')
            topic_btn.click()
            force_sleep(span_wait_sec) # 为了等待异步加载数据，控制个间隔时间
            # 再在[描述]栏里输入一个话题文字
            upload_desc_input = driver.find_element_by_xpath('//*[@id="post-textarea"]')
            upload_desc_input.send_keys(topic)
            force_sleep(span_wait_sec) # 为了等待异步加载数据，控制个间隔时间
            # 按下回车确定选择 下面下拉框里显示的 第一个话题
            upload_desc_input.send_keys(Keys.ENTER)
            force_sleep(span_wait_sec) # 为了等待异步加载数据，控制个间隔时间

# 编辑封面
def edit_cover(driver:Edge,cover_img_file):
    # 点击按钮 <编辑封面>
    edit_cover_btn = driver.find_element_by_xpath('//*[@id="publish-container"]/div/div[2]/div[2]/div[2]/div[1]/div[1]')
    edit_cover_btn.click()
    force_sleep(2)

    if str(cover_img_file).replace(' ','') == '':
        # 【*】视频截取封面方案
        # 最终测试发现，下方的条状是由一个一个 <li> 拼接而成的，只要点击其中一个 <li> 就能完美实现封面的切换功能了
        cover_bar_li = driver.find_element_by_xpath('//*[@id="cover-modal-0"]/div/div/div[2]/div/div[2]/div[2]/div/div[2]/ul/li[7]')
        cover_bar_li.click()
        force_sleep(2)
    else:
        # 【*】使用来自B站的封面图片
        # 切换页签 <上传封面>
        cover_bar_li = driver.find_element_by_xpath('//*[@id="cover-modal-0"]/div/div/div[2]/div/div[2]/div[1]/div[2]')
        cover_bar_li.click()
        force_sleep(2)
        # 把图片输入到上传栏位中
        upload_cover_input = driver.find_element_by_xpath('//*[@id="cover-modal-0"]/div/div/div[2]/div/div[2]/div[3]/div[2]/input')
        upload_cover_input.send_keys(cover_img_file)
        force_sleep(2)

    # 点击按钮 <确定> (关闭编辑封面弹窗)
    cover_confirm_btn = driver.find_element_by_xpath('//*[@id="cover-modal-0"]/div/div/div[3]/div/button[2]/span')
    cover_confirm_btn.click()
    force_sleep(2)

# 请求小红书的笔记数据（即所有已提交的视频数据）
def request_all_xiaohongshu_video():
    headers = my_request_headers
    headers['Cookie'] = cookie_str
    url = f'https://creator.xiaohongshu.com/api/galaxy/creator/note/user/posted?tab=0'
    r = requests.request(method='GET',url=url,headers=headers)
    res_data = json.loads(r.content)['data']
    print(f'请求到的 小红书 笔记数据：\n{res_data}')
    notes = res_data['notes']
    return notes

# 去全部笔记列表里检查是否存在刚发布的视频数据
def check_upload_success(upload_title):
    log_print('刚发布的视频，需要稍等片刻后，再去笔记里检查是否存在数据...')
    force_sleep(6)
    # 请求小红书所有笔记
    notes_data = request_all_xiaohongshu_video()
    # 在所有笔记数据里查找有没有相同的 title 有说明发布成功了，否则说明发布失败了，要重新发布
    find_notes = [i for i in notes_data if i['title'] == upload_title]
    if len(find_notes) > 0:
        return True
    return False

def upload_video_one(driver:Edge,video_file_path,video_config):
    log_print(f'正在上传的视频文件：\n{video_file_path}')

    video_file_name = str(video_config['title'])
    # [标题栏]
    # 上传视频的[标题栏]填写规则：先读取配置参数，若配置参数为空，则使用默认规则
    upload_title = str(video_config['upload_title'])
    if upload_title.replace(' ','') == '':
        # 参数值为空时，默认使用文件的原始标题作为上传时的标题
        upload_title = get_video_source_title_by_name(video_file_name)
    # 由于小红书平台的标题限制在 20 字，若设置内容超出 20 字，则截取其中一定长度的文字，并追加省略号 ...
    upload_title_max = 20
    if len(upload_title) > upload_title_max:
        upload_title = upload_title[:upload_title_max - 6] + '...'
    # [描述栏]
    desc_total_max = 900 # [描述] 栏位里只允许最多填写 1000 字（包含话题在内），但为了保险起见，这里特地减少了一定的字数最大值控制
    # 话题
    # （话题默认规则特别说明：由于 str..split(',') 对于空字符串会得到 [''] 这样的数组，那么后续填写话题时，点击一下<话题>按钮，在对空字符串回车的情况下，小红书会根据标题自动识别出合适的话题）
    # 只需要写话题文字即可，若多个话题，用英文逗号隔开即可，比如 搞笑,动画,...，若为空则使用默认规则填写
    upload_topic_list = str(video_config['upload_topic']).replace('，',',').split(',') # 避免出现中文逗号的错误情况，提前把中文逗号替换成英文逗号
    # 上传视频的[描述栏]填写规则：先读取配置参数，若配置参数为空，则使用默认规则
    upload_desc = str(video_config['upload_desc'])
    if upload_desc.replace(' ','') == '':
        if not upload_title.replace(' ','') == '':
            # 若本视频已设置的独立的 上传标题，那有限默认使用上传标题
            upload_desc = upload_title
        else:
            # 否则，默认情况下，使用原始视频的标题(title)作为内容
            upload_desc = get_video_source_title_by_name(video_file_name)
    
    # [视频封面]
    cover_img_file = video_config['upload_cover']

    # 把视频文件输入到上传按钮中，执行上传视频操作
    upload_input = driver.find_element_by_class_name('upload-input')
    upload_input.send_keys(video_file_path)
    # 输入标题
    upload_title = upload_title
    upload_title_input = driver.find_element_by_xpath('//*[@id="publish-container"]/div/div[2]/div[2]/div[3]/input')
    upload_title_input.send_keys(upload_title)
    # 输入描述前面的话题
    input_topic_into_el(upload_topic_list)
    # 输入描述内容
    # 由于 [话题] 也在 [描述栏里]，总字数不可超过 1000 所以描述的内容要进行一定控制
    # 由于 [话题] 的格式比较特殊，比如"影视"是2个字，变成话题后字数实际是5个字(加了#号和空格以及一个隐藏字符)，也就是说，话题实际所占字数为：原字数+3
    # 所以话题所占字数计算公式为：话题实际字数占位 = 纯字数 + (话题个数 * 3)
    upload_topic__ = str(video_config['upload_topic'])
    if upload_topic__.replace(' ','') == '':
        upload_topic__ = upload_default_topics
    topic_len = len(upload_topic__.replace(' ','').replace(',','')) + (len([i for i in upload_topic__.split(',') if not i == '']) * 3)
    log_print(f'topic_len = {topic_len}')
    # 那么剩余 [描述内容] 可填写的字数就如下
    desc_constent_max = desc_total_max - topic_len
    log_print(f'desc_constent_max = {desc_constent_max}')
    log_print(f'upload_desc = {upload_desc}')
    log_print('len(upload_desc) = {}'.format(len(upload_desc)))
    # 若字数超出，则截取其中一定长度的文字，并追加省略号 ...
    if len(upload_desc) > desc_constent_max:
        upload_desc = upload_desc[:desc_total_max - 10] + '...'
    log_print(f'输入的描述内容：\n{upload_desc}')
    upload_desc_input = driver.find_element_by_xpath('//*[@id="post-textarea"]')
    upload_desc_input.send_keys(upload_desc)
    # 点击单选<公开>
    permission_public_radio = driver.find_element_by_xpath('//*[@id="publish-container"]/div/div[2]/div[2]/div[8]/div[3]/div[2]/div[1]/label')
    permission_public_radio.click()
    # 点击单选<立即发布>
    pubtime_atonce_radio = driver.find_element_by_xpath('//*[@id="publish-container"]/div/div[2]/div[2]/div[8]/div[5]/div[2]/label[1]')
    pubtime_atonce_radio.click()
    # 编辑封面
    edit_cover(driver,cover_img_file)

    log_print(f'避免视频没有上传完成，等待 {pub_wait_sec} 秒后，再点击发布...')
    force_sleep(pub_wait_sec)
    # 点击按钮<发布>
    pub_btn = driver.find_element_by_xpath('//*[@id="publish-container"]/div/div[2]/div[2]/div[9]/button[1]')
    # pub_btn = driver.find_element_by_class_name('submit')
    pub_btn.click()

    # 检查是否存在刚发布的视频数据
    if check_upload_success(upload_title):
        # 发布成功后，视频名称记录到本地文档，以供后续查询
        write_uploaded_remember_txt(video_file_name)
    else: # 若发布数据里不存在刚发布的视频，则重新发布该条视频
        force_sleep(10)
        driver.get(xiaohongshu_clip_tool_url)
        force_sleep(6)
        upload_video_one(driver,video_file_path,video_config)

def upload_videos():
    video_file_dir = video_new_dir
    # 从视频上传菜单里读取上传视频的名单，按照名单顺序进行上传视频（获取的名单已经经过了排除处理，是排除了 video_exclude.txt 中的名单）
    video_config_list = read_upload_video_menu(video_upload_menu_xiaohongshu_txt_name)
    # 过滤掉已经上传过的视频
    video_config_list = [i for i in video_config_list if not read_uploaded_remember_to_judge_isuploaded(i['title'])]
    log_print(f'此次要上传的视频列表：\n{video_config_list}')
    if len(video_config_list) > 0:
        for video_config in video_config_list:
            video_file_name = video_config['title']
            video_file_path = f'{video_file_dir}/{video_file_name}.mp4'
            log_print('\n---------- 正在上传的视频文件 ------------')
            log_print(video_file_path)
            # 一定要确保要上传的文件是存在的，避免中途误删除的问题
            if os.path.exists(video_file_path):
                try:
                    # 开始逐个视频上传                
                    upload_video_one(driver,video_file_path,video_config)
                    # 点击发布之后，会跳回原来的上传视频的页面，直接继续下一轮视频发布即可
                    force_sleep(10)
                    # # 若想确保回到上传视频页面，就可以用下面的功能，定位url
                    # # 重新返回到上传视频的地址，然后开始下一轮的上传视频操作
                    # driver.get(xiaohongshu_clip_tool_url)
                    # force_sleep(10)
                except Exception as ex:
                    log_print(f'上传失败，发生异常：{ex}')
                    write_uploaded_remember_txt(video_file_name,True)
                    force_sleep(6)
                    driver.get(clip_tool_url)
                    force_sleep(6)

def upload2xiaohongshu():
    global driver
    global cookie_str
    driver = create_driver()
    # 读取本地存储 cookie ，只要登录过一次后，便可跳过登录验证
    json_obj = read_xiaohongshu_cookie(driver)
    check_pass = json_obj['check_pass']
    cookie_str = json_obj['cookie_str']
    cookie_items = json_obj['cookie_items']
    log_print(f'check_pass = {check_pass}')
    if check_pass:
        cookie_str = cookie_str
        # 把 cookie 填入当前浏览器的网站内
        log_print(f'----- 准备把 cookie 填入当前浏览器的网站内\ncookie_items\n{cookie_items}')
        add_cookie_item_into_web(driver,cookie_items)
        # cookie 若有效，上面会直接填入网站，重新直接定位到上传页面（可直接跳过登录）
        driver.get(clip_tool_url)
        # driver.refresh()
        force_sleep(6)
        # 开始上传视频
        upload_videos()
        log_print('-------------- 视频全部上传发布完毕 --------------')
    else:
        log_print('------- 小红书 cookie 验证失败，请检查代码后重试')
    
    # 定位到首页
    driver.get('https://creator.xiaohongshu.com/creator/home?roleType=creator')
    driver.close()

# if __name__ == '__main__':
#     upload2xiaohongshu()
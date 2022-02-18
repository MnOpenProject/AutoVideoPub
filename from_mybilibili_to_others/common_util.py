from time import sleep
from datetime import datetime
from .common_config import __CURPATH__,request_all_video_remember_dir,video_redeal_config_dir,video_download_exclude_txt,video_upload_menu_dir,personal_info_py_name,personal_info_path,cookie_txt_path,bilibili_request_headers,cookie_xiaohongshu_txt_path,xiaohongshu_request_headers,logs_out_dir,download_file_dir,covert_file_dir,tsfiles_root_dir,video_new_dir
import eventlet,os,importlib
import ffmpy3,json,subprocess,shutil,requests

''' ------------------- 移除所有自动创建的文件夹和文件 start -------------------'''

def clear_all_folderfiles_of_autocreate():
    # 会移除一些自动创建的目录和文件，会使得整个项目回到几乎初始时的状态（但不会清理掉 video_exclude/, video_upload_menu/, video_redeal_config/ 这类记录型的文件
    # 会移除的目录有：logs/, request_video_all/, video_flv/, video_mp4/, video_tsfiles/, video_new_mp4/, personal_info/, /b_cookie.txt, /xhs_cookie.txt 

    # logs/
    if os.path.exists(logs_out_dir):
        del_files(logs_out_dir)
        os.rmdir(logs_out_dir)
    # request_video_all/
    if os.path.exists(request_all_video_remember_dir):
        del_files(request_all_video_remember_dir)
        os.rmdir(request_all_video_remember_dir)
    # video_flv/
    if os.path.exists(download_file_dir):
        del_files(download_file_dir)
        os.rmdir(download_file_dir)
    # video_mp4/
    if os.path.exists(covert_file_dir):
        del_files(covert_file_dir)
        os.rmdir(covert_file_dir)
    # video_tsfiles/
    if os.path.exists(tsfiles_root_dir):
        tsfloder_list = os.listdir(tsfiles_root_dir)
        for tsfloder_name in tsfloder_list:
            tsfloder_dir = f'{tsfiles_root_dir}/{tsfloder_name}'
            if os.path.exists(tsfloder_dir):
                del_files(tsfloder_dir)
                os.rmdir(tsfloder_dir)
        del_files(tsfiles_root_dir)
        os.rmdir(tsfiles_root_dir)
    # video_new_mp4/
    if os.path.exists(video_new_dir):
        del_files(video_new_dir)
        os.rmdir(video_new_dir)
    # /personal_info.py
    if os.path.exists(personal_info_path):
        os.remove(personal_info_path)
    # /b_cookie.txt
    if os.path.exists(cookie_txt_path):
        os.remove(cookie_txt_path)
    # /xhs_cookie.txt
    if os.path.exists(cookie_xiaohongshu_txt_path):
        os.remove(cookie_xiaohongshu_txt_path)

''' ------------------- 移除所有自动创建的文件夹和文件 end -------------------'''

# 获取视频文件的时长
# 参考地址：https://blog.csdn.net/lilongsy/article/details/121206810
def get_duration_from_ffmpeg(url):
    # [url] 可以是本地文件的绝对路径，也可以是在线地址 https://xxx
    tup_resp = ffmpy3.FFprobe(
        inputs={url: None},
        global_options=[
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format', '-show_streams'
        ]
    ).run(stdout=subprocess.PIPE)

    meta = json.loads(tup_resp[0].decode('utf-8'))
    return meta['format']['duration']

# 判定是否为纯整数字符串
def is_int_str(str):
    try:
        int(str)
        return True
    except:
        return False

# 选项输入
def input_selection():
    selection = input()
    selection = 1 if not is_int_str(selection) else int(selection)
    return selection

def time_sleep(value):
    with eventlet.Timeout(30, False):  # 设置超时间
        sleep(value)

# 强制睡眠方法
def force_sleep(wait_sec):
    log_print(' ------ 强制等待，第 {} 秒 ----- '.format(wait_sec))
    time_sleep(wait_sec)

# 自定义的 log 输出方法
cur_timestamp = str(datetime.now().timestamp()).replace('.','')
def log_print(str_content,file_name='common'):
    # 在终端打印
    print(str_content)
    # 输出到日志文件
    logs_dir = logs_out_dir
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    # _log 前面改成当前的脚本文件名称
    f_path = f'{logs_dir}/{file_name}_{cur_timestamp}.log'
    # 写入文本
    fp = open(f_path,"a",encoding="utf-8")
    fp.write('{0}\n'.format(str_content))
    fp.close()

# 删除一个文件夹下的所有文件
# EXAMPLE_PATH = r'C:\Users\shenping\PycharmProjects\Shenping_TEST\day_5\Testfolder'
def del_files(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_files(c_path)
        else:
            os.remove(c_path)

# 获取个人信息脚本模块
def get_personal_info_module():
    # 动态引入脚本
    module_str = f"from_mybilibili_to_others.{personal_info_py_name}"
    module_config = importlib.import_module(module_str)
    return module_config

# 检查个人信息信息是否完整，程序必须基于这些参数才能正常执行，否则无法访问接口和完成登录功能
def check_personal_info():
    check_pass = True
    if not os.path.exists(personal_info_path):
        fp = open(personal_info_path,"w",encoding="utf-8")
        str_content = ''
        # 后续如有其他信息需要扩展，可继续这样追加其他内容
        str_content += "b_phone = '' # B站登录账号绑定的手机号\n" # B站登录账号绑定的手机号
        str_content += "xiaohongshu_phone = '' # 小红书登录账号绑定的手机号\n" # 小红书登录账号绑定的手机号
        fp.write(str_content)
        fp.close()
    # 获取个人信息脚本模块
    module_config = get_personal_info_module()
    b_phone = str(module_config.b_phone)
    xiaohongshu_phone = str(module_config.xiaohongshu_phone)
    if b_phone.replace(' ','') == '':
        print(f'{personal_info_path}中参数不完整：\n请填写 b_phone (B站登录账号绑定的手机号)')
        check_pass = False
    if xiaohongshu_phone.replace(' ','') == '':
        print(f'{personal_info_path}中参数不完整：\n请填写 xiaohongshu_phone (小红书登录账号绑定的手机号)')
        check_pass = False
    return check_pass

# 读取本地存储的 B站 cookie 记录
def read_blibli_cookie_from_txt():
    f_path = cookie_txt_path
    if not os.path.exists(f_path):
        print('{} --> 不存在'.format(f_path))
        return ''
    cookie_str = ''
    for remember_line_ in open(f_path):
        remember_line = remember_line_.replace('\n','').replace('\r','')
        cookie_str = f'{cookie_str}{remember_line}'
    print(f'cookie：\n{cookie_str}')
    print('\n------------------------------------------------------------------------\n')
    return cookie_str

# 把 B站 需要的 cookie 写入文本
def write_blibli_cookie_into_txt(cookie_str):
    fp = open(cookie_txt_path,"w",encoding="utf-8")
    str_content = cookie_str
    fp.write(str_content)
    fp.close()

# 检测 cookie 是否有效
def check_cookie_validity(cookie_str,url,headers,response_status_name='code'):
    # params response_status_name: 不同的后台接口 restful 风格不同，返回的表示接口错误码的属性 key 名称也不同，该参数根据不同的接口设置接口
    headers['Cookie'] = cookie_str
    r = requests.request(method='GET',url=url,headers=headers)
    print(f'r.status_code = {r.status_code}')
    if r.status_code == 200:
        res = json.loads(r.content)
        print(f'res = {res}')
        print(f"res['{response_status_name}'] = {res[response_status_name]}")
        if res[response_status_name] == 0:
            return True
    return False

# 检测 B站 cookie 是否有效
def check_bilibili_cookie_validity(cookie_str):
    headers = bilibili_request_headers
    url = f'https://member.bilibili.com/x/web/archives?status=pubed&pn=1&ps=10&coop=1&interactive=1'
    return check_cookie_validity(cookie_str,url,headers,'code')

# ------------------------------------- 小红书 cookie --- start ------------------------------------------

# 检测 小红书 cookie 是否有效
def check_xiaohongshu_cookie_validity(cookie_str):
    headers = xiaohongshu_request_headers
    url = f'https://creator.xiaohongshu.com/api/galaxy/creator/home/latest_note_data'
    return check_cookie_validity(cookie_str,url,headers,'result')

# 读取本地存储的 小红书 cookie 记录
# 第一行存的是 cookie 的完整字符串
# 后面几行存的是 从浏览器里读取出来的 cookie json 对象 item（这是为了方便进入 小红书 网站时，直接把cookie填入浏览器，就不用每次都重复登录了）
def read_xiaohongshu_cookie_from_txt():
    f_path = cookie_xiaohongshu_txt_path
    if not os.path.exists(f_path):
        print('{} --> 不存在'.format(f_path))
        return ''
    cookie_str = ''
    cookie_items = []
    rd_idx = 0
    for remember_line_ in open(f_path):
        remember_line = remember_line_.replace('\n','').replace('\r','')
        if rd_idx == 0:
            # 第一行存的是 cookie 的完整字符串
            cookie_str = remember_line
        else:
            # 后面几行存的是 从浏览器里读取出来的 cookie json 对象 item（
            json_obj = json.loads(remember_line)
            cookie_items.append(json_obj)
            # cookie_items.append(remember_line)
        rd_idx += 1
    print(f'cookie：\n{cookie_str}')
    print(f'cookie_items\n{cookie_items}')
    print('\n------------------------------------------------------------------------\n')
    return {'cookie_str':cookie_str,'cookie_items':cookie_items}

# 把 小红书 需要的 cookie 写入文本
# 第一行存的是 cookie 的完整字符串
# 后面几行存的是 从浏览器里读取出来的 cookie json 对象 item（这是为了方便进入 小红书 网站时，直接把cookie填入浏览器，就不用每次都重复登录了）
def write_xiaohongshu_cookie_into_txt(cookie_str,cookie_items):
    str_content = cookie_str
    for item in cookie_items:
        # 遍历 json 对象，把其中的值都转为 str 类型，这样读取的时候，重新转回 json 对象才不会报错（json.loads() 函数转 json 对象必须其中的所有属性值都是 str 类型，否则报错）
        for key_name in item:
            item[key_name] = str(item[key_name])
        json_str = json.dumps(item,ensure_ascii=False)
        # json_str = item
        str_content = '{0}\n{1}'.format(str_content,json_str)
    fp = open(cookie_xiaohongshu_txt_path,"w",encoding="utf-8")
    fp.write(str_content)
    fp.close()

# ------------------------------------- 小红书 cookie --- end ------------------------------------------

# 由于文件命名规则，下载的视频title要进行处理后才能用作视频文件名
def get_video_name_by_title(video_title):
    return str(video_title).replace(' ','_') # 把空格转为下划线，因为在转MP4方法中文件名不允许出现空格符

# 通过视频文件名，获取视频的原始标题（即 上面函数的反向转换）
def get_video_source_title_by_name(video_file_name):
    return str(video_file_name).replace('_',' ') # 把空格转为下划线，因为在转MP4方法中文件名不允许出现空格符

upload_rember_dir = f'{__CURPATH__}/upload_remember'
upload_rember_xhs_txt_path = f'{upload_rember_dir}/xiaohongshu_remember.txt'
# 读取已上传的视频记录文件，并判定当前视频是否已经上传过
def read_uploaded_remember_to_judge_isuploaded(upload_file_name):
    f_path = upload_rember_xhs_txt_path
    if not os.path.exists(f_path):
        log_print('{} --> 不存在'.format(f_path))
        return False
    for remember_line_ in open(f_path,encoding='utf-8'):
        remember_line = remember_line_.replace('\n','').replace('\r','').replace(error_suffix_flag,'')
        if remember_line == upload_file_name:
            log_print(f'-- 视频 【{upload_file_name}】 存在上传记录 ---')
            return True
    log_print(f'{upload_file_name} --> 没有上传记录')
    return False

# 编辑发布时发生错误异常的视频文件，则存储记录时会打上这个错误记号(后缀)
error_suffix_flag = '__error'
# 将当前已成功发布到B站的视频记录下来，下次再执行程序时，会读取记录，并排除已发布过的视频
def write_uploaded_remember_txt(upload_file_name,error_file=False):
    # 输出记录文件的目录
    # upload_rember_path
    if not os.path.exists(upload_rember_dir):
        os.makedirs(upload_rember_dir)

    # 如果是编辑发布时发生错误异常的视频文件，则存储记录时会打上错误记号(后缀)
    error_suffix = '' if error_file == False else error_suffix_flag
    # 每一行记录的名称，都跟要上传的视频文件名称保持一致，这样方便读取的时候可以直接进行比对
    upload_file_str = f'{upload_file_name}{error_suffix}'
    
    # 如果记录已存在，那么不再重复记录
    if read_uploaded_remember_to_judge_isuploaded(upload_file_name):
        return
    f_path = upload_rember_xhs_txt_path
    # 写入文本
    # 每一行记录的名称，都跟要上传的视频文件名称保持一致，这样方便读取的时候可以直接进行比对
    str_content = upload_file_str
    fp = open(f_path,"a",encoding="utf-8") # 以追加模式写入
    fp.write('{0}\n'.format(str_content))
    fp.close()

# 把数据列表写入文本的通用函数
def write_data_list_into_txt(data_list,txt_dir,txt_name,rm_old=True,is_had_content=False):
    # params rm_old: 若为True，则会删除原来的 .txt 文件，否则不删除并继续追加内容

    # 输出记录文件的目录
    if not os.path.exists(txt_dir):
        os.makedirs(txt_dir)
    # 每一行记录的名称，都跟要上传的视频分段文件名称保持一致，这样方便读取的时候可以直接进行比对
    f_path = f'{txt_dir}/{txt_name}.txt'
    if rm_old and os.path.exists(f_path):
        os.remove(f_path)
    # 写入文本
    # 每一行记录的名称，都跟要上传的视频分段文件名称保持一致，这样方便读取的时候可以直接进行比对
    str_content = ''
    for video_idx,video_title in enumerate(data_list):
        if video_idx == 0 and not is_had_content:
            str_content = f'{video_title}'
        else:
            str_content = f'\n{video_title}'
        fp = open(f_path,"a",encoding="utf-8") # 以追加模式写入
        fp.write('{0}'.format(str_content))  
        fp.close()

# 每次请求 aid 数据时，会把所有请求的视频的 title 都记录到这个目录下
request_remember_txt_name = 'request_remember'
def write_request_remember_txt(video_title_list):
    write_data_list_into_txt(video_title_list,request_all_video_remember_dir,request_remember_txt_name)

# 每次请求 aid 数据时，也会把所有的视频的相关数据整理成一份配置（json 格式），存储到该目录下，然后在重新处理视频时(掐头去尾这类操作)，会从这里读取相应的配置参数
def write_redeal_config_txt(video_json_list):
    # params video_json_list: 每一个元素都是一个json, json 案例为：{'aid':'xxx','title':'xxx','rm_header_tail_time_long':'00:01:01,00:01:01'}
    # 其中 'rm_header_tail_time_long':'00:01:01,00:01:01' 就是重新处理视频时，需要选取的视频的时间范围 '需要减去的开头时长,需要减去的结尾时长'

    # 先读取已有的配置文件，如果已存在相同的，则排除掉，只刷选出需要新增的内容
    is_had_content = False # 用于判定文本中是否已存在内容
    new_video_json_list = []
    txt_dir = video_redeal_config_dir
    txt_name = 'redeal_config'
    f_path = f'{txt_dir}/{txt_name}.txt'
    if os.path.exists(f_path):
        for video_json in video_json_list:
            video_title = video_json['title']
            exist = False
            rd_idx = 0
            for remember_line_ in open(f_path,encoding='utf-8'):
                rd_idx += 1
                remember_line = remember_line_.replace('\r','').replace('\n','')
                if rd_idx == 1 and not remember_line == '':
                    is_had_content = True
                config_json = json.loads(remember_line)  
                if video_title == config_json['title']:
                    exist = True
                    break
            if not exist:
                new_video_json_list.append(video_json)
    else:
        new_video_json_list = video_json_list
    
    # 要想随后正常读取出 json 中的中文，需要把数组中的 json 都转为 json 格式字符串
    # 注意：json.dumps(i,ensure_ascii=False) 中的 ensure_ascii=False 是确保中文不会被转义，默认情况下 json.dumps(xxx) 是会把其中的中文进行转义的
    new_video_json_list = [json.dumps(i,ensure_ascii=False) for i in new_video_json_list]

    # 把经过筛选后的数据写入到文本中
    write_data_list_into_txt(new_video_json_list,video_redeal_config_dir,'redeal_config',False,is_had_content)

# 根据视频的 title 去本地文件里查找相应的配置参数
def read_redeal_config(video_title):
    txt_dir = video_redeal_config_dir
    txt_name = 'redeal_config'
    f_path = f'{txt_dir}/{txt_name}.txt'
    if os.path.exists(f_path):
        for remember_line_ in open(f_path,encoding="utf-8"):
            remember_line = remember_line_.replace('\r','').replace('\n','')
            json_config = json.loads(remember_line)
            if video_title == json_config['title']:
                return json_config
    return None

# 从视频排除文档中读取，检查是否属于排除项
def is_in_exclude_txt(video_title):
    if os.path.exists(video_download_exclude_txt):
        for line in open(video_download_exclude_txt,encoding='utf-8'):
            line = line.replace('\r','').replace('\n','')
            if line == video_title:
                return True
    return False

# 获取需要上传的视频名单
# 菜单会结合 request_video_all/request_remember.txt 和 video_exclude/video_exclude.txt 中的内容，整理出一份需要上传的菜单
def get_video_upload_init_data():
    # 菜单会结合 request_video_all/request_remember.txt 和 video_exclude/video_exclude.txt 中的内容，整理出一份需要上传的菜单

    # 收集请求的所有视频名单
    request_video_title_list = []
    request_remember_txt_path = f'{request_all_video_remember_dir}/{request_remember_txt_name}.txt'
    for line in open(request_remember_txt_path,encoding='utf-8'):
        line = line.replace('\r','').replace('\n','')
        if not line == '':
            request_video_title_list.append(line)
    
    # 收集要排除的视频名单
    exculde_video_title_list = []
    exculde_txt_path = video_download_exclude_txt
    for line in open(exculde_txt_path,encoding='utf-8'):
        line = line.replace('\r','').replace('\n','')
        if not line == '':
            exculde_video_title_list.append(line)
    
    # 整理出一份要上传的菜单
    upload_video_title_list = []
    for video_title in request_video_title_list:
        exclude_list = [i for i in exculde_video_title_list if i == video_title]
        # 若当前视频title不在排除名单内，则提取出来
        if len(exclude_list) < 1:
            upload_video_title_list.append(video_title)

    return upload_video_title_list

# 输出一份视频上传菜单（后续的上传视频操作会根据该菜单中的顺序依次上传视频）
# 在上传之前如果需要修改顺序，可以修改该菜单后，再执行自动上传操作
def create_upload_video_menu(txt_name):
    # params txt_name: 是针对平台有不同的文本，比如 上传到小红书的话，就是使用 common_config.py 里的 video_upload_menu_xiaohongshu_txt_name 变量

    # 目录不存在则创建
    if not os.path.exists(video_upload_menu_dir):
        os.makedirs(video_upload_menu_dir)
    
    # 整理出一份要上传的菜单
    upload_video_title_list = get_video_upload_init_data()
    print(f'upload_video_title_list = {upload_video_title_list}')

    # 创建一份 上传菜单的 json 对象列表
    # 使用者在上传之前编辑想要填写的内容，上传时会根据其中的参数，在对应的栏位填写对应的内容
    # （如果其中的内容为空，则上传时会默认使用默认的规则进行填写，具体规则需要在上传脚本里查看对应的注释）
    upload_json_list = []
    for v_title in upload_video_title_list:  #男士烫发[话题]# 
        v_item = {
            'title': v_title, # 下载视频时保存的title
            'upload_title': '', # 上传时，[标题栏]里填写的内容（需使用者自行编写，若为空则使用默认规则填写）
            'upload_topic': '', # 上传时，[描述栏]里最前面#标注的[话题]（需使用者自行编写，只需要写话题文字即可，若多个话题，用英文逗号隔开即可，比如 搞笑,动画,...，若为空则使用默认规则填写）
            'upload_desc': '' # 上传时，[描述栏]里填写的内容（需使用者自行编写，若为空则使用默认规则填写）
        }
        upload_json_list.append(json.dumps(v_item,ensure_ascii=False))
    # 倒序排列一下(这样可以使得上传视频时，默认从最早的一期视频开始上传)
    upload_json_list = upload_json_list[::-1]

    # 写入到文本中
    # upload_menu_path = f'{video_upload_menu_dir}/{txt_name}.txt'
    # is_had_content = False # 判定文本中是否已有内容，这影响到追加内容是否换行
    # if os.path.exists(upload_menu_path):
    #     rd_idx = 0
    #     for line in upload_menu_path:
    #         rd_idx += 1
    #         line = line.replace('\r','').replace('\n','')
    #         if rd_idx == 1 and not line == '':
    #             is_had_content = True
    #             break
    # write_data_list_into_txt(upload_video_title_list,video_upload_menu_dir,txt_name,True,is_had_content)

    # 若文本已存在，为了避免删除原来已经更改过的上传名单，将原来的文件重新复制出一份，作为保留记录
    # 使用者如果还想用原来的名单，可以把内容复制进去（因为可能每次下载的视频都不一致，原来的顺序也不一定是准确的）
    # 所以程序只会每次都根据当前的下载视频名单来创建一个新文本，至于原来的顺序就需要使用者自己手动复制过来进行整理了
    upload_menu_path = f'{video_upload_menu_dir}/{txt_name}.txt'
    if os.path.exists(upload_menu_path):
        # 每次保留的文本后面会追加当前的时间字符串
        # cur_timestamp_str = str(datetime.now().timestamp()).replace('.','')
        cur_timestamp = datetime.now().timestamp()
        dateArray = datetime.utcfromtimestamp(cur_timestamp)
        time_str = dateArray.strftime("%Y_%m_%d__%H_%M_%S")
        target_file = f'{video_upload_menu_dir}/{txt_name}_{time_str}.txt'
        shutil.copyfile(upload_menu_path,target_file)

    # 每次都移除旧文本，创建新文本（即覆盖原内容）    
    print('--------------------------------------------------------------')
    print(f'upload_json_list = {upload_json_list}')
    print(f'video_upload_menu_dir = {video_upload_menu_dir}')
    print(f'txt_name = {txt_name}')
    write_data_list_into_txt(upload_json_list,video_upload_menu_dir,txt_name)

# 从文本中读取上传视频的菜单，上传视频时需要根据此文本中的顺序进行依次上传视频
def read_upload_video_menu(txt_name):
    upload_json_list = []
    upload_menu_path = f'{video_upload_menu_dir}/{txt_name}.txt'
    if os.path.exists(upload_menu_path):
        for line in open(upload_menu_path,encoding='utf-8'):
            line = line.replace('\r','').replace('\n','')
            if not line == '':
                upload_json_list.append(line)
    # 读取时，需要把其中的 json 字符串逐一转为 json 对象
    upload_json_list = [json.loads(i) for i in upload_json_list]
    return upload_json_list
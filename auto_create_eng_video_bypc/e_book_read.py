''' 电子书自动生成视频 '''
''' 
利用 <必剪app> 里的文字视频模板直接把这里生成的音频文件变成文字视频
【注1】：但是因为 文字视频模板 不支持导入超过 10 分钟的音频，所以需要手动把txt原始文本进行拆分，确保每次到处的音频是在10分钟以内的
【注1】：因为代码里是通过句号来拆分句子的进行逐句音频下载的，所以标题后面一定要记得自己手动加个句号，否则会被跟接下来的句子合在一起读出来，这效果就不对了
'''

import os,requests,re
from .module_root import __MODULEROOTPATH__
from .common.common_util import debug_input,is_int_str,del_files
from .combine_audio import combine_audio_files,add_silence_headend_for_audio
from auto_clip_video_byandroid.auto_upload_video_to_blibli import pub_common_main_func
from .baidu_audio_api import download_audio_by_baiduapi

# 用于自动发布时取用名字的txt文本名称的前缀
pub_file_prefix = 'pubname_'

# 图片尺寸（即最终输出视频对画面尺寸）(宽,高)
article_img_size = (520, 960)
# 一个屏幕上的最大显示字数（会根据这个数值将一篇原始文本分成N个组）
screen_font_count_max = 100

# 字符集存放目录（字符集 即 字体的样式，比如 宋体之类的）
fonts_dir = f'{__MODULEROOTPATH__}/fonts'
# 【可根据自行需求更改】字符集文件名称，可以自行在网络上下载字符集文件，然后放到上面的 /fonts 目录下
# 注：目前实际测下来，并非支持所有的字符集，有的会导致无法绘制（如果更换了字符集之后，发现在合成视频的步骤里发生问题，并没有输出合成视频，就说明并不支持当前设置的字符集）
# 【中文字符集】
zh_ttc_file_full_name = 'GenRyuMinTWBold.ttf' #  演示夏行楷 'xiaxingkai.ttf'  # 'msyh.ttc' # 宋体：'simsun.ttc'

# 视频背景图片存储目录
screen_bg_image_dir = f'{__MODULEROOTPATH__}/bg_dir'
# 视频背景图片名称(包含后缀名)，若需要修改，请把要修改的图片放到上面的 /bg_dir 目录下
screen_bg_image_full_name = 'darkstudy.jpg'

# ----------- [纯中文 原文] 字体参数 start -----------
article_screen_bg_image_full_name = screen_bg_image_full_name
article_ttc_fonts_dir = fonts_dir
# 文本处理成图片并生成视频，需要统一确定图片的尺寸，从而决定最终生成的视频尺寸
article_font_size = 30 # 字体的尺寸大小
article_font_line_h = article_font_size + 10 # 字体的行高，字体变大了行高也要相应变大
article_txt_margin_left = 100
article_screen_margin_top = int(round(article_img_size[1] / 12)) # 文字距离图片(即最终生成视频屏幕)顶部的间距
# 文本要根据图片的尺寸实现自动换行，这个值控制一行上最多存放多少个英文字符(1个英文字母占1字节，一个中文字符占2字节)
# 最后的 -5 是一个为了避免单词过长换行效果不佳，而多减去的一个值
article_screen_line_char_len_max = int(round(article_img_size[0] / 5,0)) * (article_font_size*0.0072) # int(round(1.653442,0)) 是四舍五入取整(单纯的 round(1.653442,0) 会变成 2.0 所以前面加个 int() 去掉.0)
# ----------- [纯中文 原文] 翻译视频的字体参数 end -----------

# 文件生成的根目录
e_book_dir = f'{__MODULEROOTPATH__}/e_book_dir'
# 电子书原始文件存放目录
e_book_source_dir = f'{e_book_dir}/e_book_source_dir'
# 一份电子书原始文本的每一句的音频存放目录
audio_e_book_source_dir = f'{e_book_dir}/audio_e_book_source_dir'
# # 一份电子书原始文本的每一句的优化音频的存放目录
# sentence_audio_better_dir = f'{e_book_dir}/sentence_audio_better_dir'
# 一份电子书原始文本的合并后的完整音频存放目录
audio_combine_e_book_source_dir = f'{e_book_dir}/audio_combine_e_book_source_dir'
# # 一份电子书文本的分页存放目录
# e_book_txt_pages_dir = f'{e_book_dir}/e_book_txt_pages_dir'
# # 分页文本的音频存放目录
# audio_e_book_pages_dir = f'{e_book_dir}/audio_e_book_pages_dir'
# # 一组文本的视频存放目录
# video_e_book_pages_dir = f'{e_book_dir}/video_e_book_pages_dir'
# # 选择多个视频进行组合后的视频存放目录
# video_e_book_combine_full_dir = f'{e_book_dir}/e_book_group_full_video_dir'

# 初始化目录
def init_dir():
    if not os.path.exists(e_book_dir):
        os.makedirs(e_book_dir)
    if not os.path.exists(e_book_source_dir):
        os.makedirs(e_book_source_dir)
    if not os.path.exists(audio_e_book_source_dir):
        os.makedirs(audio_e_book_source_dir)
    # if not os.path.exists(sentence_audio_better_dir):
    #     os.makedirs(sentence_audio_better_dir)
    if not os.path.exists(audio_combine_e_book_source_dir):
        os.makedirs(audio_combine_e_book_source_dir)
    # if not os.path.exists(e_book_txt_pages_dir):
    #     os.makedirs(e_book_txt_pages_dir)
    # if not os.path.exists(audio_e_book_pages_dir):
    #     os.makedirs(audio_e_book_pages_dir)
    # if not os.path.exists(video_e_book_pages_dir):
    #     os.makedirs(video_e_book_pages_dir)
    # if not os.path.exists(video_e_book_combine_full_dir):
    #     os.makedirs(video_e_book_combine_full_dir)


# 终端询问选择下载发音音频的 API 平台
def ask_select_download_language_audio_api():
    # hint_options = [
    #     '[{}] - 百度 API',
    #     '[{}] - 有道 API'
    # ]
    # for opt_i,opt in enumerate(hint_options):
    #     print(opt.format(opt_i+1))
    # print('\n请选择下载源 API：(默认 [1])')
    # user_selected = input()
    # user_selected = '1' if not is_int_str(user_selected) else user_selected
    # user_selected = '1' if int(user_selected) < 1 or int(user_selected) > len(hint_options) else str(user_selected)
    # user_selected_idx = int(user_selected)-1
    # selected_selection = hint_options[user_selected_idx]
    # print('[*] - 已选择：{}\n'.format(selected_selection))
    # # 函数集合
    # func_ary = [
    #     download_audio_by_baiduapi,
    #     download_language_audio_by_youdao
    # ]
    # return func_ary[user_selected_idx]

    # 暂时放弃使用百度API，因为发现百度API特别不好用，限制字数太少，而且报错说没有免费额度，简直垃圾
    return download_language_audio_by_youdao
    

# 通过有道翻译接口，句子输出成音频到本地
def download_language_audio_by_youdao(out_dir,content:str,se_id=1,le='eng',audio_name=None):
    # params audio_name: 下载到本地的音频文件的名称，默认为 None；若为 None 则使用 se_id 参数进行命名

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    print(f'\n------------------ 通过有道翻译接口，查询语句翻译 开始... ---------------------\n')
    print(f'【*】查询语句：\n{content}')
    print(f'【{content}】音频下载中...\n')
    sentence_words = content.split(' ')
    sentence_words = [w for w in sentence_words if not str(w).replace(' ', '') == '']
    sentence_words_str = ''
    for s_i,ss in enumerate(sentence_words):
        sentence_words_str = ss if s_i == 0 else f'{sentence_words_str}+{ss}'
    print(f'sentence_words_str = {sentence_words_str}')
    # 我的有道翻译 API 管理地址：https://ai.youdao.com/console/#/service-singleton/text-translation
    # type=2 声音音色类型(目前觉得第2种女生音色比较好听)
    url = f'https://dict.youdao.com/dictvoice?audio={sentence_words_str}&type=2&le={le}' # le=eng 英语发音; le=zh 中文发音

    # 发起请求
    r = requests.request(method='GET',url=url)
    contentType = r.headers['Content-Type']
    # res = json.loads(r.content) # r.content 就是浏览器调试接口里看到的响应体
    print(f'Content-Type = {contentType}')
    if contentType == "audio/mpeg":
        # print(f'r \n {r.content}')
        # millis = int(round(time.time() * 1000))
        # print(f'millis = {millis}')
        audio_file_name = str(se_id) if audio_name == None else str(audio_name)
        fpath = f"{out_dir}/{audio_file_name}.mp3"
        if os.path.exists(fpath):
            os.remove(fpath)
        fp = open(fpath, 'wb')
        fp.write(r.content)
        fp.close()
        print(f'【{content}】音频下载完成，保存路径如下\n{fpath}')
        return fpath
    return None

# 选择一份要处理的电子书原始文本
def ask_for_one_book_source(is_pub=False):
    book_list = os.listdir(e_book_source_dir)
    # 若不是发布，则排除那些用于发布的txt文本
    if not is_pub:
        book_list = [fn for fn in book_list if not pub_file_prefix in fn]
    else:
        # 若是自动发布，则只筛选出那些用于发布时取用名称的txt文本
        book_list = [fn for fn in book_list if pub_file_prefix in fn]

    hint_options = []
    for opt_i,opt in enumerate(book_list):
        num = opt_i+1
        hint_options.append(f'[{num}] - {opt}')
    print('\n------------------------------------------\n')
    for hint in hint_options:
        print(hint)
    print('\n请选择一份原始文本：(默认 [1])')
    user_selected = input()
    user_selected = '1' if not is_int_str(user_selected) else user_selected
    user_selected = '1' if int(user_selected) < 1 or int(user_selected) > len(hint_options) else str(user_selected)
    user_selected_idx = int(user_selected)-1
    selected_selection = hint_options[user_selected_idx]
    print('[*] - 已选择：{}\n'.format(selected_selection))
    return book_list[user_selected_idx]
    
def read_book_source(file_full_name):
    content = ''
    fpath = f'{e_book_source_dir}/{file_full_name}'
    for line in open(fpath,encoding='utf-8'):
        line = line.replace('\r','')
        if not line.replace(' ','') == '':
            content = f'{content}{line}'
    return content

# 【电子书分解】：一本完整的电子书txt分解成适合做成视频的多份txt（分组管理），一份txt的文字就是视频里的一段固定的画面
def download_book_source_audio():
    book_file_full_name = ask_for_one_book_source()
    print(book_file_full_name)
    txt_file_name = book_file_full_name.strip('txt')

    font_count_max = screen_font_count_max
    # 读取一份电子书txt的所有文字
    book_content = read_book_source(book_file_full_name)
    # 先下载一份完整的文章音频
    save_content_audio_path = download_article_txt_audio(book_content,txt_file_name)
    if save_content_audio_path == None:
        print('！！！！！！ 合并被终端，请检查并处理掉错误后，再重新执行 ！！！！！')
        return
    print(book_content)

    print('\n============================================\n')
    print('文章的完整音频输出完成：')
    print(save_content_audio_path)

    # # 进行合理分页
    # book_content_font_count = len(book_content)
    # int_val = int(book_content_font_count/font_count_max)
    # more_one_page = 0 if book_content_font_count%font_count_max == 0 else 1
    # page_count = int_val + more_one_page
    # print(f'book_content_font_count = {book_content_font_count}')
    # print(f'font_count_max = {font_count_max}')
    # print(f'int_val = {int_val}')
    # print(f'more_one_page = {more_one_page}')
    # print(f'page_count = {page_count}')
    # print(f' book_content_font_count%font_count_max = { book_content_font_count%font_count_max}')

    # # 根据分页数量，将文字分组存入数组
    # content_list = []
    # for p_i in range(page_count):
    #     start_idx = p_i * font_count_max
    #     end_idx = start_idx + font_count_max
    #     cur_content = book_content[start_idx:end_idx]
    #     content_list.append(cur_content)
    # print(content_list)

# 先下载一份完整的文章音频
def download_article_txt_audio(book_content:str,txt_file_name:str):    
    audio_out_dir = f'{audio_e_book_source_dir}/{txt_file_name}'
    if not os.path.exists(audio_out_dir):
        os.makedirs(audio_out_dir)
    # 对一段较长的文字下载一份完整的音频
    return download_language_audio_long_content(book_content,txt_file_name,audio_out_dir)

# 把一些不适合用于朗读的文字内容过滤掉
def sentence_str_filter(content:str):
    content = content.replace('[','(').replace(']',')').replace('……','')
    # 从字符串中截取出括号内容（截取出的字符串是不包括两个括号的）
    p1 = re.compile(r'[(](.*?)[)]', re.S) # 最小匹配
    remove_list = re.findall(p1,content)
    # 把字符串里的括号内的包括括号都移除掉
    for s in remove_list:
        content = content.replace(f'({s})','')
    return content

# 对一段较长的文字下载一份完整的音频
# 由于不能一次性下载一个完整的发音文件（文字内容太长了），所以要拆分成句子，逐句下载发音音频文件，然后本地手动合成完整的音频
def download_language_audio_long_content(book_content:str,txt_file_name:str,audio_out_dir):
    # 逐句下载的音频存放到一个单独的文件夹下，方便稍后取用，然后合成一个完整的音频
    audio_sentences_dir = f'{audio_out_dir}/{txt_file_name}'
    if not os.path.exists(audio_sentences_dir):
        os.makedirs(audio_sentences_dir)
    else:
        del_files(audio_sentences_dir)
    # 把完整的文字内容按特定符号进行拆分
    # book_content_new  = book_content.replace('\r','').replace('\n','').replace(' ','').replace('？','，').replace('！','，').replace('：','，').replace('。','，').replace('；','，')
    # sentence_list = book_content_new.split('，') # 因为百度 API 限制一次下载音频对应的文字数量太少了，所以这里为了确保每一句尽量短，上面把所有结尾的符号都统一变成逗号，并按照逗号进行分割
    book_content_new  = book_content.replace('\r','').replace('\n','').replace(' ','')
    sentence_list = book_content_new.split('。') # 因为百度 API 限制一次下载音频对应的文字数量太少了，所以这里为了确保每一句尽量短，上面把所有结尾的符号都统一变成逗号，并按照逗号进行分割
    sentence_list = [s for s in sentence_list if not s.replace(' ','') == '']
    sentence_audio_path_list = []
    # 终端询问选择用哪个平台的 API
    download_language_audio_by_api = ask_select_download_language_audio_api()
    for sen_i,sen in enumerate(sentence_list):
        sen = sentence_str_filter(sen)
        audio_path = download_language_audio_by_api(audio_sentences_dir, sen, se_id=(sen_i+1), le='zh')
        sentence_audio_path_list.append(audio_path)

    # # 对下载的句子进行逐句优化处理（若直接把每一句句子合并，不同的音频之间会出现0间断的问题，所以要给每个句子音频之间添加一段静音）
    # sentence_audio_better_path_list = []
    # audio_better_sentences_dir = f'{sentence_audio_better_dir}/{txt_file_name}'
    # if not os.path.exists(audio_better_sentences_dir):
    #     os.makedirs(audio_better_sentences_dir)
    # else:
    #     del_files(audio_better_sentences_dir)
    # for s_path_i, s_path in enumerate(sentence_audio_path_list):
    #     try:
    #         sentence_audio_better_path = f'{audio_better_sentences_dir}/{s_path_i+1}.mp3'
    #         add_silence_headend_for_audio(source_audio_full_path=s_path,out_audio_full_path=sentence_audio_better_path,silence_sec=0.2,position='end')
    #         sentence_audio_better_path_list.append(sentence_audio_better_path)
    #     except Exception as ex:
    #         print(f'\n！！！！！！！！！\n优化失败:{ex}\n请检查原因后再重新合并，此次合并中断：\n{sentence_audio_better_path}\n！！！！！！！！！\n')
    #         return None
    
    # 合并所有句子的音频文件
    print('\n============================================\n')
    print('句子音频下载完毕，开始执行音频合并，请稍后...\n')
    save_content_audio_dir = f'{audio_combine_e_book_source_dir}/{txt_file_name}'
    if not os.path.exists(save_content_audio_dir):
        os.makedirs(save_content_audio_dir)
    else:
        del_files(save_content_audio_dir)
    save_content_audio_path = f'{save_content_audio_dir}/{txt_file_name}.mp3'
    combine_audio_files(sentence_audio_path_list,out_audio_full_path=save_content_audio_path,silence_sec=0.2)

    return save_content_audio_path

def pub_book_source():
    book_file_full_name = ask_for_one_book_source(True)
    print(book_file_full_name)
    txt_file_name = book_file_full_name.strip(pub_file_prefix).strip('txt')
    print('\n============================================\n')
    print(f'要发布的文章名称：{txt_file_name}')
    print('\n============================================\n')
    # 截取出电子书的名称
    # 电子书txt命名请一定确保按此规则名 '西游记_吴承恩_第一回_猴王出世_1'
    # 这样就能通过第一个下划线的索引来截取作品名称了
    first_span_char_index = txt_file_name.find('_')
    book_name = txt_file_name[0:first_span_char_index] # 截取书名
    # 发布参数
    upload_title_full = f'[{txt_file_name}] -- [视频听书]'
    upload_dynamic = f'[{book_name}]\n-- 一起来回味原著\n-- 特别适合休闲、恰饭、睡前享用哦'
    article_source = '资源来自网络'
    instroduction = f'{upload_title_full}\n-- {upload_dynamic}\n--{article_source}'
    pub_params_json = {
        'firth_partition':'知识',
        'second_partition':'校园学习',
        'upload_title': upload_title_full,
        'upload_dynamic':upload_dynamic,
        'instroduction': instroduction,
        'pub_tag_str': '知识分享官', # 活动话题
        'upload_tags': '学习,电子书,休闲,生活,校园,读书,经典' # 视频的普通标签
    }
    pub_common_main_func(book_file_full_name,pub_params_json)

# =======================================================================================

def main_func(selected_selection):
    init_dir()
    # ----------------------------- 选择要执行的功能 ----------------------------------
    print('\n----------------------------- 选择要执行的功能 ----------------------------------\n')
    print('【注】：目前需要人工对分集，就是说一份txt文档中的内容不能过多，否则容易报错')
    hint_options_init = [
        '[{0}] - <电子书视频> -- 【电子书音频】：下载一本完整的电子书txt的完整发音音频（拆分成句子，逐句下载发音音频文件，然后本地手动合成完整的音频）',
    # 以下思路注释掉的原因：发现《必剪app》里自带的文字视频模板+已合成的音频后，就能做成很完美的文字读书视频了，自己就不用实现读书视频功能了
    #   '[{0}] - <电子书视频> -- 【电子书分页】：一本完整的电子书txt分解成适合做成视频的多份（每一份文字数量不要超出视频画面，即将文本进行分页展示）',
    #   '[{0}] - <电子书视频> -- 【电子书音频】：下载一组txt对应的发音音频，并进行加工处理',
    #   '[{0}] - <电子书视频> -- 【电子书视频】：根据一组txt对应音频时长，生成相应的视频',
    #   '[{0}] - <电子书视频> -- 【电子书视频--完整一集】：将一组txt对应的多个视频合成一个完整的视频',
      '[{0}] - <电子书视频> -- 【发布】：必剪app自动发布 -- 发布某一期电子书的某一集'
    ]
    hint_options = []
    for opt_i,opt in enumerate(hint_options_init):
      hint_options.append(opt.format(opt_i+1))

    print('请选择要操作的功能：(默认 [1])')
    for hint in hint_options:
      print(hint)
    user_selected = input()
    user_selected = '1' if not is_int_str(user_selected) else user_selected
    user_selected = '1' if int(user_selected) < 1 or int(user_selected) > len(hint_options) else str(user_selected)
    user_selected_idx = int(user_selected)-1
    selected_selection = hint_options[user_selected_idx]
    print('[*] - 已选择：{}\n'.format(selected_selection))

    if user_selected == '1':
        #  <电子书视频> -- 【电子书音频】：下载一本完整的电子书txt的完整发音音频（拆分成句子，逐句下载发音音频文件，然后本地手动合成完整的音频）
        download_book_source_audio()
    if user_selected == '2':
        #  <电子书视频> -- 【电子书音频】：下载一本完整的电子书txt的完整发音音频（拆分成句子，逐句下载发音音频文件，然后本地手动合成完整的音频）
        pub_book_source()
    
    

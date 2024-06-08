''' 制作每日英语文章阅读视频的脚本 '''
import math,random,json,os,re,requests,uuid,time,hashlib,functools,shutil
from .common.common_util import debug_input,ask_for_selection,del_files
from .common.ffmpeg_util import get_duration_from_ffmpeg
from auto_create_eng_video_bypc.module_root import __MODULEROOTPATH__
from .eng_study_daily_read_words_lib import words_lib
from .config import difficult_word_len_min,youdao_api_daily_eng,eng_symbol_ttc_file_full_name,eng_ttc_file_full_name,zh_ttc_file_full_name,fonts_dir,screen_bg_image_dir,screen_bg_image_full_name
from .config_words_video_combine_data import words_whole_videos_dir as need_combine_words_whole_videos_dir,\
    combine_words_whole_videos_dir, combine_words_video_file_name,\
    words_whole_videos as need_combine_words_whole_videos
from .convert_txt_to_img import txt_to_img
from .convert_img_to_video import img_to_video,combine_audio_video_by_ffmpeg,combine_videos_by_ffmpeg
from .combine_audio import combine_audio_files,add_silence_headend_for_audio
from .eng_study_daily_read_words_lib import words_lib as my_words_lib
from .auto_upload_video_to_blibli import pub_common_main_func

# 图片尺寸（即最终输出视频对画面尺寸）(宽,高)
article_img_size = (1080, 720)

# ----------- [纯英文 原文] 字体参数 start -----------
article_screen_bg_image_full_name = 'darkstudy.jpg'
article_ttc_fonts_dir = fonts_dir
# 文本处理成图片并生成视频，需要统一确定图片的尺寸，从而决定最终生成的视频尺寸
article_font_size = 30 # 字体的尺寸大小
article_font_line_h = article_font_size + 10 # 字体的行高，字体变大了行高也要相应变大
article_txt_margin_left = 100
article_screen_margin_top = int(round(article_img_size[1] / 12)) # 文字距离图片(即最终生成视频屏幕)顶部的间距
# 文本要根据图片的尺寸实现自动换行，这个值控制一行上最多存放多少个英文字符(1个英文字母占1字节，一个中文字符占2字节)
# 最后的 -5 是一个为了避免单词过长换行效果不佳，而多减去的一个值
article_screen_line_char_len_max = int(round(article_img_size[0] / 5,0)) * (article_font_size*0.0072) # int(round(1.653442,0)) 是四舍五入取整(单纯的 round(1.653442,0) 会变成 2.0 所以前面加个 int() 去掉.0)
# ----------- [纯英文 原文] 翻译视频的字体参数 end -----------

# ----------- [逐句] 翻译视频的字体参数 start -----------
sentence_screen_bg_image_full_name = screen_bg_image_full_name
sentence_ttc_fonts_dir = fonts_dir
sentence_eng_ttc_file_full_name = eng_ttc_file_full_name
sentence_zh_ttc_file_full_name = zh_ttc_file_full_name
# 文本处理成图片并生成视频，需要统一确定图片的尺寸，从而决定最终生成的视频尺寸
sentence_font_size = 35 # 字体的尺寸大小
sentence_eng_font_size = sentence_font_size
sentence_zh_font_size = sentence_font_size - 5
sentence_font_line_h = sentence_font_size + 10 # 字体的行高，字体变大了行高也要相应变大
sentence_screen_margin_left = 80
sentence_screen_margin_top = int(round(article_img_size[1] / 8)) # 文字距离图片(即最终生成视频屏幕)顶部的间距
# 文本要根据图片的尺寸实现自动换行，这个值控制一行上最多存放多少个英文字符(1个英文字母占1字节，一个中文字符占2字节)
# 最后的 -5 是一个为了避免单词过长换行效果不佳，而多减去的一个值
sentence_screen_line_char_len_max = int(round(article_img_size[0] / 6,0)) * (sentence_font_size*0.0072) # int(round(1.653442,0)) 是四舍五入取整(单纯的 round(1.653442,0) 会变成 2.0 所以前面加个 int() 去掉.0)
# ----------- [逐句] 翻译视频的字体参数 end -----------

# ----------- [单词] 翻译视频的字体参数 start -----------
word_img_screen_bg_path = 'darkstudy.jpg'
word_ttc_fonts_dir = fonts_dir
word_font_size = 60 # 字体的尺寸大小
word_eng_font_size = word_font_size
word_zh_font_size = word_font_size - 30
word_eng_font_line_h = word_font_size + 10 # 字体的行高，字体变大了行高也要相应变大
word_zh_font_line_h = word_zh_font_size + 10 # 字体的行高，字体变大了行高也要相应变大
word_img_txt_margin_left = 80
word_screen_margin_top = int(round(article_img_size[1] / 8)) # 文字距离图片(即最终生成视频屏幕)顶部的间距
# 文本要根据图片的尺寸实现自动换行，这个值控制一行上最多存放多少个英文字符(1个英文字母占1字节，一个中文字符占2字节)
# 最后的 -5 是一个为了避免单词过长换行效果不佳，而多减去的一个值
word_screen_line_char_len_max = int(round(article_img_size[0] / 13,0)) * (word_font_size*0.0072) # int(round(1.653442,0)) 是四舍五入取整(单纯的 round(1.653442,0) 会变成 2.0 所以前面加个 int() 去掉.0)
# ----------- [单词] 翻译视频的字体参数 end -----------

# 当前脚本需要的相关文件目录（无论是生成的还是需要手动填写的文件，都会在该目录下）
eng_study_daily_read_dir = f'{__MODULEROOTPATH__}/eng_study_daily_read'

# ------- 以下目录中的文件都以精确到天的日期命名且一一对应，比如：2022_02_28.txt，则以下几个目录下必然都有一份该文件 -----
# 因为该视频一天最多只会发一期，所以叫做《每日英语文章阅读》

# 文本要根据图片的尺寸实现自动换行，这个值控制一行上最多存放多少个英文字符(1个英文字母占1字节，一个中文字符占2字节)
# 最后的 -5 是一个为了避免单词过长换行效果不佳，而多减去的一个值
screen_line_char_len_max = math.ceil(article_img_size[0] / 10) - 5

# 文章原文目录（该目录下的文章有可能时我手动填写的，也有可能会通过其他脚本自动生成进去）
# 但是为了能够让后续进行逐句拆分，必须定下如下规则：
# [1] - 文本中的第一行，会被当作为标题，其余行的内容被认为是文章内容
# [2] - 每一句结尾必须是英文格式的 句号+空格（". "），因为后续会按照此标志来逐句拆分
# [3] - 为了能够兼容一些特殊感情的句子（疑问句和感叹句），程序在拆分句子之前，会为每个问号和感叹号后面加一个英文格式的句号"."
article_source_dir = f'{eng_study_daily_read_dir}/article_source_dir'
# 原文逐句拆分后的内容目录
sentences_dir = f'{eng_study_daily_read_dir}/sentences_dir'
# 原文逐句拆分后与之一一对应的翻译信息目录
translations_dir = f'{eng_study_daily_read_dir}/translations_dir'
# 从原文中提取单词并翻译到文本目录
words_tranlations_dir = f'{eng_study_daily_read_dir}/words_tranlations_dir'
# 记录此次正在操作的文件，以便下次操作的时候一个参考，分步操作时间长了容易忘记上一次正在制作哪篇文章
option_remember_file = f'{eng_study_daily_read_dir}/option_remember_file.txt'
# 一篇文章的完整发音音频文件存储目录
articlefull_audio_dir = f'{eng_study_daily_read_dir}/audio_articlefull_dir'
# 英语语句发音音频文件存储目录
sentences_audio_dir = f'{eng_study_daily_read_dir}/audio_sentences_dir'
# 英语句子发音音频加工后的新音频文件存储目录
sentences_audio_better_dir = f'{eng_study_daily_read_dir}/audio_sentences_better_dir'
# 中文翻译语句发音音频文件存储目录
translations_audio_dir = f'{eng_study_daily_read_dir}/audio_translations_dir'
# 英文单词音频文件存储目录
words_audio_dir = f'{eng_study_daily_read_dir}/audio_words_dir'
# 英语单词发音音频加工后的新音频文件存储目录
words_audio_better_dir = f'{eng_study_daily_read_dir}/audio_words_better_dir'
# 单词翻译发音音频文件存储目录
words_translations_audio_dir = f'{eng_study_daily_read_dir}/audio_words_translations_dir'
# 单词音频解析失败的单词记录存储目录
# （在实际测试过程中，发现下载下来的音频中存在无法解析的音频，这些音频则记录在该文档中，在所有的处理中会进行排除）
words_fail_remember_dir = f'{eng_study_daily_read_dir}/words_fail_remember_dir'
# 单词发音音频和翻译音频的合成音频的存储目录
words_translations_combine_audio_dir = f'{eng_study_daily_read_dir}/audio_words_translations_combine_dir'
# 单词视频文件存储目录
words_translations_video_dir = f'{eng_study_daily_read_dir}/words_translations_video_dir'
# 一篇文章的所有单词视频最终合成的完整视频的存储目录
words_translations_whole_video_dir = f'{eng_study_daily_read_dir}/words_translations_whole_video_dir'
# 单词翻译转图片的存储目录
words_translations_img_dir = f'{eng_study_daily_read_dir}/words_translations_img_dir'
# 文本转为图片视频的存储目录
txt_to_img_dir = f'{eng_study_daily_read_dir}/txt_to_img_dir'
# 图片转为视频的存储目录
img_to_video_dir = f'{eng_study_daily_read_dir}/img_to_video_dir'
# 生成逐句翻译视频时的图片存储目录
sentences_txt_to_img_dir = f'{eng_study_daily_read_dir}/sentences_txt_to_img_dir'
# 逐句生成翻译视频时，合成音频存储目录
sentences_translations_audio_dir = f'{eng_study_daily_read_dir}/audio_sentences_translations_dir'
# 逐句生成翻译视频时，文本转为图片视频的存储目录
sentences_translations_img_to_video_dir = f'{eng_study_daily_read_dir}/sentences_translations_img_to_video_dir'
# 合并“原文跟读”和的“逐句翻译跟读”视频的存储目录
article_and_sentences_read_video_dir = f'{eng_study_daily_read_dir}/article_and_sentences_read_video_dir'
def init_dir():
    print('-------------------------\n')
    print('脚本需要的相关文件目录:' + eng_study_daily_read_dir)
    print('文章原文目录:' + article_source_dir)
    print('原文逐句拆分后的内容目录:' + sentences_dir)
    print('原文逐句拆分后与之一一对应的翻译信息目录:' + translations_dir)
    print('\n---- 以上目录已生成 ----\n')
    if not os.path.exists(word_ttc_fonts_dir):
        os.makedirs(word_ttc_fonts_dir)
    if not os.path.exists(screen_bg_image_dir):
        os.makedirs(screen_bg_image_dir)
    if not os.path.exists(eng_study_daily_read_dir):
        os.makedirs(eng_study_daily_read_dir)
    if not os.path.exists(article_source_dir):
        os.makedirs(article_source_dir)
    if not os.path.exists(sentences_dir):
        os.makedirs(sentences_dir)
    if not os.path.exists(translations_dir):
        os.makedirs(translations_dir)
    if not os.path.exists(words_tranlations_dir):
        os.makedirs(words_tranlations_dir)
    if not os.path.exists(articlefull_audio_dir):
        os.makedirs(articlefull_audio_dir)
    if not os.path.exists(sentences_audio_dir):
        os.makedirs(sentences_audio_dir)
    if not os.path.exists(sentences_audio_better_dir):
        os.makedirs(sentences_audio_better_dir)
    if not os.path.exists(translations_audio_dir):
        os.makedirs(translations_audio_dir)
    if not os.path.exists(words_audio_dir):
        os.makedirs(words_audio_dir)
    if not os.path.exists(words_audio_better_dir):
        os.makedirs(words_audio_better_dir)
    if not os.path.exists(words_translations_audio_dir):
        os.makedirs(words_translations_audio_dir)
    if not os.path.exists(words_fail_remember_dir):
        os.makedirs(words_fail_remember_dir)
    if not os.path.exists(words_translations_combine_audio_dir):
        os.makedirs(words_translations_combine_audio_dir)
    if not os.path.exists(words_translations_video_dir):
        os.makedirs(words_translations_video_dir)
    if not os.path.exists(words_translations_whole_video_dir):
        os.makedirs(words_translations_whole_video_dir)
    if not os.path.exists(words_translations_img_dir):
        os.makedirs(words_translations_img_dir)
    if not os.path.exists(txt_to_img_dir):
        os.makedirs(txt_to_img_dir)
    if not os.path.exists(img_to_video_dir):
        os.makedirs(img_to_video_dir)
    if not os.path.exists(sentences_txt_to_img_dir):
        os.makedirs(sentences_txt_to_img_dir)
    if not os.path.exists(sentences_translations_audio_dir):
        os.makedirs(sentences_translations_audio_dir)
    if not os.path.exists(sentences_translations_img_to_video_dir):
        os.makedirs(sentences_translations_img_to_video_dir)
    if not os.path.exists(article_and_sentences_read_video_dir):
        os.makedirs(article_and_sentences_read_video_dir)

def clear_some_tmp_dirs():
    try:
        if os.path.exists(sentences_dir):
            del_files(sentences_dir)
            os.rmdir(sentences_dir)
        if os.path.exists(translations_dir):
            del_files(translations_dir)
            os.rmdir(translations_dir)
        if os.path.exists(words_tranlations_dir):
            del_files(words_tranlations_dir)
            os.rmdir(words_tranlations_dir)
        if os.path.exists(articlefull_audio_dir):
            del_files(articlefull_audio_dir)
            os.rmdir(articlefull_audio_dir)
        if os.path.exists(sentences_audio_dir):
            del_files(sentences_audio_dir)
            os.rmdir(sentences_audio_dir)
        if os.path.exists(sentences_audio_better_dir):
            del_files(sentences_audio_better_dir)
            os.rmdir(sentences_audio_better_dir)
        if os.path.exists(translations_audio_dir):
            del_files(translations_audio_dir)
            os.rmdir(translations_audio_dir)
        if os.path.exists(words_audio_dir):
            del_files(words_audio_dir)
            os.rmdir(words_audio_dir)
        if os.path.exists(words_audio_better_dir):
            del_files(words_audio_better_dir)
            os.rmdir(words_audio_better_dir)
        if os.path.exists(words_translations_audio_dir):
            del_files(words_translations_audio_dir)
            os.rmdir(words_translations_audio_dir)
        if os.path.exists(words_translations_combine_audio_dir):
            del_files(words_translations_combine_audio_dir)
            os.rmdir(words_translations_combine_audio_dir)
        if os.path.exists(words_translations_video_dir):
            del_files(words_translations_video_dir)
            os.rmdir(words_translations_video_dir)
        if os.path.exists(words_translations_whole_video_dir):
            del_files(words_translations_whole_video_dir)
            os.rmdir(words_translations_whole_video_dir)
        if os.path.exists(words_translations_img_dir):
            del_files(words_translations_img_dir)
            os.rmdir(words_translations_img_dir)
        if os.path.exists(txt_to_img_dir):
            del_files(txt_to_img_dir)
            os.rmdir(txt_to_img_dir)
        if os.path.exists(img_to_video_dir):
            del_files(img_to_video_dir)
            os.rmdir(img_to_video_dir)
        if os.path.exists(sentences_txt_to_img_dir):
            del_files(sentences_txt_to_img_dir)
            os.rmdir(sentences_txt_to_img_dir)
        if os.path.exists(sentences_translations_audio_dir):
            del_files(sentences_translations_audio_dir)
            os.rmdir(sentences_translations_audio_dir)
        if os.path.exists(sentences_translations_img_to_video_dir):
            del_files(sentences_translations_img_to_video_dir)
            os.rmdir(sentences_translations_img_to_video_dir)
        if os.path.exists(article_and_sentences_read_video_dir):
            del_files(article_and_sentences_read_video_dir)
            os.rmdir(article_and_sentences_read_video_dir)
    except Exception as ex:
        clear_some_tmp_dirs()

def clear_img_tmp_dirs():
    try:
        if os.path.exists(words_translations_img_dir):
            del_files(words_translations_img_dir)
            os.rmdir(words_translations_img_dir)
    except Exception as ex:
        clear_img_tmp_dirs()

# 一个单词的翻译信息存入本地文本（提前把翻译在本地存好，需要的时候直接从本地读取，不需要访问接口，更加方便快捷）
# 一个单词收集完所有翻译信息后，最后加的这个分隔符，代表一个单词翻译的结束
# 用于存入文本后再读取时可以通过此标记进行识别一个单词的翻译信息
word_trans_end = '====== end ======'
def write_word_transinfo_into_txt(file_full_name,trans_str_list):
    if not os.path.exists(words_tranlations_dir):
        os.makedirs(words_tranlations_dir)
    content_str = ''
    for idx,trans_str in enumerate(trans_str_list):
        # 最后加个分隔符，代表一个单词翻译的结束，存入文本后再读取时可以通过此标记进行识别一个单词的翻译信息
        trans_str = f'{trans_str}\n{word_trans_end}'
        # 追加到文本字符串
        content_str = trans_str if idx == 0 else f'{content_str}\n{trans_str}'
    fpath = f'{words_tranlations_dir}/{file_full_name}'
    if os.path.exists(fpath):
        os.remove(fpath)
    fp = open(fpath,'w',encoding='utf-8')
    fp.write(content_str)
    fp.close()
    print(f'单词翻译信息已写入文本：\n{fpath}')

# 读取本地一存储的单词翻译信息
def read_word_transinfo_from_txt(file_full_name):
    fpath = f'{words_tranlations_dir}/{file_full_name}'
    if not os.path.exists(fpath):
        print(f'文件不存在：\n{fpath}')
        return None
    word_list = [] # 单独收集的单词，数量与下面的transinfo_list集合一一对应
    transinfo_list = [] # 用于收集单词翻译信息的集合
    trans_str = '' # 一个单词信息字符串
    idx = 0
    for line in open(fpath,encoding='utf-8'):
        line = line.replace('\r','').replace('\n','')
        # 遇到结尾符号，说明一个单词的翻译信息结束
        if line == word_trans_end:
            idx = 0
            transinfo_list.append(trans_str) # 一个单词翻译结束，把整理好的信息字符串追加到集合中
        else:
            if idx == 0:
                word_list.append(line)
            trans_str = line if idx == 0 else f'{trans_str}\n{line}'
            idx += 1
    return {
        'word_list': word_list,
        'word_transinfo_list':transinfo_list
    }

# 通过有道翻译接口，查询单词翻译，并整理到本地文本中
def transform_word_list_by_youdao(file_full_name,difficult_word_list):
    print(f'\n------------------ 通过有道翻译接口，查询单词翻译 开始... ---------------------\n{file_full_name}\n')
    # 收集单词翻译信息
    transform_info_list = []
    for word in difficult_word_list:
        print(f'【*】查询单词：\n{word}')
        print('****** 翻译信息如下 *******')
        url = f'https://dict.youdao.com/jsonapi_s?doctype=json&jsonversion=4&q={word}&le=en&t=5&client=web&sign=9762b20df4cc2c2470c4042dd431d438&keyfrom=webdict'
        print('\n************************************\n')
        print(f'require word translation url:\n{url}')
        print('\n************************************\n')
        r = requests.request(method='GET',url=url)
        # print(f'有道翻译接口反馈：\n{r}')
        res = json.loads(r.content) # r.content 就是浏览器调试接口里看到的响应体
        # 收集单词翻译文本
        transform_word_info = ''
        # 若接口响应体中存在 'typos' 推荐单词，说明这个单词没找到（这里不用收集，相当于会再次过滤掉一些不正确的单词）
        typos_key = 'typos'
        if typos_key in res:
            print(f'【{word}】单词不存在，可能拼错了！（该单词已被忽略收集）')
            if 'typo' in res[typos_key]:
                print('你要找的是不是：')
                for tpw in res[typos_key]['typo']:
                    print(f'tpw = {json.dumps(tpw,ensure_ascii=False)}')
                    if 'word' in tpw and 'trans' in tpw:
                        print(f"{tpw['word']}--{tpw['trans']}")
        else:
            try:
                # 美式发音音标
                usphone = res['simple']['word'][0]['usphone']
                usphone_str = f'[{usphone}]'
                # 有的单词有多种音标，目前视频不支持展示多种音标，太长了，画面尺寸不够，只取其中的第一个即可
                usphone_list = usphone.split(';')
                usphone_list = [up for up in usphone_list if not up.replace(' ','') == '']
                if len(usphone_list) > 1:
                    usphone_str = f'[{usphone_list[0]}]'
                # 英式发音音标
                ukphone = res['simple']['word'][0]['ukphone']
                ukphone_str = f'[{ukphone}]'
                # 有的单词有多种音标，目前视频不支持展示多种音标，太长了，画面尺寸不够，只取其中的第一个即可
                ukphone_list = ukphone.split(';')
                ukphone_list = [up for up in ukphone_list if not up.replace(' ','') == '']
                if len(ukphone_list) > 1:
                    ukphone_str = f'[{ukphone_list[0]}]'
                print('\n************************************\n')
                print('音标:\n')
                print(f"美式发音：{usphone_str}")
                print(f"英式发音：{ukphone_str}")
                print('\n************************************\n')
                # 单词拼写正确，整理出得到的翻译信息
                trans_data = res['ec']['word']
                # transform_word_info = f"{trans_data['return-phrase']}" # 要翻译的单词
                # transform_word_info = f"{trans_data['return-phrase']}\nUK:{ukphone_str}; US:{usphone_str}" # 要翻译的单词（选用发音音标加入到翻译中）
                transform_word_info = f"{trans_data['return-phrase']}\n英 {ukphone_str}; 美 {usphone_str}" # 要翻译的单词（选用发音音标加入到翻译中）(不要跟上面一下加冒号，否则渲染效果是冒号和中文会叠加，不好看，也不知怎么解决)
                # transform_word_info = f"{trans_data['return-phrase']}\n " # 要翻译的单词（选用发音音标加入到翻译中） 暂时音标用空格代替，这样对应音标的逻辑就不用改了，因为加入音标字符集有问题
                for tr in trans_data['trs']:
                    trans_str = f"{tr['pos']}--{tr['tran']};"
                    transform_word_info = f'{transform_word_info}\n{trans_str}'
                    transform_word_info = transform_word_info.replace('<', '(').replace('>', ')')  # 这种符号在发音时会被误以为时大于号和小于号，然后就读出声音来了
                transform_info_list.append(transform_word_info) # 追加到集合中
                print(transform_word_info)
                print('=====================')
            except Exception as ex:
                print(f'单词翻译请求操作发生异常，（该单词已被忽略收集）:\n{ex}')
                continue
            # print(f'整理出的翻译信息：\n{transform_word_info}')    
    # 把翻译信息存入本地文本
    write_word_transinfo_into_txt(file_full_name=file_full_name,trans_str_list=transform_info_list)
    print(f'\n{file_full_name}\n------------------ 通过有道翻译接口，查询单词翻译 结束 ---------------------\n')
    return transform_info_list

# 去除单词上一些特殊的符号
def filter_word_special_chars(word:str):
    word_new = word.replace("'s",'').replace("ing",'')
    return word_new

# 从一篇文章中提取出一些较难的单词
def filter_out_difficult_words(article:str,long_min=5):
    if long_min < 4:
        return []
    # params long_min： 用于作为提取单词的标准，凡是长度少于这个数的，都认为是较难单词进行提取
    article = article.replace('.','').replace(',','').replace('!','').replace('?','')

    word_list:list[str] = article.split(' ')
    word_list = [filter_word_special_chars(w) for w in word_list] # 去除掉单词上一些特殊的符号
    word_list = [w for w in word_list if len(w.replace("'s",'').replace('ing ','')) > long_min]
    # 对比已知单词库，排除那些已知的单词
    word_list = [w for w in word_list if not w in words_lib]

    # 若数量太少，则降低标准，继续提取
    if len(word_list) < 2:
        return filter_out_difficult_words(article,long_min-1)
    else:
        return word_list

# 对单词进行去重并排序
def word_list_resort(word_list:list[str]):
    # 为了保证原始单词不变，这种对比去重的方式最稳妥
    word_list_new = []
    for w in word_list:
        find_words = [w_j for w_j in word_list_new if str(w_j).lower() == str(w).lower()]
        find_words = [w_j for w_j in find_words if not str(w_j).replace(' ','') == ''] # 排除空字符元素
        if len(find_words) < 1:
            word_list_new.append(w)
    # 数组里的元素按照字符串的长度进行排序
    def compare_personal(x,y):
        return len(y) - len(x)
    word_list_new.sort(key=functools.cmp_to_key(compare_personal))
    return word_list_new

# 从原文中提取单词并翻译到文本
def export_words_translations_from_article_into_txt(article_obj):
    article_obj = split_article(article_obj)
    file_full_name = article_obj['file_full_name']
    article_title:str = article_obj['article_title']
    article_content:str = article_obj['article_content']
    # article_sentences = article_obj['article_content_list']
    # 从一篇文章中提取出一些较难的单词
    difficult_word_list = filter_out_difficult_words(f'{article_title}. {article_content}',difficult_word_len_min)
    difficult_word_list = word_list_resort(difficult_word_list)
    transform_word_list_by_youdao(file_full_name,difficult_word_list)

# 获取一段字符串的朗读音频时长（仅适合 中英双语 朗读音）（针对 英语朗读）
def get_eng_reader_audio_duration(text:str):
    text = sentence_str_filter(text)
    text = str(text).replace('. ',',').replace(' ',',').replace(', ',' ').replace(',',' ')
    # 这个单位时长是通过实际测试得到的计算值（63个）（仅适合 中英双语 朗读音）
    unit_duration = 63 / 3.5 # 63 / 3.5 = 18 即 63个字符生成的朗读音大约是3.5秒
    # 找出有多少个超长的单词，就增加对应的秒数（针对某些单词过长读音时长会比较长的问题）
    word_len_max = 8 #  设定一个超长的值
    long_words = [i for i in text.split(' ') if not i.replace(' ', '') == '']
    long_words = [i for i in long_words if len(i) >= word_len_max] # 找出有几个超长的单词
    long_word_count = len(long_words)
    add_sec_val = long_word_count * 0.3 # 计算出要增加多少额外的秒数
    text_len = len(text)
    duration =  text_len / unit_duration + add_sec_val
    return round(duration,2) # 保留2位小数

# 获取一段字符串的朗读音频时长（仅适合 中英双语 朗读音）（针对 中文朗读）
def get_ch_reader_audio_duration(text:str):
    text = sentence_str_filter(text)
    text = str(text).replace('. ',',').replace(' ',',').replace(', ',' ').replace(',',' ')
    # 这个单位时长是通过实际测试得到的计算值（22个）（仅适合 中英双语 朗读音） 
    unit_duration = 10 / 2.4 #  10 / 2.4 = 4.166 # 22 / 5.2 = 4.23 即 10个字符生成的朗读音大约是2.4秒
    # 找出有多少个超长的单词，就增加对应的秒数（针对某些单词过长读音时长会比较长的问题）
    word_len_max = 8 #  设定一个超长的值
    long_words = [i for i in text.split(' ') if not i.replace(' ', '') == '']
    long_words = [i for i in long_words if len(i) >= word_len_max] # 找出有几个超长的单词
    long_word_count = len(long_words)
    add_sec_val = long_word_count * 0.3 # 计算出要增加多少额外的秒数
    text_len = len(text)
    duration =  text_len / unit_duration + add_sec_val
    return round(duration,2) # 保留2位小数

# 把一些不适合用于朗读的文字内容过滤掉
def sentence_str_filter(content:str):
    # 从字符串中截取出括号内容（截取出的字符串是不包括两个括号的）
    p1 = re.compile(r'[(](.*?)[)]', re.S) # 最小匹配
    remove_list = re.findall(p1,content)
    # 把字符串里的括号内的包括括号都移除掉
    for s in remove_list:
        content = content.replace(f'({s})','')
    return content

# 把此次操作的文件记录到本地
def remember_option_into_article_txt(file_full_name,selction_hint):
    step_desc = selction_hint
    content_str = f'【{file_full_name}】 -- 步骤记录: 【{step_desc}】'
    fpath = option_remember_file
    fp = open(fpath,'w',encoding='utf-8')
    fp.write(content_str)
    fp.close()

# 读取操作记录中的内容
def read_option_remember_from_article_txt():
    content_str = ''
    fpath = option_remember_file
    if not os.path.exists(fpath):
        return ''
    for line in open(fpath, encoding='utf-8'):
        line = line.replace('\n','').replace('\r','')
        content_str = line
    return content_str

# 对文章文件进行排序，文件名是安装日期格式命名的，所以按照日期的从最早的到最新的进行排序
def sort_article_files(article_list):
    arr = article_list
    n = len(arr)
    # 遍历所有数组元素
    for i in range(n):
        # Last i elements are already in place
        for j in range(0, n-i-1):
            try:
                cur_item_dateformat = str(arr[j]).replace('.txt','').replace('_','-')
                cur_item = f'{cur_item_dateformat} 00:00:00'
                cur_item = time.mktime(time.strptime(cur_item, '%Y-%m-%d %H:%M:%S')) # 转为时间戳
                next_item_dateformat = str(arr[j+1]).replace('.txt','').replace('_','-')
                next_item = f'{next_item_dateformat} 00:00:00'
                next_item = time.mktime(time.strptime(next_item, '%Y-%m-%d %H:%M:%S')) # 转为时间戳
                # 通过转换后的时间戳进行对比
                if cur_item > next_item :
                    arr[j], arr[j+1] = arr[j+1], arr[j]
            except Exception as ex:
                continue
    return arr


# 询问选择一份原文文本，作为创作的来源，该函数会返回读取的文章内容字符串
def ask_select_article_source(selected_selection=None):
    article_list = os.listdir(article_source_dir)
    article_list = sort_article_files(article_list) # 对文章文件进行排序，文件名是安装日期格式命名的，所以按照日期的早晚进行排序
    if len(article_list) < 1:
        print('抱歉，当前没有任何文章来源可供选择，请先在以下目录下添加一份文章吧！')
        print(article_source_dir)
        print('---------------------------------\n')
        return None
    hint_options = []
    for idx,article_file_name in enumerate(article_list):
        hint_str = f'[{idx + 1}] - {article_file_name}'
        hint_options.append(hint_str)
    print('\n')
    last_option_remember = read_option_remember_from_article_txt()
    last_option_remember = f'\n上一次操作记录：{last_option_remember}' if not last_option_remember == '' else ''
    ask_hint_str=f'先选择一篇原文吧：{last_option_remember}'
    selction = None
    if selected_selection == None:
        selction = ask_for_selection(hint_options,hint_str=ask_hint_str)
    else:
        selction = selected_selection
    article_idx = int(selction) - 1
    # 读取文本
    file_full_name = article_list[article_idx]
    article_file_path = f'{article_source_dir}/{file_full_name}'
    article_title = ''
    article_content = ''
    rd_idx = 0
    for line in open(article_file_path,encoding='utf-8'):
        line = line.replace('\r','').replace('\n','')
        if not line.replace(' ', '') == '':
            if rd_idx == 0:
                # 第一行作为文章标题
                article_title = line
            else:
                # 其余行作为文章内容
                article_content += line
            rd_idx += 1
    return {
        'selected_selection': selction,
        'file_full_name': file_full_name,
        'article_title':article_title,
        'article_content':article_content
    } 

# 拆分原文内容
def split_article(article_obj,for_article_source=False):
    file_full_name = article_obj['file_full_name']
    article_title:str = article_obj['article_title']
    article_content:str = article_obj['article_content']
    article_sentences_1 = article_content.split('. ')
    # 再把句子按照逗号进行拆分，这是为了避免朗读音因为句子太长而读的太快
    article_sentences = []
    for sen in article_sentences_1:
        if not for_article_source:
            # 若是逐句翻译，则一定要是完整的句子，这样翻译才能精准
            sen = sentence_str_filter(sen) # 把一些不适合用于朗读的文字内容过滤掉
            article_sentences.append(sen)
        else:
            # 根据逗号拆解（为了让原文跟读更加清晰，原文跟读时会把语句再按照逗号隔开，这样可以再次切割朗读音，让朗读音简短一些，方便跟读）
            sen_j_list = sen.split(', ')
            article_sentences_j = []
            for sen_j_idx,sen_j in enumerate(sen_j_list):
                sen_j = sentence_str_filter(sen_j) # 把一些不适合用于朗读的文字内容过滤掉
                # 为了避免把一些逗号隔开的短句也分隔开，导致朗读音很奇怪，这里需要进行一定的判定
                sen_j_tmps = sen_j.split(' ') # 当前句子拆分成单词数组
                sen_j_last_tmps = sen_j_list[sen_j_idx - 1].split(' ') # 上一个句子拆分成单词数组
                # 这里逻辑还要优化，有 Anneliese Dodd, said the data showed women 这种情况，前一句数量不够，也要组合起来
                if sen_j_idx > 0 and (len(sen_j_tmps) < 7 or len(sen_j_last_tmps) < 7):
                    # 如果当前一句的数量少或上一句数量也少，则也进行组合成整体
                    article_sentences_j_enddx = len(article_sentences_j) - 1
                    article_sentences_j_end = article_sentences_j[article_sentences_j_enddx]
                    article_sentences_j[article_sentences_j_enddx] = f'{article_sentences_j_end}, {sen_j}'
                else:
                    article_sentences_j.append(sen_j)
            for asj in article_sentences_j:
                article_sentences.append(asj)
    print(article_sentences)
    article_sentences = [i for i in article_sentences if not i.replace(' ','') == '']
    article_obj_new = {
        'file_full_name': file_full_name,
        'article_title': article_title,
        'article_content': article_content,
        'article_content_list': article_sentences
    }
    return article_obj_new

# 把拆出的语句依次存入本地文本
def write_sentence_into_txt(article_title,article_sentences,file_full_name):
    # 写入本地文本
    content = article_title
    for i,s in enumerate(article_sentences):
        content = f'{content}\n{s}'
    sentences_path = f'{sentences_dir}/{file_full_name}'
    fp = open(sentences_path,'w',encoding='utf-8')
    fp.write(content)
    fp.close()

def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()

def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]

# 通过有道翻译接口，查询句子翻译，并整理到本地文本中
def transform_sentences_by_youdao(sentence_str):
    print(f'\n------------------ 通过有道翻译接口，查询语句翻译 开始... ---------------------\n')
    print(f'【*】查询语句：\n{sentence_str}')
    print('****** 翻译信息如下 *******')
    # 我的有道翻译 API 管理地址：https://ai.youdao.com/console/#/service-singleton/text-translation
    url = 'https://openapi.youdao.com/api'
    APP_KEY = youdao_api_daily_eng['APP_KEY']
    APP_SECRET = youdao_api_daily_eng['APP_SECRET']
    header = youdao_api_daily_eng['header']
    data = {}
    q = sentence_str
    data['from'] = '源语言'
    data['to'] = '目标语言'
    data['signType'] = 'v3'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['q'] = q
    data['salt'] = salt
    data['sign'] = sign
    data['vocabId'] = "您的用户词表ID"
    r = requests.request(method='POST',url=url,data=data,headers=header)
    contentType = r.headers['Content-Type']
    res = json.loads(r.content) # r.content 就是浏览器调试接口里看到的响应体
    if contentType == "audio/mp3":
        print(f'【{sentence_str}】这是音频，这里不支持这种翻译内容！！！\n')
    else:
        try:
            if not str(res['errorCode']) == '0':
                print(f'【{sentence_str}】请求翻译信息接口反馈报错！！！\n')
                print(f'------- res: \n{res}\n')
            else:
                # 获取翻译信息
                translations = res['translation']
                print(f'翻译内容：{translations}')
                if len(translations) > 0:
                    translation = translations[0]
                    return translation
        except Exception as ex:
            print(f'【{sentence_str}】获取翻译信息翻译出错：{ex}\n')
    return None

# 逐句翻译，并把翻译信息存入本地文本
def translate_sentences_into_txt(article_title:str,article_sentences:list,file_full_name:str):
    translation_list = []
    # 标题翻译
    title_translation = transform_sentences_by_youdao(article_title)
    if not title_translation == None:
            translation_list.append(title_translation)
    # 内容逐句翻译
    for sen in article_sentences:
        sen_translation = transform_sentences_by_youdao(sen)
        if not sen_translation == None:
            translation_list.append(sen_translation)
    # 写入本地文本
    content = ''
    for i,s in enumerate(translation_list):
        content = s if i == 0 else f'{content}\n{s}'
    translation_path = f'{translations_dir}/{file_full_name}'
    fp = open(translation_path,'w',encoding='utf-8')
    fp.write(content)
    fp.close()

# 读取拆分后的文章语句信息（read_article_sentences() 和 read_article_translations() 读取的数据集合是一一对应的）
def read_article_sentences(file_full_name):
    sentences = []
    fpath = f'{sentences_dir}/{file_full_name}'
    if not os.path.exists(fpath):
        print(f'文件不存在，请先生成该文件：\n{fpath}')
        return None
    for line in open(fpath,encoding='utf-8'):
        line = line.replace('\r','').replace('\n','')
        if not line.replace(' ','') == '':
            sentences.append(line)
    return sentences

# 读取翻译信息（read_article_sentences() 和 read_article_translations() 读取的数据集合是一一对应的）
def read_article_translations(file_full_name):
    translations = []
    fpath = f'{translations_dir}/{file_full_name}'
    if not os.path.exists(fpath):
        print(f'文件不存在，请先生成该文件：\n{fpath}')
        return None
    for line in open(fpath,encoding='utf-8'):
        line = line.replace('\r','').replace('\n','')
        if not line.replace(' ','') == '':
            translations.append(line)
    return translations


# 读取原文内容，并进行逐句拆分并翻译，最后整理好信息写入文本
def dealwith_article_into_text(article_obj):
    article_obj = split_article(article_obj)
    file_full_name = article_obj['file_full_name']
    article_title:str = article_obj['article_title']
    article_content:str = article_obj['article_content']
    article_sentences = article_obj['article_content_list']

    # 把拆出的语句依次存入本地文本
    write_sentence_into_txt(article_title,article_sentences,file_full_name)

    # 逐句翻译，并把翻译信息存入本地文本
    translate_sentences_into_txt(article_title,article_sentences,file_full_name)


def dealwith_article_all_into_local_audio(article_obj):
    article_obj = split_article(article_obj)
    file_full_name = article_obj['file_full_name']
    article_title: str = article_obj['article_title']
    article_content: str = article_obj['article_content']
    # article_sentences = article_obj['article_content_list']
    # sentences_translations = read_article_translations(file_full_name)

    article_full = f'{article_title}. {article_content}'

    audio_out_dir = f"{articlefull_audio_dir}/{file_full_name.replace('.txt', '')}"
    if not os.path.exists(audio_out_dir):
        os.makedirs(audio_out_dir)
    else:
        del_files(audio_out_dir)
    # 下载
    download_language_audio_by_youdao(audio_out_dir,article_full,se_id=1)

def dealwith_article_into_local_audio(article_obj):
    article_obj = split_article(article_obj)
    file_full_name = article_obj['file_full_name']
    article_title: str = article_obj['article_title']
    # article_content: str = article_obj['article_content']
    article_sentences = article_obj['article_content_list']

    # 逐句翻译，并把翻译信息存入本地文本
    download_sentences_into_local_audio(article_title, article_sentences, file_full_name)

def download_sentences_into_local_audio(article_title, article_sentences, file_full_name):
    text_file_name = file_full_name.replace('.txt','')
    audio_out_dir = f"{sentences_audio_dir}/{text_file_name}"
    if not os.path.exists(audio_out_dir):
        os.makedirs(audio_out_dir)
    else:
        del_files(audio_out_dir)
    se_id = 1 # 一篇文章输出的语句音频放置在对应名称的文件夹下，为了方便识别，就用序号标记，对应好第n句
    sentence_audio_path_list = []
    # 标题下载
    title_sentence_audio_path = download_language_audio_by_youdao(audio_out_dir,article_title,se_id=se_id)
    se_id += 1
    sentence_audio_path_list.append(title_sentence_audio_path)
    # 内容逐句下载
    for sen in article_sentences:
        sentence_audio_path = download_language_audio_by_youdao(audio_out_dir,sen,se_id=se_id)
        se_id += 1
        sentence_audio_path_list.append(sentence_audio_path)
    
    # 音频加工
    save_sentence_audio_better_dir = f'{sentences_audio_better_dir}/{text_file_name}'
    if not os.path.exists(save_sentence_audio_better_dir):
        os.makedirs(save_sentence_audio_better_dir)
    else:
        del_files(save_sentence_audio_better_dir)
    # 给音频文件进行一定的加工，在头部添加一段静音，后续合成视频的时候就不至于出现这种情况：声音比图像先出现（声音应该比图像后出现，这样效果最佳）
    for sap_i,sen_audio_path in enumerate(sentence_audio_path_list):
        # 这里的原始音频和输出音频完全一样，因为默认会替换原始音频文件，不会造成冲突
        sentence_audio_better_path = f'{save_sentence_audio_better_dir}/{sap_i + 1}.mp3'
        add_silence_headend_for_audio(source_audio_full_path=sen_audio_path,out_audio_full_path=sentence_audio_better_path)

def dealwith_article_translations_into_local_audio(article_obj):
    article_obj = split_article(article_obj)
    file_full_name = article_obj['file_full_name']
    # article_title: str = article_obj['article_title']
    # # article_content: str = article_obj['article_content']
    # article_sentences = article_obj['article_content_list']
    sentences_translations = read_article_translations(file_full_name)

    # 逐句下载
    download_sentences_tranlations_into_local_audio(sentences_translations, file_full_name)

def download_sentences_tranlations_into_local_audio(sentences_translations, file_full_name):
    audio_out_dir = f"{translations_audio_dir}/{file_full_name.replace('.txt', '')}"
    if not os.path.exists(audio_out_dir):
        os.makedirs(audio_out_dir)
    else:
        del_files(audio_out_dir)
    se_id = 1
    # 内容逐句下载
    for sen in sentences_translations:
        download_language_audio_by_youdao(audio_out_dir, sen, se_id=se_id, le='zh')
        se_id += 1

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

# 把原文的文本直接处理成一个视频文件
def dealwith_article_source_to_video(article_obj):
    article_obj = split_article(article_obj)
    file_full_name = article_obj['file_full_name']
    article_title: str = article_obj['article_title']
    article_content: str = article_obj['article_content']

    # 把文本处理成图片 再处理成视频
    do_article_source_to_img_and_video(file_full_name,article_title,article_content)

def do_article_source_to_img_and_video(file_full_name:str,article_title,article_content):
    txt_file_name = file_full_name.replace('.txt', '')
    # 因为需要把音频与视频进行合成，所以一定需要全文的音频文件
    article_source_full_audio_path = f"{articlefull_audio_dir}/{txt_file_name}/1.mp3"
    if not os.path.exists(article_source_full_audio_path):
        print(f'该文章对应的音频文件不存在，请先生成下面的音频文件：\n{article_source_full_audio_path}')
        return
    # 读取音频文件的时长，下面文本转视频的时长要与此保持一致
    audio_duration = get_duration_from_ffmpeg(article_source_full_audio_path)
    audio_duration_int = int(round(float(audio_duration))) # 四舍五入取整
    print('*****************************************')
    print(f'{article_source_full_audio_path}\n该文章对应的音频文件时长为：{audio_duration}；\n取整后的时长：{audio_duration_int}')
    print('*****************************************')

    text_file_name = file_full_name.replace('.txt','')
    img_size=article_img_size

    # 一行的最大字符数
    line_char_len_max = article_screen_line_char_len_max
    print(f'line_char_len_max = {line_char_len_max}')

    # 处理标题
    article_title_new = eng_content_line_wrap(article_title, line_char_len_max)
    # 处理文章内容
    article_content_new = eng_content_line_wrap(article_content, line_char_len_max)
    # 把处理好的标题和内容进行组合成一个完整的文本
    article_full = f'{article_title_new}\n \n{article_content_new}'
    # 把完整的文本转为图片
    # 英文文本转图片
    img_format = '.png'
    font_line_h = article_font_line_h
    # img_file_name = f'{text_file_name}__{sentence}'
    save_img_path = f"{txt_to_img_dir}/{text_file_name}{img_format}"
    img_txt_margin_top = article_screen_margin_top  # 因为一句的内容不会很多，所以为了让文字能够尽量在图片垂直方向的中间，所以根据图片的高度大约计算一个顶部间距
    ttc_fonts_dir = article_ttc_fonts_dir
    txt_margin_left = article_txt_margin_left
    screen_bg_img_path = f'{screen_bg_image_dir}/{article_screen_bg_image_full_name}'
    txt_eng_font_size = article_font_size
    txt_zh_font_size = article_font_size
    txt_to_img(img_full_path=save_img_path, content=article_full, img_size=img_size, txt_margin_left=txt_margin_left,
               txt_margin_top=img_txt_margin_top, ttc_fonts_dir=ttc_fonts_dir, eng_font_color='#ffffff',
               eng_ttc_file_full_name=eng_ttc_file_full_name, zh_ttc_file_full_name=zh_ttc_file_full_name,
               eng_font_size=txt_eng_font_size, zh_font_size=txt_zh_font_size, font_line_h=font_line_h, bg_img_path=screen_bg_img_path)

    # 因为图片转视频需要足够的图片数量，所以先复制一批图片
    # 后续图片生成视频的需要，把一篇文章对应的图片归类到一个文件夹下
    save_imgs_dir = f"{txt_to_img_dir}/{text_file_name}"
    if not os.path.exists(save_imgs_dir):
        os.makedirs(save_imgs_dir)
    else:
        del_files(save_imgs_dir)
    # 音频多少秒，就复制多少张图片，后面生成视频也就会是多少秒
    fps_unit_img_count = 25 # 1帧所需的图片数量，经实际实验测试，1帧使用的图片多一些，最终形成的播放时越细腻
    # 这个数量可控制视频和音频的轨道对齐情况（这里太多了会导致视频太长，最后合成视频时会发生声音先于视频，反之则视频画面已经切换下一个了，音频过了很久才开始，导致偏差过大）
    audio_need_img_count = (audio_duration_int+1)*fps_unit_img_count
    for i in range(audio_need_img_count):
        save_copy_img_path = f"{save_imgs_dir}/{text_file_name}_{i}{img_format}"
        shutil.copy(save_img_path,save_copy_img_path)

    # 图片转视频
    save_videos_dir = f"{img_to_video_dir}/{text_file_name}"
    if not os.path.exists(save_videos_dir):
        os.makedirs(save_videos_dir)
    else:
        del_files(save_videos_dir)
    save_video_tmp_path = f'{save_videos_dir}/{text_file_name}_txt.mp4'
    img_to_video(save_imgs_dir, save_videos_dir, save_video_tmp_path, text_file_name,
                 fps=fps_unit_img_count, duration=audio_duration_int, img_format=img_format, video_size=img_size)

    # 把音频和图片生成的视频两个文件合并成一个视频
    save_full_video_path = f'{save_videos_dir}/{text_file_name}.mp4'
    combine_audio_video_by_ffmpeg(source_audio_path=article_source_full_audio_path,source_video_path=save_video_tmp_path,out_video_path=save_full_video_path)
    # 操作完成后，把临时使用的视频文件删除
    os.remove(save_video_tmp_path)

# 英文句子根据图片尺寸自动换行
def eng_content_line_wrap(sentence:str,line_char_len_max):
    screen_len_max = line_char_len_max # 一行最多显示 N 个英文字符
    sentence_len = len(sentence)
    # 若超出最大显示字符，则进行换行处理
    if sentence_len > screen_len_max:
        new_sentence = ''
        words = sentence.split(' ')
        len_val = 0
        for w_i,w in enumerate(words):
            len_val += len(w) + 1
            if len_val > screen_len_max:
                new_sentence = f'{new_sentence}\n{w}'
                len_val = 0
            else:
                new_sentence = w if w_i == 0 else f'{new_sentence} {w}'
        return new_sentence
    return sentence

# 对中文句子进行屏幕适配（一行文字太长会无法显示全面，如果文字太长，则进行换行处理）
def zh_content_line_wrap(sentence:str,line_char_len_max):
    screen_byte_len_max = line_char_len_max # 一行最多显示N个字节（中文翻译中不一定全是中文，会混合着数字和英文，所以需要通过字节数来进行精确判定）
    sentence_byte_count = 0
    for w in sentence:
        try:
            sentence_byte_count += len(w.encode('gbk'))
        except Exception as ex:
            sentence_byte_count += 1
    # 若超出最大显示字节数，则进行换行处理
    if sentence_byte_count > screen_byte_len_max:
        w_i_end = len(sentence) - 1
        new_sentence = ''
        byte_len_val = 0
        eng_word_tmp = '' # 用于记录一个完整的英语单词的临时变量，每次使用完成之后需被清空
        for w_i,w in enumerate(sentence):
            byte_len = 0
            try:
                byte_len = len(w.encode('gbk'))
            except Exception as ex:
                byte_len = 1
            byte_len_val += byte_len
            if byte_len == 2:
                eng_word_tmp = ''
                # 中文字符（占2个字节）
                if byte_len_val > screen_byte_len_max:
                    new_sentence = f'{new_sentence}\n{w}'
                    byte_len_val = 0
                else:
                    new_sentence = w if w_i == 0 else f'{new_sentence}{w}'
            elif byte_len == 1:
                # 单词累加，直到下一个字符是中文时，才把完整的单词进行追加进字符串中，通过判断是否超出行最大字符数判断单词是否需要换行处理
                eng_word_tmp = f"{eng_word_tmp}{w}"
                # 英文或数字之类的字符（占1个字节）
                # 先判定下一个字符是不是中文
                if w_i < w_i_end:
                    next_w = sentence[w_i+1]
                    next_w_byte = 0
                    try:
                        next_w_byte = len(next_w.encode('gbk'))
                    except Exception as ex:
                        next_w_byte = 1
                    if next_w_byte == 2:
                        # 若下一个字符是中文，则判定当前是否需要换行
                        if byte_len_val > screen_byte_len_max:
                            new_sentence = f'{new_sentence}\n{eng_word_tmp}'
                            byte_len_val = 0
                        else:
                            new_sentence = w if w_i == 0 else f'{new_sentence}{eng_word_tmp}'
                    # elif next_w_byte == 1:
                    #     # 若下一个字符不是中文，则不管继续收集，因为说明当前正在收集的是英文单词或是个整体的数字之类的情况
                    #     new_sentence = w if w_i == 0 else f'{new_sentence}{w}'
                else:
                    new_sentence = f'{new_sentence}{w}'
        return new_sentence
    return sentence

# 把原文的句子和翻译文本直接处理成一个视频文件
def dealwith_article_sentences_tranlations_to_video(article_obj):
    article_obj = split_article(article_obj)
    file_full_name:str = article_obj['file_full_name']
    
    # 读取本地文本中已处理好的句子和翻译，句子和翻译的两个数组是一一对应的
    # 读取本地文本中已处理好的句子
    article_sentences = read_article_sentences(file_full_name)
    if article_sentences == None:
        return
    # 读取本地文本中已处理好的翻译
    article_translations = read_article_translations(file_full_name)
    if article_translations == None:
        return    
    # 把句子和翻译文本处理成图片 再处理成视频
    do_article_sentences_tranlations_to_img_and_video(file_full_name,article_sentences,article_translations)

# 把句子和翻译文本处理成图片 再处理成视频
def do_article_sentences_tranlations_to_img_and_video(file_full_name,article_sentences,article_translations):
    text_file_name = file_full_name.replace('.txt','')
    print(f'[*] - file_full_name = {file_full_name}')
    print(f'[*] - text_file_name = {text_file_name}')
    print(f'\n[*] - article_sentences = {article_sentences}')
    print(f'\n[*] - article_translations = {article_translations}')

    # 一篇文章的对应句子和翻译的合成音频都统一归类到一个文件夹下，便于按照文章进行管理
    save_audio_dir = f'{sentences_translations_audio_dir}/{text_file_name}'
    if not os.path.exists(save_audio_dir):
        os.makedirs(save_audio_dir)
    else:
        del_files(save_audio_dir)

    # 一篇文章的对应句子和翻译的图片都统一归类到一个文件夹下，便于按照文章进行管理
    save_sentence_img_dir = f'{sentences_txt_to_img_dir}/{text_file_name}'
    if not os.path.exists(save_sentence_img_dir):
        os.makedirs(save_sentence_img_dir)
    else:
        del_files(save_sentence_img_dir)

    # 一篇文章的对应句子和翻译的合成视频都统一归类到一个文件夹下，便于按照文章进行管理
    save_sentences_translations_videos_dir = f"{sentences_translations_img_to_video_dir}/{text_file_name}"
    if not os.path.exists(save_sentences_translations_videos_dir):
        os.makedirs(save_sentences_translations_videos_dir)
    else:
        del_files(save_sentences_translations_videos_dir)

    # 逐句制作
    sentence_translation_video_path_list = []
    for sen_i,sen in enumerate(article_sentences):
        trans = article_translations[sen_i]
        # 制作一句的原句和翻译组成的一个图片，再把图片变成视频
        sen_idx = sen_i+1
        sentence_translation_video_path = do_one_sentence_tranlation_to_img_and_video(sentence_img_dir=save_sentence_img_dir, save_audio_dir=save_audio_dir, save_sentences_translations_videos_dir=save_sentences_translations_videos_dir, text_file_name=text_file_name,sentence=sen,translation=trans,sen_idx=sen_idx)
        sentence_translation_video_path_list.append(sentence_translation_video_path)
    
    # 把最后的每一句的合成视频，再组合成一个完整的视频（这个完整视频的文件名与所在文件夹的名称是一致的，便于识别）
    save_sentences_translations_whole_video_path = f"{save_sentences_translations_videos_dir}/{text_file_name}.mp4"
    combine_videos_by_ffmpeg(source_video_path_list=sentence_translation_video_path_list,out_video_path=save_sentences_translations_whole_video_path)
    
# 制作一句的原句和翻译组成的一个图片，再把图片变成视频
def do_one_sentence_tranlation_to_img_and_video(sentence_img_dir:str, save_audio_dir:str, save_sentences_translations_videos_dir:str, text_file_name:str, sentence:str,translation:str,sen_idx):
    sentence = sentence.strip() # 清除两边空格
    translation = translation.strip() # 清除两边空格

    # 图片的尺寸
    img_size=article_img_size
    # 一行的最大字符数
    line_char_len_max = sentence_screen_line_char_len_max

    # 获取英文原句和对应的翻译的音频文件，将二者进行合并
    sentence_audio_path = f'{sentences_audio_better_dir}/{text_file_name}/{sen_idx}.mp3'
    translation_audio_path = f'{translations_audio_dir}/{text_file_name}/{sen_idx}.mp3'
    audio_file_path_list = [
        sentence_audio_path,
        translation_audio_path
    ]    
    save_audio_full_path = f'{save_audio_dir}/{sen_idx}.mp3' # 合成音频文件的绝对路径
    combine_audio_files(audio_file_path_list=audio_file_path_list,out_audio_full_path=save_audio_full_path)
    # 获取最后得到的合成音频的时长
    sen_trans_audio_duration = get_duration_from_ffmpeg(save_audio_full_path)
    sen_trans_audio_duration = int(round((float(sen_trans_audio_duration)))) # 四舍五入取整

    # 想将文本处理成一张图片
    # 英文原句在上，中文翻译在下
    sentence_wrap = eng_content_line_wrap(sentence,line_char_len_max) # 先进行根据图片尺寸自动换行处理
    translation_wrap = zh_content_line_wrap(translation,line_char_len_max) # 先进行根据图片尺寸自动换行处理
    sen_trans_content = f'{sentence_wrap}\n \n{translation_wrap}'
    # sen_trans_content = f'{translation_wrap}'
    print(f'sen_trans_content === {sen_trans_content}')
    # 把完整的文本转为图片
    img_format = '.png'
    font_size = sentence_font_size # 图片上绘制的字体大小，这个与图片尺寸 和 文字换行算法进行结合来计算，因为文字尺寸的大小和图片的尺寸会影响一行可容纳的文字数量
    font_line_h = sentence_font_line_h
    img_file_name = f'{text_file_name}__{sen_idx}'
    save_img_path = f'{sentence_img_dir}/{img_file_name}{img_format}'
    img_txt_margin_left = sentence_screen_margin_left
    img_txt_margin_top = sentence_screen_margin_top # 因为一句的内容不会很多，所以为了让文字能够尽量在图片垂直方向的中间，所以根据图片的高度大约计算一个顶部间距
    ttc_fonts_dir = sentence_ttc_fonts_dir
    screen_bg_img_path = f'{screen_bg_image_dir}/{sentence_screen_bg_image_full_name}'
    txt_eng_ttc_file_full_name = sentence_eng_ttc_file_full_name
    txt_zh_ttc_file_full_name = sentence_zh_ttc_file_full_name
    txt_eng_font_size = sentence_eng_font_size
    txt_zh_font_size = sentence_zh_font_size
    txt_to_img(img_full_path=save_img_path, content=sen_trans_content, img_size=img_size, txt_margin_left=img_txt_margin_left, txt_margin_top=img_txt_margin_top,ttc_fonts_dir=ttc_fonts_dir,eng_ttc_file_full_name=txt_eng_ttc_file_full_name,zh_ttc_file_full_name=txt_zh_ttc_file_full_name,eng_font_size=txt_eng_font_size,zh_font_size=txt_zh_font_size,font_line_h=font_line_h,bg_img_path=screen_bg_img_path)

    # 因为图片转视频需要足够的图片数量，所以先复制一批图片
    # 后续图片生成视频的需要，把一篇文章对应的图片归类到一个文件夹下
    save_imgs_dir = f"{sentence_img_dir}/{text_file_name}__{sen_idx}"
    if not os.path.exists(save_imgs_dir):
        os.makedirs(save_imgs_dir)
    else:
        del_files(save_imgs_dir)
    # 音频多少秒，就复制多少张图片，后面生成视频也就会是多少秒
    fps_unit_img_count = 20 # 1帧所需的图片数量，经实际实验测试，1帧使用的图片越多，最终形成的播放时越细腻
    audio_need_img_count = sen_trans_audio_duration * fps_unit_img_count # 这里多加N张张是为了让视频延长N秒，避免图片数量不足的情况
    for i in range(audio_need_img_count):
        save_copy_img_path = f"{save_imgs_dir}/{text_file_name}_{i}{img_format}"
        shutil.copy(save_img_path,save_copy_img_path)
    
    # 图片转视频
    save_sentence_translation_video_path = f'{save_sentences_translations_videos_dir}/{sen_idx}_txt.mp4'
    img_to_video(save_imgs_dir, save_sentences_translations_videos_dir, save_sentence_translation_video_path, text_file_name,
                 fps=fps_unit_img_count, duration=sen_trans_audio_duration, img_format=img_format, video_size=img_size)

    # 把音频和图片生成的视频两个文件合并成一个视频
    save_full_video_path = f'{save_sentences_translations_videos_dir}/{sen_idx}.mp4'
    combine_audio_video_by_ffmpeg(source_audio_path=save_audio_full_path,source_video_path=save_sentence_translation_video_path,out_video_path=save_full_video_path)
    # 操作完成后，把临时使用的视频文件删除
    os.remove(save_sentence_translation_video_path)
    # 把最终合成的视频的绝对路径返回出去
    return save_full_video_path

# ********************************* 下载单词和翻译音频，以及把单词和翻译文本转成图片，再合成视频 ********************************************
# 下载原文中抽取的单词和翻译的音频文件
def dealwith_download_article_words_tranlations_audio(article_obj):
    article_obj = split_article(article_obj)
    file_full_name:str = article_obj['file_full_name']
    
    # 读取本地文本中已处理好单词和翻译
    article_word_translation_list = read_word_transinfo_from_txt(file_full_name)
    if article_word_translation_list == None:
        return
    word_list = article_word_translation_list['word_list']
    word_transinfo_list = article_word_translation_list['word_transinfo_list']
    # 下载原文中抽取的单词和翻译的音频文件
    do_download_article_words_tranlations_audio(file_full_name,word_list,word_transinfo_list)

# 下载原文中抽取的单词和翻译的音频文件
def do_download_article_words_tranlations_audio(file_full_name:str,word_list,word_transinfo_list):
    text_file_name = file_full_name.replace('.txt','')
    # 下载英语单词音频文件
    download_word_audio_files_to_local(text_file_name,word_list)
    
    # 下载单词翻译音频文件
    download_translation_audio_files_to_local(text_file_name,word_transinfo_list)
    
# 下载英语单词音频文件
def download_word_audio_files_to_local(text_file_name:str,word_list:list[str]):
    # 下载英语单词音频文件
    # 一篇文章的档次音频都归类到一个文件下进行管理
    save_words_audio_dir = f'{words_audio_dir}/{text_file_name}'
    if not os.path.exists(save_words_audio_dir):
        os.makedirs(save_words_audio_dir)
    else:
        del_files(save_words_audio_dir)
    word_audio_path_list = []
    for w in word_list:
        # 下载一个单词的音频文件，这里的音频文件直接以单词命名即可(单词长度不会太长，而且可以作为文件名。这里也已确保单词唯一性)
         word_audio_path = download_one_word_audio(save_words_audio_dir,word=w)
         word_audio_path_list.append(word_audio_path)
    
    # 单词音频加工
    do_words_audio_better(text_file_name,word_audio_path_list,word_list)

# 单词音频加工
def do_words_audio_better(text_file_name:str,word_audio_path_list:list[str],word_list:list[str]):
    # 单词音频加工
    save_word_audio_better_dir = f'{words_audio_better_dir}/{text_file_name}'
    if not os.path.exists(save_word_audio_better_dir):
        os.makedirs(save_word_audio_better_dir)
    else:
        del_files(save_word_audio_better_dir)
    # 给音频文件进行一定的加工，在头部添加一段静音，后续合成视频的时候就不至于出现这种情况：声音比图像先出现（声音应该比图像后出现，这样效果最佳）
    fail_better_word_audios = [] # 实际测试中发现有写单词音频不知何原因会加工失败，目前遇到这样的单词就直接把原单词音频复制过去，并提示使用者，暂无其他方案 
    fail_better_words = []
    for wap_i,w_audio_path in enumerate(word_audio_path_list):
        # 这里的原始音频和输出音频完全一样，因为默认会替换原始音频文件，不会造成冲突
        word = word_list[wap_i]
        word_audio_better_path = f'{save_word_audio_better_dir}/{word}.mp3'
        try:
            add_silence_headend_for_audio(source_audio_full_path=w_audio_path,out_audio_full_path=word_audio_better_path)
        except Exception as ex:
            fail_better_word_audios.append(w_audio_path)
            fail_better_words.append(word)
    if len(fail_better_word_audios) > 0:
        print(f'以下单词音频加工处理无效:\n{fail_better_word_audios}')
        fail_remember_path = write_fail_better_audio_words_into_txt(text_file_name,fail_better_words)
        print(f'这些加工失败的单词音频已记录到文档中，后续操作中将会排除这些单词音频：\n{fail_remember_path}')
        # for fail_word in fail_better_words:
        #     fail_word_audio_path = f'{words_audio_dir}/{text_file_name}/{fail_word}.mp3'
        #     word_audio_better_path = f'{save_word_audio_better_dir}/{fail_word}.mp3'
        #     shutil.copy(src=fail_word_audio_path,dst=word_audio_better_path)

# 把音频加工失败的单词记录到文档中
def write_fail_better_audio_words_into_txt(text_file_name,words:list[str]):
    # save_words_fail_remember_dir = f'{words_fail_remember_dir}/{text_file_name}'
    # if not os.path.exists(save_words_fail_remember_dir):
    #     os.makedirs(save_words_fail_remember_dir)
    # else:
    #     del_files(save_words_fail_remember_dir)
    content = ''
    for w_i,w in enumerate(words):
        content = w if w_i == 0 else f'{content}\n{w}'
    fpath = f'{words_fail_remember_dir}/{text_file_name}.txt'
    if os.path.exists(fpath):
        os.remove(fpath)
    fp = open(fpath,'w',encoding='utf-8')
    fp.write(content)
    fp.close()
    return fpath

# 读取音频加工失败的单词记录
def read_fail_better_audio_words_from_txt(text_file_name:str):
    fpath = f'{words_fail_remember_dir}/{text_file_name}.txt'
    if not os.path.exists(fpath):
        return []
    words = []
    for line in open(fpath, encoding='utf-8'):
        line = line.replace('\n','').replace('\r','')
        words.append(line)
    return words

# 下载一个单词的音频文件，这里的音频文件直接以单词命名即可(单词长度不会太长，而且可以作为文件名。这里也已确保单词唯一性)
def download_one_word_audio(save_words_audio_dir:str,word:str):
    return download_language_audio_by_youdao(save_words_audio_dir,word,audio_name=word)

# 下载单词翻译音频文件
def download_translation_audio_files_to_local(text_file_name:str,word_transinfo_list:list[str]):
    # 一篇文章的档次音频都归类到一个文件下进行管理
    save_words_translations_audio_dir = f'{words_translations_audio_dir}/{text_file_name}'
    if not os.path.exists(save_words_translations_audio_dir):
        os.makedirs(save_words_translations_audio_dir)
    else:
        del_files(save_words_translations_audio_dir)
    for trans in word_transinfo_list:
        # 下载一个单词的音频文件，这里的音频文件直接以单词命名即可(单词长度不会太长，而且可以作为文件名。这里也已确保单词唯一性)
        trans_list = trans.split('\n')
        w = trans_list[0]
        # trans_content = trans.replace(f'{w}\n','') # 完整的单词翻译中第一行是对应的英文单词，把单词去除剩下的就是纯粹的中文翻译了
        wphone = trans_list[1] # 第二行是发音音标信息
        trans_content = trans.replace(f'{w}\n','').replace(f'{wphone}\n','') # 完整的单词翻译中第一行和第二行是对应的英文单词和发音音标，把单词和音标去除剩下的就是纯粹的中文翻译了
        trans_content = replace_word_post_to_zh(trans_content) # 把单词翻译中的词性符号(n. 之类)替换成中文说明，这样效果更佳
        download_one_word_translation_audio(save_words_translations_audio_dir,word=w,translation=trans_content)

# 把单词翻译中的词性符号(n. 之类)替换成中文说明，这样效果更佳
def replace_word_post_to_zh(trans_content:str):
    w_str = '{0}.--'
    hint_str = '作为[{0}]译为：--'
    trans_content = trans_content.replace(w_str.format('n'),hint_str.format('名词'))
    trans_content = trans_content.replace(w_str.format('adj'),hint_str.format('形容词'))
    trans_content = trans_content.replace(w_str.format('adv'),hint_str.format('副词'))
    trans_content = trans_content.replace(w_str.format('num'),hint_str.format('数词'))
    trans_content = trans_content.replace(w_str.format('art'),hint_str.format('冠词'))
    trans_content = trans_content.replace(w_str.format('prep'),hint_str.format('介词'))
    trans_content = trans_content.replace(w_str.format('conj'),hint_str.format('连词'))
    trans_content = trans_content.replace(w_str.format('interj'),hint_str.format('感叹词'))
    trans_content = trans_content.replace(w_str.format('vi'),hint_str.format('不及物动词'))
    trans_content = trans_content.replace(w_str.format('vt'),hint_str.format('及物动词'))
    trans_content = trans_content.replace(w_str.format('pron'),hint_str.format('代名词'))
    trans_content = trans_content.replace(w_str.format('v'),hint_str.format('动词'))
    trans_content = trans_content.replace(w_str.format('conj'),hint_str.format('连接词'))
    trans_content = trans_content.replace(w_str.format('s'),hint_str.format('主词'))
    trans_content = trans_content.replace(w_str.format('sc'),hint_str.format('主词补语'))
    trans_content = trans_content.replace(w_str.format('o'),hint_str.format('受词'))
    trans_content = trans_content.replace(w_str.format('oc'),hint_str.format('受词补语'))
    trans_content = trans_content.replace(w_str.format('aux.v'),hint_str.format('助动词'))
    trans_content = trans_content.replace(w_str.format('aux'),hint_str.format('助动词'))
    trans_content = trans_content.replace(w_str.format('pl'),hint_str.format('复数'))
    trans_content = trans_content.replace(w_str.format('c'),hint_str.format('可数名词'))
    trans_content = trans_content.replace(w_str.format('u'),hint_str.format('不可数名词'))
    trans_content = trans_content.replace(w_str.format('num'),hint_str.format('数词'))
    trans_content = trans_content.replace(w_str.format('art'),hint_str.format('冠词'))
    trans_content = trans_content.replace(w_str.format('ad'),hint_str.format('副词'))
    trans_content = trans_content.replace(w_str.format('a'),hint_str.format('形容词'))
    # 这里处理以下一些特殊的符号，替换成中文说明效果更佳
    trans_content = trans_content.replace('……','什么什么')
    return trans_content

# 下载一个单词翻译的音频文件，这里的音频文件直接以单词命名即可(单词长度不会太长，而且可以作为文件名。这里也已确保单词唯一性)
def download_one_word_translation_audio(save_words_translations_audio_dir:str,word:str,translation:str):
    print(f'word:')
    print(word)
    print('****')
    print(f'translation:')
    print(translation)
    print("========================")
    return download_language_audio_by_youdao(save_words_translations_audio_dir,translation,audio_name=word,le='zh')

# 将已下载好的单词发音音频和翻译音频合并成一份完整的音频（一个单词对应一个翻译合成一份音频）
def dealwith_combine_article_words_tranlations_audio(article_obj):
    article_obj = split_article(article_obj)
    file_full_name:str = article_obj['file_full_name']
    
    # 读取本地文本中已处理好单词和翻译
    article_word_translation_list = read_word_transinfo_from_txt(file_full_name)
    if article_word_translation_list == None:
        return
    word_list = article_word_translation_list['word_list']
    # 将已下载好的单词发音音频和翻译音频合并成一份完整的音频（一个单词对应一个翻译合成一份音频）
    do_combine_article_words_tranlations_audio(file_full_name,word_list)

# 将已下载好的单词发音音频和翻译音频合并成一份完整的音频（一个单词对应一个翻译合成一份音频）
def do_combine_article_words_tranlations_audio(file_full_name:str,word_list:list[str]):
    text_file_name = file_full_name.strip('.txt')
    # 一篇文章的档次音频都归类到一个文件下进行管理
    save_words_translations_combine_audio_dir = f'{words_translations_combine_audio_dir}/{text_file_name}'
    if not os.path.exists(save_words_translations_combine_audio_dir):
        os.makedirs(save_words_translations_combine_audio_dir)
    else:
        del_files(save_words_translations_combine_audio_dir)
    for w in word_list:
        # 合并一个单词的发音音频和翻译音频
        combine_one_word_translation_audio(text_file_name,save_words_translations_combine_audio_dir,word=w)

# 合并一个单词的发音音频和翻译音频
def combine_one_word_translation_audio(text_file_name:str,save_words_translations_combine_audio_dir:str,word:str):
    word_audio_path = f'{words_audio_better_dir}/{text_file_name}/{word}.mp3'
    translation_audio_path = f'{words_translations_audio_dir}/{text_file_name}/{word}.mp3'
    fail_better_audio_words = read_fail_better_audio_words_from_txt(text_file_name) # 读取那些加工失败的单词音频
    if word in fail_better_audio_words:
        print(f'!!!!!该单词的发音音频属于加工时无法解析的，已进行忽略：\n{word_audio_path}\n')
        return
    # 发音和翻译音频合并
    if not os.path.exists(word_audio_path):
        print(f'!!!!!该单词的发音音频不存在(已忽略)：\n{word_audio_path}\n')
        return
    if not os.path.exists(translation_audio_path):
        print(f'!!!!!该单词的翻译音频不存在(已忽略)：\n{translation_audio_path}\n')
        return
    audio_file_path_list = [word_audio_path,translation_audio_path]
    save_words_translations_combine_audio_path = f'{save_words_translations_combine_audio_dir}/{word}.mp3'
    combine_audio_files(audio_file_path_list,out_audio_full_path=save_words_translations_combine_audio_path,silence_sec=1)

# 把一篇文章中提取的所有单词的发音音频和翻译音频合并并生成完整视频
def dealwith_article_words_tranlations_to_video(article_obj):
    article_obj = split_article(article_obj)
    file_full_name:str = article_obj['file_full_name']
    
    # 读取本地文本中已处理好单词和翻译
    article_word_translation_list = read_word_transinfo_from_txt(file_full_name)
    if article_word_translation_list == None:
        return
    word_list = article_word_translation_list['word_list']
    word_transinfo_list = article_word_translation_list['word_transinfo_list']
    # 把一篇文章中提取的所有单词的发音音频和翻译音频合并并生成完整视频
    do_article_words_tranlations_to_video(file_full_name,word_list,word_transinfo_list)

# 把一篇文章中提取的所有单词的发音音频和翻译音频合并并生成完整视频
def do_article_words_tranlations_to_video(file_full_name:str,word_list:list[str],word_transinfo_list:list[str]):
    text_file_name = file_full_name.replace('.txt','')
    # 一篇文章的档次音频都归类到一个文件下进行管理
    save_words_translations_video_dir = f'{words_translations_video_dir}/{text_file_name}'
    if not os.path.exists(save_words_translations_video_dir):
        os.makedirs(save_words_translations_video_dir)
    else:
        del_files(save_words_translations_video_dir)
    save_full_video_path_list = []
    for trans in word_transinfo_list:
        trans_list = trans.split('\n')
        w = trans_list[0]
        # trans_content = trans.replace(f'{w}\n','') # 完整的单词翻译中第一行是对应的英文单词，把单词去除剩下的就是纯粹的中文翻译了
        wphone = trans_list[1] # 第二行是发音音标信息
        trans_content = trans.replace(f'{w}\n','').replace(f'{wphone}\n','') # 完整的单词翻译中第一行和第二行是对应的英文单词和发音音标，把单词和音标去除剩下的就是纯粹的中文翻译了
        fail_better_audio_words = read_fail_better_audio_words_from_txt(text_file_name) # 读取音频加工失败的单词音频，这里进行排除
        if w in fail_better_audio_words:
            word_audio_path = f'{words_audio_dir}/{text_file_name}/{w}.mp3'
            print(f'!!!!!该单词的发音音频属于加工时无法解析的，已进行忽略：\n{word_audio_path}\n')
            continue
        if w in my_words_lib:
            word_audio_path = f'{words_audio_dir}/{text_file_name}/{w}.mp3'
            print(f'!!!!!该单词存在于我的已知单词表中，已进行忽略：\n{word_audio_path}\n')
            continue
        # 制作一个单词的视频
        save_full_video_path = make_one_word_translation_video(text_file_name,save_words_translations_video_dir,word=w,wphone=wphone,translation=trans_content)
        save_full_video_path_list.append(save_full_video_path)
    
    # 把一篇文章的所有单词翻译视频合成一个完整的视频
    save_words_translations_whole_video_path = f'{words_translations_whole_video_dir}/{text_file_name}.mp4'
    combine_videos_by_ffmpeg(source_video_path_list=save_full_video_path_list, out_video_path=save_words_translations_whole_video_path)

# 制作一个单词的视频
def make_one_word_translation_video(text_file_name:str, save_words_translations_video_dir:str, word:str, wphone:str, translation:str):
    # 图片的尺寸
    img_size=article_img_size
    # 一行的最大字符数
    line_char_len_max = word_screen_line_char_len_max

    # 获取英文单词发音和翻译音频的合成文件
    word_translation_combine_audio_path = f'{words_translations_combine_audio_dir}/{text_file_name}/{word}.mp3'
    # 获取最后得到的合成音频的时长
    word_translation_combine_audio_duration = get_duration_from_ffmpeg(word_translation_combine_audio_path)
    word_translation_combine_audio_duration = int(round(float(word_translation_combine_audio_duration),0)) # 四舍五入取整

    # 想将文本处理成一张图片
    # 英文在上，中文翻译在下
    translation = translation.replace('\n','').replace('\r','')
    translation_wrap = zh_content_line_wrap(translation,line_char_len_max) # 先进行根据图片尺寸自动换行处理
    # 下面的 txt_to_img 函数里因音标字符串比较特殊，所以特定固定渲染在第二行（切记仅适合单词视频布局）
    # 所以为了把音标渲染的位置好看，前面弄个空行
    eng_symbol_txt = f'\n \n{wphone}' # 音标字符串
    word_trans_content = f'{word}\n \n \n \n{translation_wrap}' # 中间弄四个 \n 是为了给上面的音标字符留出合理的空间

    # while not word_trans_content.find('\n\n') == -1:
    #     word_trans_content = word_trans_content.replace('\n\n','\n')
    print(f'word_trans_content === {word_trans_content}')

    # 把完整的文本转为图片
    img_format = '.png'
    txt_eng_font_line_h = word_eng_font_line_h
    txt_zh_font_line_h = word_zh_font_line_h
    img_file_name = f'{text_file_name}__{word}'
    save_img_path = f'{words_translations_img_dir}/{img_file_name}{img_format}'
    img_txt_margin_left = word_img_txt_margin_left
    img_txt_margin_top = word_screen_margin_top # 因为一句的内容不会很多，所以为了让文字能够尽量在图片垂直方向的中间，所以根据图片的高度大约计算一个顶部间距
    ttc_fonts_dir = word_ttc_fonts_dir
    screen_bg_img_path = f'{screen_bg_image_dir}/{word_img_screen_bg_path}'
    txt_eng_font_size = word_eng_font_size
    txt_zh_font_size = word_zh_font_size
    txt_to_img(img_full_path=save_img_path, content=word_trans_content, img_size=img_size, txt_margin_left=img_txt_margin_left, txt_margin_top=img_txt_margin_top,ttc_fonts_dir=ttc_fonts_dir,eng_ttc_file_full_name=eng_ttc_file_full_name,zh_ttc_file_full_name=zh_ttc_file_full_name,eng_font_size=txt_eng_font_size,zh_font_size=txt_zh_font_size,eng_font_line_h=txt_eng_font_line_h,zh_font_line_h=txt_zh_font_line_h,bg_img_path=screen_bg_img_path,eng_symbol_ttc_file_full_name=eng_symbol_ttc_file_full_name,eng_symbol_txt=eng_symbol_txt)

    # 因为图片转视频需要足够的图片数量，所以先复制一批图片
    # 后续图片生成视频的需要，把一篇文章对应的图片归类到一个文件夹下
    save_imgs_dir = f"{words_translations_img_dir}/{img_file_name}"
    if not os.path.exists(save_imgs_dir):
        os.makedirs(save_imgs_dir)
    else:
        del_files(save_imgs_dir)
    # 音频多少秒，就复制多少张图片，后面生成视频也就会是多少秒
    fps_unit_img_count = 25 # 1帧所需的图片数量，经实际实验测试，1帧使用的图片多一些，最终形成的播放时越细腻
    # 这个数量可控制视频和音频的轨道对齐情况（这里太多了会导致视频太长，最后合成视频时会发生声音先于视频，反之则视频画面已经切换下一个单词了，音频过了很久才开始，导致偏差过大）
    audio_need_img_count = (word_translation_combine_audio_duration+1)*fps_unit_img_count # 这里每份多加1张是为了避免图片不够导致时长不足的偏差情况（确保图片数量足够组成当前时长所需的视频）
    for i in range(audio_need_img_count):
        save_copy_img_path = f"{save_imgs_dir}/{text_file_name}_{i}{img_format}"
        shutil.copy(save_img_path,save_copy_img_path)
    
    # 图片转视频
    save_video_tmp_path = f'{save_words_translations_video_dir}/{word}_txt.mp4'
    img_to_video(save_imgs_dir, save_words_translations_video_dir, save_video_tmp_path, text_file_name, fps=fps_unit_img_count,duration=word_translation_combine_audio_duration, img_format=img_format, video_size=img_size)

    # 把音频和图片生成的视频两个文件合并成一个视频
    save_full_video_path = f'{save_words_translations_video_dir}/{word}.mp4'
    combine_audio_video_by_ffmpeg(source_audio_path=word_translation_combine_audio_path,source_video_path=save_video_tmp_path,out_video_path=save_full_video_path)
    # 操作完成后，把临时使用的视频文件删除
    os.remove(save_video_tmp_path)
    # 把最终合成的视频的绝对路径返回出去
    return save_full_video_path

def dealwith_article_words_audio_better(article_obj):
    article_obj = split_article(article_obj)
    file_full_name:str = article_obj['file_full_name']
    text_file_name = file_full_name.replace('.txt','')

    # 读取本地文本中已处理好单词和翻译
    article_word_translation_list = read_word_transinfo_from_txt(file_full_name)
    if article_word_translation_list == None:
        return
    word_list = article_word_translation_list['word_list']
    # 整理收集要优化的单词音频文件
    # 先检查一遍单词音频是否都存在
    lose_word_audios = []
    for w in word_list:
        source_word_audio_path = f'{words_audio_dir}/{text_file_name}/{w}.mp3'
        if not os.path.exists(source_word_audio_path):
            lose_word_audios.append(source_word_audio_path)
    if len(lose_word_audios) > 0:
        print(f'!!!!!!!处理失败！！！！，当前文章【{file_full_name}】的单词音频不完整，以下单词视频不存在:\n{lose_word_audios}')
        return
    word_audio_path_list = []
    for w in word_list:
        source_word_audio_path = f'{words_audio_dir}/{text_file_name}/{w}.mp3'
        word_audio_path_list.append(source_word_audio_path)
    # 将单词音频进行优化处理
    do_words_audio_better(text_file_name,word_audio_path_list,word_list)

def dealwith_combine_whole_words_video_to_one_video():
    if not os.path.exists(need_combine_words_whole_videos_dir):
        print(f'合并时要选用的目录不存在：\n{need_combine_words_whole_videos_dir}')
        print('请先至少生成一份完整的单词视频，然后再在 config_words_video_combine_data.py 脚本中配置相应的参数')
        print('-------------------------------------------------')
        return
    # 整理收集要合并的单词视频
    lose_video_path_list = []
    can_combine_video_path_list = []
    for word_video_file_name in need_combine_words_whole_videos:
        word_video_path = f'{need_combine_words_whole_videos_dir}/{word_video_file_name}.mp4'
        if not os.path.exists(word_video_path):
            lose_video_path_list.append(word_video_path)
        else:
            can_combine_video_path_list.append(word_video_path)
    if len(lose_video_path_list) > 0:
        print(f'以下单词视频不存在，以进行排除：\n{lose_video_path_list}')
    if len(can_combine_video_path_list) < 2:
        print(f'只有1份单词视频，请至少确保2份单词视频进行合并：\n{can_combine_video_path_list}')
        return
    
    # 合并视频
    combine_words_video_file_name_new = combine_words_video_file_name
    if not os.path.exists(combine_words_whole_videos_dir):
        os.makedirs(combine_words_whole_videos_dir)
    save_combine_video_path = f'{combine_words_whole_videos_dir}/{combine_words_video_file_name_new}.mp4'
    if os.path.exists(save_combine_video_path):
        print(f'\n-------------------------------------------\n')
        print(f'{save_combine_video_path}')
        user_input_val = input(f'同名文件已存在，是否直接替换到原文件(Y/n):')
        user_input_val = 'Y' if user_input_val == '' else user_input_val.upper()
        if user_input_val == 'N':
            # 若不替换，则继续询问要更改的文件名
            combine_words_video_file_name_new = input(f'请输入新的文件名:')
            if combine_words_video_file_name_new == '':
                print('！！！！视频合并失败！！！输入的文件名不能为空')
                return
            save_combine_video_path = f'{combine_words_whole_videos_dir}/{combine_words_video_file_name_new}.mp4'
        print(f'\n-------------------------------------------\n')
    combine_videos_by_ffmpeg(source_video_path_list=can_combine_video_path_list,out_video_path=save_combine_video_path)

# 合并“原文跟读”和的“逐句翻译跟读”视频
def dealwith_combine_article_and_sentences_read_video(article_obj):
    article_obj = split_article(article_obj)
    file_full_name:str = article_obj['file_full_name']
    text_file_name:str = file_full_name.replace('.txt','')
    
    # 合并
    # 原文跟读视频
    article_video_path = f'{img_to_video_dir}/{text_file_name}/{text_file_name}.mp4'
    if not os.path.exists(article_video_path):
        print('**************************************************************')
        print(f'\n{article_video_path}\n!!!!!!!原文跟读视频不存在，请生成原文跟读视频\n')
        print('**************************************************************')
        return
    # 逐句跟读视频
    sentences_video_path = f"{sentences_translations_img_to_video_dir}/{text_file_name}/{text_file_name}.mp4"
    if not os.path.exists(sentences_video_path):
        print('**************************************************************')
        print(f'\n{sentences_video_path}\n!!!!!!!逐句跟读视频不存在，请生成逐句跟读视频\n')
        print('**************************************************************')
        return
    combine_video_list = [article_video_path,sentences_video_path]
    # 合并视频
    save_article_and_sentences_read_video_path = f'{article_and_sentences_read_video_dir}/{text_file_name}.mp4'
    combine_videos_by_ffmpeg(source_video_path_list=combine_video_list,out_video_path=save_article_and_sentences_read_video_path)
    print(f'合并完成，输出文件为：\n{save_article_and_sentences_read_video_path}')
    

# -----------------------------------------------------------------------------------------------
# 以下是一些提供给外界调用的入口函数
# -----------------------------------------------------------------------------------------------

# 对原文进行翻译到本地
def translate_article_into_txt(selction_hint,selected_selection=None):
    article_obj = ask_select_article_source(selected_selection)    
    # 把此次操作的文件记录到本地
    file_full_name = article_obj['file_full_name']
    remember_option_into_article_txt(file_full_name,selction_hint)
    if article_obj == None:
        return
    dealwith_article_into_text(article_obj)
    return article_obj['selected_selection'] 

# 直接对原文输出一个完整对音频到本地
def download_article_all_into_local_audio(selction_hint,selected_selection=None):
    article_obj = ask_select_article_source(selected_selection)
    # 把此次操作的文件记录到本地
    file_full_name = article_obj['file_full_name']
    remember_option_into_article_txt(file_full_name,selction_hint)
    if article_obj == None:
        return
    dealwith_article_all_into_local_audio(article_obj)
    return article_obj['selected_selection'] 

# 对原文逐句下载发音音频到本地
def download_article_into_local_audio(selction_hint,selected_selection=None):
    article_obj = ask_select_article_source(selected_selection)
    # 把此次操作的文件记录到本地
    file_full_name = article_obj['file_full_name']
    remember_option_into_article_txt(file_full_name,selction_hint)
    if article_obj == None:
        return
    dealwith_article_into_local_audio(article_obj)
    return article_obj['selected_selection'] 

# 对原文对逐句翻译发音音频下载到本地
def download_article_translations_into_local_audio(selction_hint,selected_selection=None):
    article_obj = ask_select_article_source(selected_selection)
    # 把此次操作的文件记录到本地
    file_full_name = article_obj['file_full_name']
    remember_option_into_article_txt(file_full_name,selction_hint)
    if article_obj == None:
        return
    dealwith_article_translations_into_local_audio(article_obj)
    return article_obj['selected_selection'] 

# 从原文中提取单词并翻译到文本中
def export_words_translations_from_article(selction_hint,selected_selection=None):
    article_obj = ask_select_article_source(selected_selection)
    # 把此次操作的文件记录到本地
    file_full_name = article_obj['file_full_name']
    remember_option_into_article_txt(file_full_name,selction_hint)
    if article_obj == None:
        return
    export_words_translations_from_article_into_txt(article_obj)
    return article_obj['selected_selection'] 

def make_article_source_to_video(selction_hint,selected_selection=None):
    article_obj = ask_select_article_source(selected_selection)
    # 把此次操作的文件记录到本地
    file_full_name = article_obj['file_full_name']
    remember_option_into_article_txt(file_full_name,selction_hint)
    if article_obj == None:
        return
    dealwith_article_source_to_video(article_obj)
    return article_obj['selected_selection'] 

def make_article_sentences_tranlations_to_video(selction_hint,selected_selection=None):
    article_obj = ask_select_article_source(selected_selection)
    # 把此次操作的文件记录到本地
    file_full_name = article_obj['file_full_name']
    remember_option_into_article_txt(file_full_name,selction_hint)
    if article_obj == None:
        return
    dealwith_article_sentences_tranlations_to_video(article_obj)
    return article_obj['selected_selection'] 

def download_article_words_tranlations_audio(selction_hint,selected_selection=None):
    article_obj = ask_select_article_source(selected_selection)
    # 把此次操作的文件记录到本地
    file_full_name = article_obj['file_full_name']
    remember_option_into_article_txt(file_full_name,selction_hint)
    if article_obj == None:
        return
    dealwith_download_article_words_tranlations_audio(article_obj)
    return article_obj['selected_selection'] 

def make_article_words_audio_better(selction_hint,selected_selection=None):
    article_obj = ask_select_article_source(selected_selection)
    # 把此次操作的文件记录到本地
    file_full_name = article_obj['file_full_name']
    remember_option_into_article_txt(file_full_name,selction_hint)
    if article_obj == None:
        return
    dealwith_article_words_audio_better(article_obj)
    return article_obj['selected_selection'] 

def combine_article_words_tranlations_audio(selction_hint,selected_selection=None):
    article_obj = ask_select_article_source(selected_selection)
    # 把此次操作的文件记录到本地
    file_full_name = article_obj['file_full_name']
    remember_option_into_article_txt(file_full_name,selction_hint)
    if article_obj == None:
        return
    dealwith_combine_article_words_tranlations_audio(article_obj)
    return article_obj['selected_selection'] 

def make_article_words_tranlations_to_video(selction_hint,selected_selection=None):
    article_obj = ask_select_article_source(selected_selection)
    # 把此次操作的文件记录到本地
    file_full_name = article_obj['file_full_name']
    remember_option_into_article_txt(file_full_name,selction_hint)
    if article_obj == None:
        return
    dealwith_article_words_tranlations_to_video(article_obj)
    # <清理> -- 移除所有临时图片文件目录
    clear_img_tmp_dirs()
    print('所有临时图片文件目录 -- 清理完成')
    return article_obj['selected_selection'] 

def combine_whole_words_video_to_one_video(selction_hint,selected_selection=None):
    dealwith_combine_whole_words_video_to_one_video()

def combine_article_and_sentences_read_video(selction_hint,selected_selection=None):
    article_obj = ask_select_article_source(selected_selection)
    # 把此次操作的文件记录到本地
    file_full_name = article_obj['file_full_name']
    remember_option_into_article_txt(file_full_name,selction_hint)
    if article_obj == None:
        return
    dealwith_combine_article_and_sentences_read_video(article_obj)
    # <清理> -- 移除所有临时图片文件目录
    clear_img_tmp_dirs()
    print('所有临时图片文件目录 -- 清理完成')
    return article_obj['selected_selection']

def clear_video_audio_all_files(selction_hint,selected_selection=None):
    # <清理> -- 移除所有临时文件目录
    clear_some_tmp_dirs()
    print('清理完成')

# <每日文章阅读视频> -- 必剪app自动发布 -- 发布“原文跟读”和的“逐句翻译跟读”的完整视频'
def pub_article_and_sentences_read_video_by_bijianapp(selction_hint,selected_selection=None):
    article_obj = ask_select_article_source(selected_selection)
    # 把此次操作的文件记录到本地
    file_full_name:str = article_obj['file_full_name']
    file_name:str = file_full_name.replace('.txt','')
    remember_option_into_article_txt(file_full_name,selction_hint)
    if article_obj == None:
        return
    # 发布参数
    upload_title_full = f'[短文跟读][{file_name}]期--我的简陋英语训练'
    upload_dynamic = '鼓励自己，逐步养每日跟读习惯'
    article_source = '资源来自网络和手动抄录'
    instroduction = f'{upload_title_full}--{article_source}'
    pub_params_json = {
        'firth_partition':'知识',
        'second_partition':'校园学习',
        'upload_title': upload_title_full,
        'upload_dynamic':upload_dynamic,
        'instroduction': instroduction,
        'pub_tag_str': '知识分享官', # 活动话题
        'upload_tags': '学习,英语,口语,材料,外刊' # 视频的普通标签
    }
    pub_common_main_func(file_full_name,pub_params_json)

# <每日文章阅读视频> -- 必剪app自动发布 -- 发布“单词学习”的完整视频'
def pub_words_read_video_by_bijianapp(selction_hint,selected_selection=None):
    article_obj = ask_select_article_source(selected_selection)
    # 把此次操作的文件记录到本地
    file_full_name:str = article_obj['file_full_name']
    file_name:str = file_full_name.replace('.txt','')
    remember_option_into_article_txt(file_full_name,selction_hint)
    if article_obj == None:
        return
    # 发布参数
    upload_title_full = f'[单词摘录][{file_name}]期--我的简陋英语训练'
    upload_dynamic = '坚持坚持,用简陋的视频学单词'
    article_source = '资源来自网络和手动抄录'
    instroduction = f'{upload_title_full}--{article_source}'
    pub_params_json = {
        'firth_partition':'知识',
        'second_partition':'校园学习',
        'upload_title': upload_title_full,
        'upload_dynamic':upload_dynamic,
        'instroduction': instroduction,
        'pub_tag_str': '知识分享官', # 活动话题
        'upload_tags': '学习,英语,口语,单词,词汇量' # 视频的普通标签
    }
    pub_common_main_func(file_full_name,pub_params_json)
    
import importlib,os
from .common.common_util import is_int_str
from .eng_study_daily_read import init_dir,translate_article_into_txt, download_article_all_into_local_audio,download_article_into_local_audio,\
download_article_translations_into_local_audio,download_article_words_tranlations_audio,make_article_words_audio_better,combine_article_words_tranlations_audio,\
make_article_words_tranlations_to_video,combine_whole_words_video_to_one_video,export_words_translations_from_article,\
make_article_source_to_video,make_article_sentences_tranlations_to_video,combine_article_and_sentences_read_video,pub_article_and_sentences_read_video_by_bijianapp,\
pub_words_read_video_by_bijianapp,clear_video_audio_all_files
from .e_book_read import main_func as auto_e_book_main_func

''' 提供给外界调用的主入口函数 '''
def main_func():
  init_dir()
  # ----------------------------- 选择要执行的功能 ----------------------------------
  print('\n----------------------------- 选择要执行的功能 ----------------------------------\n')
  hint_options_init = [
    '[{0}] - <每日文章阅读视频> -- 【语句】：把原文逐句翻译到本地文本',
    '[{0}] - <每日文章阅读视频> -- 【单词】：原文中提取单词并翻译，输出到文本中',
    '[{0}] - <每日文章阅读视频> -- 【文章】：下载原文的完整音频输出到本地',
    '[{0}] - <每日文章阅读视频> -- 【语句】：逐句下载原文的音频输出到本地',
    '[{0}] - <每日文章阅读视频> -- 【语句】：逐句下载原文的翻译音频输出到本地',
    '[{0}] - <每日文章阅读视频> -- 【单词】：下载原文中抽取的单词和翻译的音频到本地',
    '[{0}] - <每日文章阅读视频> -- 【单词】：对已下载的单词英语发音音频进行加工处理（前面加上一段静音）',
    '[{0}] - <每日文章阅读视频> -- 【单词】：逐个把单词的发音音频和翻译发音音频合并成完整音频（一个单词对应一个翻译合成一份音频）',
    '[{0}] - <每日文章阅读视频> -- 【完整视频-单词】：把一篇文章中提取的所有单词的发音音频和翻译音频合并并生成完整视频',
    '[{0}] - <每日文章阅读视频> -- 【*】：对指定的完整单词视频进行再次合并（请先在 config_words_video_combine_data.py 中配置好相关参数）',
    '[{0}] - <每日文章阅读视频> -- 【文章视频】：把原文文本转化成视频文件',
    '[{0}] - <每日文章阅读视频> -- 【语句视频】：把原文的逐句翻译文本转化成视频文件',
    '[{0}] - <每日文章阅读视频> --【完整视频】： 合并“原文跟读”和的“逐句翻译跟读”视频',
    '[{0}] - <每日文章阅读视频> -- 一条龙服务之 -- 自动生成“原文跟读”和的“逐句翻译跟读”的完整视频',
    '[{0}] - <每日文章阅读视频> -- 一条龙服务之 -- 完整单词视频制作，自动从一篇文章中提取单词并制作成单词学习视频',
    '[{0}] - <每日文章阅读视频> -- 【发布】：必剪app自动发布 -- 发布“原文跟读”和的“逐句翻译跟读”的完整视频',
    '[{0}] - <每日文章阅读视频> -- 【发布】：必剪app自动发布 -- 发布“单词学习”的完整视频',
    '[{0}] - <电子书视频> -- 自动生成电子书读物',
    '[{0}] - <清理> -- 移除所有临时文件目录'
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

  # 函数放到一个集合中，根据上面的选项索引进行调用相应的功能函数
  function_list = [
    # <每日文章阅读视频> -- 【语句】：把原文逐句翻译到本地文本
    translate_article_into_txt,
    # <每日文章阅读视频> -- 【单词】：原文中提取单词并翻译，输出到文本中
    export_words_translations_from_article,
    # <每日文章阅读视频> -- 【文章】：下载原文的完整音频输出到本地
    download_article_all_into_local_audio,
    # <每日文章阅读视频> -- 【语句】：逐句下载原文的音频输出到本地
    download_article_into_local_audio,
    # <每日文章阅读视频> -- 【语句】：逐句下载原文的翻译音频输出到本地
    download_article_translations_into_local_audio,
    # <每日文章阅读视频> -- 【单词】：下载原文中抽取的单词和翻译的音频到本地
    download_article_words_tranlations_audio,
    # <每日文章阅读视频> -- 【单词】：对已下载的单词英语发音音频进行加工处理（前面加上一段静音）
    make_article_words_audio_better,
    # <每日文章阅读视频> -- 【单词】：逐个把单词的发音音频和翻译发音音频合并成完整音频（一个单词对应一个翻译合成一份音频）
    combine_article_words_tranlations_audio,
    # <每日文章阅读视频> -- 【完整视频-单词】：把一篇文章中提取的所有单词的发音音频和翻译音频合并并生成完整视频
    make_article_words_tranlations_to_video,
    # <每日文章阅读视频> -- 【*】：对指定的完整单词视频进行再次合并（请先在 config_words_video_combine_data.py 中配置好相关参数）
    combine_whole_words_video_to_one_video,
    # <每日文章阅读视频> -- 把原文文本转化成视频文件
    make_article_source_to_video,
    # <每日文章阅读视频> -- 把原文的逐句翻译文本转化成视频文件
    make_article_sentences_tranlations_to_video,
    # <每日文章阅读视频> -- 合并“原文跟读”和的“逐句翻译跟读”视频
    combine_article_and_sentences_read_video,
    # <每日文章阅读视频> -- 一条龙服务之 -- 自动生成“原文跟读”和的“逐句翻译跟读”的完整视频
    auto_operations_for_article_sentences_video,
    # <每日文章阅读视频> -- 一条龙服务之 -- 完整单词视频制作，自动从一篇文章中提取单词并制作成单词学习视频
    auto_operations_for_words_video,
    # <每日文章阅读视频> -- 必剪app自动发布 -- 发布“原文跟读”和的“逐句翻译跟读”的完整视频'
    pub_article_and_sentences_read_video_by_bijianapp,
    # <每日文章阅读视频> -- 必剪app自动发布 -- 发布“单词学习”的完整视频'
    pub_words_read_video_by_bijianapp,
    # <电子书视频> -- 自动生成电子书读物
    auto_e_book_main_func,
    # <清理> -- 移除所有临时文件目录
    clear_video_audio_all_files
  ]
  function_list[user_selected_idx](selected_selection)

# 一条龙服务之 -- 自动生成“原文跟读”和的“逐句翻译跟读”的完整视频
def auto_operations_for_article_sentences_video(selected_selection):
  function_list = [
    # -------------------- 生成逐句跟读带翻译的视频前的准备 ------------------
    # <每日文章阅读视频> -- 【翻译】：把原文逐句翻译到本地文本
    translate_article_into_txt,
    # <每日文章阅读视频> -- 【翻译】：原文中提取单词并翻译，输出到文本中
    export_words_translations_from_article,
    # <每日文章阅读视频> -- 【翻译】：下载原文的完整音频输出到本地
    download_article_all_into_local_audio,
    # <每日文章阅读视频> -- 【翻译】：逐句下载原文的音频输出到本地
    download_article_into_local_audio,
    # <每日文章阅读视频> -- 【翻译】：逐句下载原文的翻译音频输出到本地
    download_article_translations_into_local_audio,
    # ----------------------------------------------------------------------
    # <每日文章阅读视频> -- 把原文文本转化成视频文件
    make_article_source_to_video,
    # <每日文章阅读视频> -- 把原文的逐句翻译文本转化成视频文件
    make_article_sentences_tranlations_to_video,
    # <每日文章阅读视频> -- 合并“原文跟读”和的“逐句翻译跟读”视频
    combine_article_and_sentences_read_video
  ]
  selected_selection = None
  for func_i,func in enumerate(function_list):
    if func_i == 0:
      # 记录下第一次选择的文档，接下来的步骤都自动使用该记录值
      selected_selection = func(selected_selection)
    else:
      func(selected_selection,selected_selection)

# 一条龙服务之 -- 完整单词视频制作，自动从一篇文章中提取单词并制作成单词学习视频
def auto_operations_for_words_video(selction_hint):
  function_list = [
    # <单词学习视频生成器> -- 【**】：原文中提取单词并翻译，输出到文本中
    export_words_translations_from_article,
    # <单词学习视频生成器> -- 【**】：下载原文中抽取的单词和翻译的音频到本地，并进行优化处理（每个英文单词发音音频前面加上一段静音，避免合成视频时读音先于画面的问题）
    download_article_words_tranlations_audio,
    # # <单词学习视频生成器> -- 【**】：【这个功能仅用于测试，已集成在上面的步骤里了】对已下载的单词英语发音音频进行加工处理（前面加上一段静音）
    # make_article_words_audio_better,
    # <单词学习视频生成器> -- 【**】：逐个把单词的发音音频和翻译发音音频合并成完整音频（一个单词对应一个翻译合成一份音频）
    combine_article_words_tranlations_audio,
    # <单词学习视频生成器> -- 【**】：把一篇文章中提取的所有单词的发音音频和翻译音频合并并生成完整视频
    make_article_words_tranlations_to_video,
  ]
  selected_selection = None
  for func_i,func in enumerate(function_list):
    if func_i == 0:
      # 记录下第一次选择的文档，接下来的步骤都自动使用该记录值
      selected_selection = func(selction_hint)
    else:
      func(selction_hint,selected_selection)
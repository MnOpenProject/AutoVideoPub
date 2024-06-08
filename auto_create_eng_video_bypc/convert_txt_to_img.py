''' 文本转化成图片 '''
# -*- coding: utf-8 -*-

import os
from PIL import Image, ImageFont, ImageDraw

def is_chinese_char(uchar):
    """判断一个unicode是否是汉字"""
    if u'\u4e00' <= uchar <= u'\u9fa5':
        return True
    else:
        return False

def contain_chinese_char(content:str):
    '''判断一个字符串中是否存在中文字符'''
    for c in content:
        if is_chinese_char(c):
            return True
    return False

# 使用Python脚本将文字转换为图片的实例分享
def txt_to_img(img_full_path:str,content='',img_size=(800,600),img_bg_color=(115,143,190),eng_font_color='#f0932b',zh_font_color='#ffffff',txt_margin_top=40,txt_margin_left=30,ttc_fonts_dir='/fonts',eng_ttc_file_full_name='simsun.ttc',zh_ttc_file_full_name='simsun.ttc',eng_font_size=18,zh_font_size=18,font_line_h=28,bg_img_path=None,eng_font_line_h=None,zh_font_line_h=None,eng_symbol_ttc_file_full_name=None,eng_symbol_txt=None):
    # params content: 要打印在图片上的文本内容字符串，如果想连续换行，请一定要这样写 "\n \n" 不要写成 "\n\n" ，目前的换行实现方案多换行只能是 "\n \n"
    # params img_size: 图片尺寸(宽，高)
    # params img_bg_color: 图片背景颜色
    # params font_bg_color: 文字区域背景颜色
    # params font_color: 文字颜色    
    # params txt_margin_top: 文本的顶部间距
    # params txt_margin_left: 文本的左边间距
    # params eng_symbol_ttc_file_full_name: 音标字符集（eng_symbol_ttc_file_full_name 和 eng_symbol_txt 都不为 None 才会渲染）
    # params eng_symbol_txt: 音标字符串（eng_symbol_ttc_file_full_name 和 eng_symbol_txt 都不为 None 才会渲染）

    # --------------------------------- 成功案例（这样渲染出的文字不会带有文字背景色块） -----------------------------------------------
    # text = u"这是一段测试文本，test 123。"
  
    # im = Image.new("RGB", img_size, img_bg_color)
    # dr = ImageDraw.Draw(im)
    # ttc_file_full_name = eng_ttc_file_full_name if str(text).isalnum() else zh_ttc_file_full_name
    # font = ImageFont.truetype(os.path.join(fonts_dir, ttc_file_full_name), font_size)
    
    # dr.text((10, 5), text, font=font, fill="#00fa00")
    
    # im.show()
    # im.save("t.png")
    # ----------------------------------------------------------------------------------------

    print(f'img_full_path = {img_full_path}')
    if os.path.exists(img_full_path):
        os.remove(img_full_path)
    # text = u"这是一\n段测试文本，\n \ntest\n123。" # 可支持中文
    # text = u"Facebook的一名高管周四在Twitter上发帖称，该公司的Meta平台中心负责监控乌克兰的冲突，并推出了一项功能，以便该国的用户可以锁定自己的社交媒体档案，以确保安全"
    text = content

    # im = Image.new("RGB", img_size, img_bg_color)
    # TODO: 暂时不设置背景图片，因为不知道文字背景色怎么去掉，导致有图片的情况下，文字有背景色不好看
    im = None
    if bg_img_path == None:
        im = Image.new("RGB", img_size, img_bg_color)
    else:
        im = Image.open(bg_img_path)
        im.thumbnail(img_size, Image.ANTIALIAS)
        
    # 根据字符串中的换行符进行拆分，并进行换行渲染
    text_list = text.split('\n')
    
    # 目前的字符集中英文分开使用，仅仅支持行识别，即只要一行上的文字不是纯英文，则一定会使用中文字符集，只有一行上是纯英文的才会使用英文字符集
    for sen_idx,sentence in enumerate(text_list):
        if not eng_symbol_ttc_file_full_name == None and not eng_symbol_txt == None and sen_idx == 1:
            # 音标比较特殊，若要渲染音标，只会放在第二行，而且使用特定的音标字符集和一些特定的参数
            # # 为了能够渲染出音标行里的中文字符，只能逐个字进行渲染，判定若是中文，则使用中文字符集
            # p_x = txt_margin_left
            line_n_list = [c for c in eng_symbol_txt if c == '\n'] # 去除其中有多少个 \n 换行符
            line_n_count = len(line_n_list)
            # 根据其中的换行符数量，组合成适合这里的换行字符串，这里如果有多个换行符，则必须每个换行符之间带有空格，否则会报错无法渲染成功，如 '\n \n \n ... \n \n ...'
            line_n_str = ''
            for l_n in range(line_n_count):
                line_n_str = '\n' if l_n == 0 else f'{line_n_str} \n'
            eng_symbol_txt_ = str(eng_symbol_txt).replace('\n \n','').replace('\n','')
            for eng_symbol_char_i,eng_symbol_char in enumerate(eng_symbol_txt_):
                font_size = zh_font_size - 5
                font_color = zh_font_color
                ttc_file_full_name = eng_symbol_ttc_file_full_name if not contain_chinese_char(eng_symbol_char) else zh_ttc_file_full_name
                font_line_h_ = font_line_h
                if not zh_font_line_h == None:
                    font_line_h_ = zh_font_line_h - 2
                dr = ImageDraw.Draw(im)
                font = ImageFont.truetype(os.path.join(ttc_fonts_dir, ttc_file_full_name), font_size)
                line_h = font_line_h_ # 设定一行文字的高度值，每次换行则 y 轴坐标增加一个单位值即可 （注意，行高跟字体尺寸有关，字体大小会影响行高，字体大了行高也要相应变大
                x_val = txt_margin_left + (eng_symbol_char_i*18) # 文本区域位置坐标，左上角的 x 坐标
                y_val = txt_margin_top + (line_h * sen_idx) # 计算当前文字区域的 y 轴坐标，用于实现文字换行功能
                if contain_chinese_char(eng_symbol_char):
                    x_val = x_val + 3
                    y_val = y_val + 3
                p_x = x_val
                p_y = y_val # 文本区域位置坐标，左上角的 y 坐标
                render_eng_symbol_char = f'{line_n_str}{eng_symbol_char}'
                dr.text((p_x, p_y), render_eng_symbol_char, font=font, fill=font_color)
            # =========================================================================================
            # font_size = zh_font_size - 5
            # font_color = zh_font_color
            # ttc_file_full_name = eng_symbol_ttc_file_full_name
            # font_line_h_ = font_line_h
            # if not zh_font_line_h == None:
            #     font_line_h_ = zh_font_line_h - 2
            # dr = ImageDraw.Draw(im)
            # font = ImageFont.truetype(os.path.join(ttc_fonts_dir, ttc_file_full_name), font_size)
            # line_h = font_line_h_ # 设定一行文字的高度值，每次换行则 y 轴坐标增加一个单位值即可 （注意，行高跟字体尺寸有关，字体大小会影响行高，字体大了行高也要相应变大
            # y_val = txt_margin_top + (line_h * sen_idx) # 计算当前文字区域的 y 轴坐标，用于实现文字换行功能
            # p_x = txt_margin_left # 文本区域位置坐标，左上角的 x 坐标
            # p_y = y_val # 文本区域位置坐标，左上角的 y 坐标
            # dr.text((p_x, p_y), eng_symbol_txt, font=font, fill=font_color)
        else:
            font_size = eng_font_size if not contain_chinese_char(sentence) and len(sentence) > 2 else zh_font_size
            font_color = eng_font_color if not contain_chinese_char(sentence) and len(sentence) > 2 else zh_font_color
            ttc_file_full_name = eng_ttc_file_full_name if not contain_chinese_char(sentence) and len(sentence) > 2 else zh_ttc_file_full_name
            font_line_h_ = font_line_h
            if not eng_font_line_h == None and not zh_font_line_h == None:
                font_line_h_ = eng_font_line_h if not contain_chinese_char(sentence) and len(sentence) > 2 else zh_font_line_h
            dr = ImageDraw.Draw(im)
            font = ImageFont.truetype(os.path.join(ttc_fonts_dir, ttc_file_full_name), font_size)
            line_h = font_line_h_ # 设定一行文字的高度值，每次换行则 y 轴坐标增加一个单位值即可 （注意，行高跟字体尺寸有关，字体大小会影响行高，字体大了行高也要相应变大
            y_val = txt_margin_top + (line_h * sen_idx) # 计算当前文字区域的 y 轴坐标，用于实现文字换行功能
            p_x = txt_margin_left # 文本区域位置坐标，左上角的 x 坐标
            p_y = y_val # 文本区域位置坐标，左上角的 y 坐标
            dr.text((p_x, p_y), sentence, font=font, fill=font_color)
    # im.show()
    im.save(img_full_path)
    # line.close()

# ------------ 这套方案保留在这里进行，已暂时废弃，因为绘制出来的文字区域有背景色，且各种尝试和查询资料都无法去除或设为透明 start -------------------------------------------

# from io import BytesIO
# # pip install pygame 
# import pygame
# # 使用Python脚本将文字转换为图片的实例分享
# def txt_to_img(img_full_path:str,content='',img_size=(800,600),img_bg_color=(115,143,190),font_bg_color=(115,143,190),font_color=(255,255,255),txt_margin_top=40,txt_margin_left=30,ttc_fonts_dir='/fonts',eng_ttc_file_full_name='simsun.ttc',zh_ttc_file_full_name='simsun.ttc',font_size=18,font_line_h=28,bg_img_path=None):
#     # params content: 要打印在图片上的文本内容字符串，如果想连续换行，请一定要这样写 "\n \n" 不要写成 "\n\n" ，目前的换行实现方案多换行只能是 "\n \n"
#     # params img_size: 图片尺寸(宽，高)
#     # params img_bg_color: 图片背景颜色
#     # params font_bg_color: 文字区域背景颜色
#     # params font_color: 文字颜色    
#     # params txt_margin_top: 文本的顶部间距
#     # params txt_margin_left: 文本的左边间距

#     print(f'img_full_path = {img_full_path}')
#     if os.path.exists(img_full_path):
#         os.remove(img_full_path)
#     pygame.init()
#     # text = u"这是一\n段测试文本，\n \ntest\n123。" # 可支持中文
#     # text = u"Facebook的一名高管周四在Twitter上发帖称，该公司的Meta平台中心负责监控乌克兰的冲突，并推出了一项功能，以便该国的用户可以锁定自己的社交媒体档案，以确保安全"
#     text = content

#     im = Image.new("RGB", img_size, img_bg_color)
#     # TODO: 暂时不设置背景图片，因为不知道文字背景色怎么去掉，导致有图片的情况下，文字有背景色不好看
#     # im = None
#     # if bg_img_path == None:
#     #     im = Image.new("RGBA", img_size, img_bg_color)
#     # else:
#     #     im = Image.open(bg_img_path)
#     # 根据字符串中的换行符进行拆分，并进行换行渲染
#     text_list = text.split('\n')
    
#     # TODO:目前的字符集中英文分开使用，仅仅支持行识别，即只要一行上的文字不是纯英文，则一定会使用中文字符集，只有一行上是纯英文的才会使用英文字符集
#     for sen_idx,sentence in enumerate(text_list):
#         ttc_file_full_name = eng_ttc_file_full_name if str(sentence).isalnum() else zh_ttc_file_full_name
#         font = pygame.font.Font(os.path.join(ttc_fonts_dir, ttc_file_full_name), font_size)
#         rtext = font.render(sentence, True, font_color, font_bg_color) # 渲染一行句子
#         sio = BytesIO()
#         pygame.image.save(rtext, sio)
#         sio.seek(0)
#         line = Image.open(sio)
#         line_h = font_line_h # 设定一行文字的高度值，每次换行则 y 轴坐标增加一个单位值即可 （注意，行高跟字体尺寸有关，字体大小会影响行高，字体大了行高也要相应变大
#         y_val = txt_margin_top + (line_h * sen_idx)
#         im.paste(line, (txt_margin_left, y_val)) # 把这一句粘贴到图片的一行位置，这是实现换行的关键，后面的 y 坐标值递增即可实现换行；第二个参数控制渲染一行字符串的位置坐标 (x,y)
#     # im.show()
#     im.save(img_full_path)
#     # line.close()

# ------------ 这套方案保留在这里进行，已暂时废弃，因为绘制出来的文字区域有背景色，且各种尝试和查询资料都无法去除或设为透明 end -------------------------------------------
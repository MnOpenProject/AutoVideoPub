''' ocr 识别视频字母，并保存到本地文本 '''
# 参考资料：https://zhuanlan.zhihu.com/p/136264493

# opencv是跨平台计算机视觉库，实现了图像处理和计算机视觉方面的很多通用算法
# cv2: 的安装包
# pip install opencv-python （如果只用主模块，使用这个命令安装）
# pip install opencv-contrib-python （如果需要用主模块和contrib模块，使用这个命令安装），推荐安装这个。
import os,pytesseract,cv2,json
from PIL import Image
from .common_config import __CURPATH__,video_transition_prefix,video_source_dir,logs_out_dir
from .common_util import is_int_str,filter_listdir,ask_for_selection,del_files,get_seirals_by_rangestr

# 从视频中逐帧提取图片保存到本地
video_frame_img_dir = f'{__CURPATH__}/video_frame_imgs'
# 提取视频图片的频率，每 10 帧提取一个
tailor_video_frame_frequency = 10
def tailor_video(video_path,video_file_name):
    # params video_path: 视频文件绝对路径
    # params video_file_name: 视频文件名称（去后缀）

    if not os.path.exists(video_frame_img_dir):
        os.makedirs(video_frame_img_dir)
    # 输出图片的绝对路径
    out_dir = f'{video_frame_img_dir}/{video_file_name}'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    times = 0
    frame_frequency = tailor_video_frame_frequency
    print(f'\n------------------ 图片提取开始... ---------------------\n[{out_dir}\n{video_file_name}]\n')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    camera = cv2.VideoCapture(video_path)
    while True:
        times += 1
        res, image = camera.read()
        if not res:
            print('not res , not image')
            break
        if times % frame_frequency == 0:
            out_img_path = f'{out_dir}/{str(times)}.jpg'
            cv2.imwrite(out_img_path, image)  # 输出的图片名，如 10.jpg
    print(f'\n[{out_dir}]\n{video_file_name}\n------------------ 图片提取结束 ---------------------\n')

# 对逐帧拆分出的图片进行二次处理，裁剪出只有字幕的区域
video_frame_caption_img_dir = f'{__CURPATH__}/video_frame_caption_imgs'
# 字幕所在图片的位置区域
# （根据字幕所在图片的位置不同来修改这个参数）控制从一张图片上裁剪出字幕图片的区域位置和尺寸，尺寸大小取决于两坐标之间的距离(差值)，比如 区域高度=y1-y0; 区域宽度=x1-x0
# caption_word_crop_positions={'y0':630,'y1':730,'x0':100,'x1':1200}
def tailor_img_for_caption(video_file_name,cv2_thresh=100,cv2_crop_positions={'y0':630,'y1':730,'x0':100,'x1':1200}):
    print(f'\n------------------ 截取字幕图片开始... ---------------------\n{video_file_name}\n')
    if not os.path.exists(video_frame_caption_img_dir):
        os.makedirs(video_frame_caption_img_dir)
    # 读取输出的图片
    frame_imgs_dir = f'{video_frame_img_dir}/{video_file_name}'
    if not os.path.exists(frame_imgs_dir):
        print(f'!!!意外情况 -- 视频输出的图片目录不存在：\n{frame_imgs_dir}')
        return
    frame_img_list = os.listdir(frame_imgs_dir)
    print(f'frame_img_list: \n {frame_img_list}')
    for frame_img_name in frame_img_list:
        frame_img_path = f'{frame_imgs_dir}/{frame_img_name}'
        # print(f'frame_img_path:\n{frame_img_path}')
        if not os.path.exists(frame_img_path):
            continue
        caption_img_dir = f'{video_frame_caption_img_dir}/{video_file_name}'
        # print(f'caption_img_dir:\n{caption_img_dir}')
        if not os.path.exists(caption_img_dir):
            os.makedirs(caption_img_dir)
        path1 = frame_img_path
        path2 = f'{caption_img_dir}/{frame_img_name}'
        # print(f'path1: \n{path1}')
        # print(f'path2: \n{path2}')
        # 其中 step_size 应该要与视频截取图片的帧率保持一致
        tailor(path1,path2,step_size=tailor_video_frame_frequency,thresh_=cv2_thresh,crop_positions=cv2_crop_positions)
    print(f'\n{video_file_name}\n------------------ 截取字幕图片结束 ---------------------\n')

# 对图片进行截取字幕
def tailor(path1,path2,begin=100,end=1000,step_size=10,thresh_=100,crop_positions={'y0':630,'y1':730,'x0':100,'x1':1200}):
    """
    对视频图片进行截取字幕
    :Args:
     - path1 - 图片的绝对路径
     - path2 - 输出的截图的存放路径(绝对路径)
     - begin,end,step_size - 即 range(start, stop[, step]) 一张图片的处理需要不断循环，这3个参数控制这个循环次数
     - thresh_ - （根据提取的文字颜色不同，二设置不同的值，目前100可提取土黄色rgb(214,167,61)和白色的文字）图片灰度处理时，这是个图片颜色的界值，凡是小于该数值的会被一律处理成这个 thresh_ 颜色值，凡是大于该值的都会被处理成代码里设置的  cv2.threshold(imgray, thresh, 255, cv2.THRESH_BINARY) 即这句代码里的 255
     - crop_positions - （根据字幕所在图片的位置不同来修改这个参数）控制从一张图片上裁剪出字幕图片的区域位置和尺寸，尺寸大小取决于两坐标之间的距离(差值)，比如 区域高度=y1-y0; 区域宽度=x1-x0
    :Usage:
        ::
            path1 = 'D:/video_img/10.jpg'
            path2 = 'D:/out_img/10.jpg'
            tailor(path1,path2,begin=100,end=1000,step_size=10,thresh_=100,crop_positions={'y0':630,'y1':730,'x0':100,'x1':1200})
    """

    for i in range(begin,end,step_size):
        fname1 = path1
        print(fname1)
        img = cv2.imread(fname1)
        print(img.shape)
        y0 = crop_positions['y0']
        y1 = crop_positions['y1']
        x0 = crop_positions['x0']
        x1 = crop_positions['x1']        
        cropped = img[y0:y1, x0:x1]  # img[630:730, 100:1200] 裁剪坐标为[y0:y1, x0:x1]
        # ---------------------------------------------------------------
        imgray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        thresh = thresh_ # 200 # 经测试，若像参考资料的源码一样设置 200 不符合我的图片，得到的图片英文字幕没有了，只有中文了，这只成 100 就可以了
        ret, binary = cv2.threshold(imgray, thresh, 255, cv2.THRESH_BINARY)  # 输入灰度图，输出二值图
        binary1 = cv2.bitwise_not(binary)  # 取反
        cv2.imwrite(path2, binary1)
        # ---------------------------------------------------------------
        # cv2.imwrite(path2, cropped)

# 对 ocr 识别出的英文字幕字符串进行过滤，排除不合规的，去除一些不合理的符号
def filter_captionstr_from_ocr(captionstr:str):
    # 多循环几次，尽量把一些不合理的句子处理掉（目前使用的ocr工具包提取出来的内容会出现很多奇怪的字符，不是非常精确的）
    for i in range(10):
        captionstr = captionstr.replace('\\','').replace('/','').replace('_','').replace(';','').replace('[','').replace(']','').replace('- ','')
        captionstr = captionstr.replace('|','').replace('=','').replace('..','').replace('...','').replace('!','').replace('@','').replace('‘','')
        captionstr = captionstr.replace('~','').replace('>','').replace('©','').replace('»','').replace(';','').replace('（','').replace('）','')
        captionstr = captionstr.replace('¥','').replace('{','').replace('}','').replace('(','').replace(')','').replace(':','').replace('*','')
        captionstr = captionstr.replace('“','').replace('”','').replace('&','').replace('. .','').replace('—','-')
        captionstr = captionstr.replace('’',"'").replace('，',',').replace('  ',' ')

        # 临时用于判定的 替换变量（若替换掉一些比较特殊的字符后，为空，则说明这条字符串也是有问题的）
        captionstr_tmp = captionstr.replace('-','').replace('.','').replace(',','').replace("'",'')
        captionstr_tmp = captionstr_tmp.replace('0','').replace('1','').replace('2','').replace('3','').replace('4','')
        captionstr_tmp = captionstr_tmp.replace('5','').replace('6','').replace('7','').replace('8','').replace('9','')
        if captionstr_tmp.replace(' ','') == '':
            captionstr = captionstr_tmp
        # 若去掉一些特殊符号之后，只剩下一个字符了，这也说明这个句子不合理，设为空即可
        if len(captionstr_tmp.replace(' ','')) < 2:
            captionstr = ''
        captionstr = captionstr.strip() # 去头尾空格
        if len(captionstr) > 0:
            # 若是一些符号开头或结尾，则也进行去除
            first_char = captionstr[0]
            first_char = first_char.replace('-','').replace('.','').replace(',','').replace("'",'')
            first_char = first_char.replace('0','').replace('1','').replace('2','').replace('3','').replace('4','')
            first_char = first_char.replace('5','').replace('6','').replace('7','').replace('8','').replace('9','')
            if first_char == '':
                captionstr = captionstr[1:len(captionstr)]
        if len(captionstr) > 0:
            end_char = captionstr[len(captionstr)-1]
            end_char = end_char.replace('-','').replace(',','').replace("'",'')
            end_char = end_char.replace('0','').replace('1','').replace('2','').replace('3','').replace('4','')
            end_char = end_char.replace('5','').replace('6','').replace('7','').replace('8','').replace('9','')
            if end_char == '':
                captionstr = captionstr[:len(captionstr)-1]
        captionstr = captionstr.strip() # 去头尾空格
        if len(captionstr) < 2:
            captionstr = '' # 若剩余的字符串长度只有1个了，则也设置为空（就一个字母的一定不是合理的句子，就算是 No 也至少2个字母）   
        
    return captionstr

# 为文件的（类似这样的 1.jpg,2.jpg,3.jpg,...,101.jpg,...）进行从小到大排序
def bubble_sort_file(arr):
    n = len(arr)
    # 遍历所有数组元素
    for i in range(n):
        # Last i elements are already in place
        for j in range(0, n-i-1):
            if int(arr[j].replace('.jpg','')) > int(arr[j+1].replace('.jpg','')) :
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# 对字幕截图进行 ocr 提取文字
caption_words_txt_dir = f'{__CURPATH__}/video_caption_words'
def ocr_text_from_caption_imgs(video_file_name):
    print(f'\n------------------ OCR 字幕图片 提取文字 开始... ---------------------\n{video_file_name}\n')
    # 读取输出的图片
    caption_imgs_dir = f'{video_frame_caption_img_dir}/{video_file_name}'
    if not os.path.exists(caption_imgs_dir):
        print(f'!!!意外情况 -- 视频字幕输出的图片目录不存在：\n{caption_imgs_dir}')
        return
    caption_img_list = os.listdir(caption_imgs_dir)
    caption_img_list = bubble_sort_file(caption_img_list)
    print(f'caption_img_list = {caption_img_list}')
    # 收集英文字幕文本
    eng_word_list = []
    for caption_img_name in caption_img_list:
        caption_img_path = f'{caption_imgs_dir}/{caption_img_name}'
        # 图片中识别文字
        text_str = pytesseract.image_to_string(Image.open(caption_img_path),lang="eng")
        text_list = str(text_str).strip().split('\n')
        captionstr = text_list[len(text_list)-1]
        captionstr = filter_captionstr_from_ocr(captionstr) # 过滤掉一些不合理的内容
        eng_word_list.append(captionstr) # 追加的集合中
        # print(text_list)
        # print(f'提取出的英文字幕为：{eng_word}')
        # print('\n**********************************************************\n')
    # 去重
    new_eng_word_list = list(set(eng_word_list)) # 这种去重方式会导致顺序被打乱
    new_eng_word_list.sort(key=eng_word_list.index) # 这一步操作是为了把集合的顺序还原回去
    print(f'此次收集到的所有英文字幕（去重）：\n{new_eng_word_list}')
    # 把收集到的字幕存入文本
    write_caption_words_into_txt(str_list=new_eng_word_list,save_dir=caption_words_txt_dir,file_name=video_file_name)
    print(f'\n{video_file_name}\n------------------ OCR 字幕图片 提取文字 结束 ---------------------\n')

# 把收集到的字幕存入文本
def write_caption_words_into_txt(str_list,save_dir,file_name):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    content_str = ''
    i = 0
    for s in str_list:
        # 排除空字串
        if not str(s).replace(' ','') == '':
            content_str = f'{s}' if i == 0 else f'{content_str}\n{s}'
            i += 1
    fpath = f'{save_dir}/{file_name}.txt'
    fp = open(fpath,'w',encoding='utf-8')
    fp.write(content_str)
    fp.close()
    print(f'已写入文本：\n{fpath}')

# 读取字幕文本，返回文本中记录的字幕列表
def read_caption_words_from_txt(dir,file_name):
    fpath = f'{dir}/{file_name}.txt'
    caption_words_list = []
    if not os.path.exists(fpath):
        return []
    for line in open(fpath,encoding='utf-8'):
        line = line.replace('\r','').replace('\n','')
        caption_words_list.append(line)
    print(f'已读取文本：\n{fpath}')
    return caption_words_list

# 排除过场视频目录(即 得到除了过场视频以外的其他目录)
# dir_list 的元素只是文件夹名称，不是路径
def filter_dir_transvideo(dir_list):
    return [i for i in dir_list if not i[:len(video_transition_prefix)] == video_transition_prefix]

# 询问使用的视频分段资源
def ask_for_video_source_path(v_source_dir):
    # video/ 下的非过场视频的文件夹列表
    v_source_1th_list = filter_dir_transvideo(filter_listdir(os.listdir(v_source_dir)))
    ask_hint_str = f'请从上面给出的列表中选择要使用的 [分段视频]\n（目前视频来源目录为：{video_source_dir}/）'
    return ask_for_video_path(v_source_dir,v_source_1th_list,ask_hint_str)

def ask_for_video_path(v_source_dir,v_source_1th_list,hint_str='',is_multi=True):
    # 收集视频片段素材的完整路径
    v_source_file_path_list = []
    # 收集视频片段素材的文件名称（与上面的集合数量一定是一致的）(该文件夹下直接存放的是视频文件)
    v_source_file_name_list = []
    # video/ 下的非过场视频的文件夹列表
    # v_source_1th_list = filter_dir_transvideo(filter_listdir(os.listdir(v_source_dir)))
    print('\n--------------------------------------------------------------------------------------------------')
    for vs_1th_name in v_source_1th_list:
        # video/xxx/
        vs_1th_path = f'{v_source_dir}/{vs_1th_name}'
        if not os.path.exists(vs_1th_path):
            continue
        v_source_2th_list = os.listdir(vs_1th_path)
        print(f'[-] - {vs_1th_name}')
        for vs_2th_name in v_source_2th_list:
            # video/xxx/xxx1/fullfiles
            vs_2th_path = f'{vs_1th_path}/{vs_2th_name}/fullfiles'
            if not os.path.exists(vs_2th_path):
                continue
            fullfiles_floder_list = os.listdir(vs_2th_path)
            print(f'  |__ [-] - {vs_2th_name}')
            for fullfiles_floder_name in fullfiles_floder_list:
                # 具体的视频文件所在目录
                # video/xxx/xxx1/fullfiles/abc/
                video_folder_path = f'{vs_2th_path}/{fullfiles_floder_name}'
                if not os.path.exists(video_folder_path):
                    continue
                video_file_list = os.listdir(video_folder_path)
                for video_file_full_name in video_file_list:
                    # video_file_full_name 是包含扩展名的
                    # 具体的视频文件路径
                    # video/xxx/xxx1/fullfiles/abc/abc.mp4
                    video_file_path = f'{video_folder_path}/{video_file_full_name}'
                    if not os.path.exists(video_file_path):
                        continue
                    v_source_file_path_list.append(video_file_path) # 追加到收集集合中
                    v_source_file_name_list.append(video_file_full_name.split('.')[0]) # 记录去后缀的文件名
                    serial_num = len(v_source_file_path_list)
                    print(f'        |__ [{serial_num}] - {fullfiles_floder_name}')
    default_num = 1 # 默认选项，仅对单选有效
    multi_hint = '（可多选）' if is_multi else f'（默认选项：{default_num}）'
    print(f'\n----- {hint_str}{multi_hint}： ----------')
    if is_multi:
        print('多选的话，请用逗号隔开即可，比如：2,10,15,... 或者也可以输入范围，比如 1:5')
    print('输入对应的序号即可')
    user_selected = input()
    user_selection_list = []
    # 整理出的选择视频 绝对路径
    v_selection_path_list = []
    # 整理出的选择视频 文件名（去后缀的文件名）
    v_selection_name_list = []
    if is_multi:
        # 先尝试是否为 '2:6' 类似这样的范围字符串，如果不是则会返回 None
        user_selection_list = get_seirals_by_rangestr(user_selected,1)
        if user_selection_list == None:
            # 如果不是范围字符串，那就只能是 '1,2,3' 类似这样的 都好分隔的字符串
            user_selection_list = [i for i in user_selected.split(',') if not i.replace(' ','') == '']
        print(f'user_selection_list = {user_selection_list}')
        v_selection_path_list = [v_source_file_path_list[int(i)-1] for i in user_selection_list]
        v_selection_name_list = [v_source_file_name_list[int(i)-1] for i in user_selection_list]
        if len(user_selection_list) < 1:
            print('至少选择一项！！！')
            return []
        print('[*] - 已选择：\n绝对路径：\n{}\n---------------\n文件名称：\n{}'.format(v_selection_path_list,v_selection_name_list))
    else:
        user_selected = str(default_num) if not is_int_str(user_selected) else user_selected
        user_selected = str(default_num) if int(user_selected) < 1 or int(user_selected) > len(v_source_file_path_list) else str(user_selected)
        v_selection_path_list = [v_source_file_path_list[int(user_selected)-1]]
        v_selection_name_list = [v_source_file_name_list[int(user_selected)-1]]
        print('[*] - 已选择：\n绝对路径：\n{}\n---------------\n文件名称：\n{}'.format(v_selection_path_list[0],v_selection_name_list[0]))
    print('--------------------------------------------------------------------------------------------------')
    return {'v_source_path_list':v_selection_path_list,'v_source_name_list':v_selection_name_list}


# 独立运行脚本的入口（为了尽量让该脚本可以独立使用，这里也提供了相关函数）
# 该函数也是为开发时使用该脚本提供使用案例
def single_start_func():
    # 视频片段素材资源
    v_source_dir = video_source_dir
    # 询问使用的视频分段资源
    v_source_obj = ask_for_video_source_path(v_source_dir)
    v_source_path_list = v_source_obj['v_source_path_list']
    v_source_name_list = v_source_obj['v_source_name_list']

    print('\n------------- 接下来请继续选择想要执行的操作，若跳步骤执行，请确保相应的前提文件一定存在 ---------')
    hint_options = [
        f'[1] - 为已选择的视频 -- 分解出图片\n    |__ 相关目录：{video_frame_img_dir}',
        f'[2] - 为已选择的视频 -- 分解出的图片进行字幕区域裁剪\n    |__ 相关目录：{video_frame_caption_img_dir}',
        f'[3] - 为已选择的视频 -- 的字幕区域截图进行 ocr 提取英文字幕到本地文本\n    |__ 相关目录：{caption_words_txt_dir}',
        '[4] - 为已选择的视频 -- 进行一条龙服务，即依次自动执行步骤：[1]->[2]->[3]'
    ]
    selection = ask_for_selection(hint_options)

    if selection == '1':
        for idx,video_path in enumerate(v_source_path_list):
            video_file_name = v_source_name_list[idx]
            # 对视频进行拆分出图片
            tailor_video(video_path,video_file_name)
    elif selection == '2':
        #  - thresh_ - （根据提取的文字颜色不同，二设置不同的值，目前100可提取土黄色rgb(214,167,61)和白色的文字）图片灰度处理时，这是个图片颜色的界值，凡是小于该数值的会被一律处理成这个 thresh_ 颜色值，凡是大于该值的都会被处理成代码里设置的  cv2.threshold(imgray, thresh, 255, cv2.THRESH_BINARY) 即这句代码里的 255
        #  - crop_positions - （根据字幕所在图片的位置不同来修改这个参数）控制从一张图片上裁剪出字幕图片的区域位置和尺寸，尺寸大小取决于两坐标之间的距离(差值)，比如 区域高度=y1-y0; 区域宽度=x1-x0
        print('请输入参数值（整数，默认：100）： cv2_thresh：')
        print('参数说明：（根据提取的文字颜色不同，二设置不同的值，目前100可提取土黄色rgb(214,167,61)和白色的文字）图片灰度处理时，这是个图片颜色的界值，\n凡是小于该数值的会被一律处理成这个 thresh_ 颜色值，\n凡是大于该值的都会被处理成代码里设置的  cv2.threshold(imgray, thresh, 255, cv2.THRESH_BINARY) 即这句代码里的 255')
        cv2_thresh = input()
        cv2_thresh = 100 if cv2_thresh == '' else int(cv2_thresh)
        print('请输入参数值（json，默认：{"y0":"630","y1":"730","x0":"100","x1":"1200"}）： cv2_crop_positions:')
        print('参数说明：（根据字幕所在图片的位置不同来修改这个参数）控制从一张图片上裁剪出字幕图片的区域位置和尺寸，尺寸大小取决于两坐标之间的距离(差值)，比如 区域高度=y1-y0; 区域宽度=x1-x0')
        cv2_crop_positions = input()
        cv2_crop_positions = {"y0":"630","y1":"730","x0":"100","x1":"1200"} if cv2_crop_positions == '' else json.loads(cv2_crop_positions)
        for json_key in cv2_crop_positions:
            cv2_crop_positions[json_key] = int(cv2_crop_positions[json_key])
        for video_file_name in v_source_name_list:
            # 对拆分出的图片进行字幕区域逐张裁剪
            tailor_img_for_caption(video_file_name,cv2_thresh=cv2_thresh,cv2_crop_positions=cv2_crop_positions)
    elif selection == '3':
        for video_file_name in v_source_name_list:
            # 对字幕截图进行 ocr 提取文字
            ocr_text_from_caption_imgs(video_file_name)
    elif selection == '4':
        for idx,video_path in enumerate(v_source_path_list):
            video_file_name = v_source_name_list[idx]
            # 一条龙服务，即依次自动执行步骤：[1]->[2]->[3]
            main_func(video_path,video_file_name)
    

''' ------------------- 移除所有自动创建的文件夹和文件 start -------------------'''

def clear_all_folderfiles_of_autocreate():
    # 会移除一些自动创建的目录和文件，会使得整个项目回到几乎初始时的状态
    # logs/
    if os.path.exists(logs_out_dir):
        del_files(logs_out_dir)
        os.rmdir(logs_out_dir)
    # video_frame_imgs/
    if os.path.exists(video_frame_img_dir):
        floder_list = os.listdir(video_frame_img_dir)
        for floder_name in floder_list:
            floder_dir = f'{video_frame_img_dir}/{floder_name}'
            if os.path.exists(floder_dir):
                del_files(floder_dir)
                os.rmdir(floder_dir)
        del_files(video_frame_img_dir)
        os.rmdir(video_frame_img_dir)
    # video_frame_caption_imgs/
    if os.path.exists(video_frame_caption_img_dir):
        floder_list = os.listdir(video_frame_caption_img_dir)
        for floder_name in floder_list:
            floder_dir = f'{video_frame_caption_img_dir}/{floder_name}'
            if os.path.exists(floder_dir):
                del_files(floder_dir)
                os.rmdir(floder_dir)
        del_files(video_frame_caption_img_dir)
        os.rmdir(video_frame_caption_img_dir)
    # video_caption_words/
    if os.path.exists(caption_words_txt_dir):
        del_files(caption_words_txt_dir)
        os.rmdir(caption_words_txt_dir)

''' ------------------- 移除所有自动创建的文件夹和文件 end -------------------'''

''' 提供个外界调用的主入口函数 '''
# video_file_name: 是一个视频的文件名称（去后缀）
def main_func(video_path,video_file_name,cv2_thresh=100,cv2_crop_positions={'y0':630,'y1':730,'x0':100,'x1':1200}):
    # 先拆分出图片
    tailor_video(video_path,video_file_name)
    # 对拆分出的图片进行字幕区域逐张裁剪
    tailor_img_for_caption(video_file_name,cv2_thresh,cv2_crop_positions)
    # 对字幕截图进行 ocr 提取文字
    ocr_text_from_caption_imgs(video_file_name)
''' 提取视频中的英文字幕（使用提取出的文本，便于看美剧学习英语） '''
from .common_util import input_selection
from .ocr_video_caption import single_start_func,clear_all_folderfiles_of_autocreate

def main_func():
    hints = [
        '[1] - 启动提取器：先选择视频源，再进行分解提取英文字幕',
        '[108] - 清除自动创建的目录（就是上面那些视频分解处理时生成的相关目录）'
    ]
    print('[*] - 选择你要的操作（默认项：[1]）：--------------------')
    [print(i) for i in hints]
    selection = input_selection()
    if selection == 1:
        single_start_func()
    elif selection == 108:
        # 清除自动创建的目录（就是那些视频分解处理时的本地文件目录）
        clear_all_folderfiles_of_autocreate()
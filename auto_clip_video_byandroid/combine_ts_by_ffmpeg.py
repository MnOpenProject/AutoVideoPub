import os
from .config.connection_config import ffmpeg_bin_dir

# 为 .ts 文件的（1.ts,2.ts,3.ts,...,101.ts,...）这样的文件列表进行从小到大排序
def bubbleSortTsFile(arr):
    n = len(arr)
    # 遍历所有数组元素
    for i in range(n):
        # Last i elements are already in place
        for j in range(0, n-i-1):
            if int(arr[j].replace('.ts','')) > int(arr[j+1].replace('.ts','')) :
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

filelist_name = 'filelist.txt'
def write_tslist_into_txt(filelist_path,tsFileDir,ts_file_list):
    if os.path.exists(filelist_path):
        os.remove(filelist_path)
    str_content = ''
    ts_end_idx = len(ts_file_list) - 1    
    f_path = filelist_path
    for ts_idx,ts_name in enumerate(ts_file_list):
        rn_str = ''
        if ts_idx < ts_end_idx:
            rn_str = '\n'
        # 写入文本
        str_content = "file '{0}/{1}'".format(tsFileDir,ts_name)
        str_content = str_content.replace('/','\\')
        str_content = f'{str_content}{rn_str}'
        fp = open(f_path,"a",encoding="utf-8")
        fp.write('{0}'.format(str_content))
        fp.close()    

# ffmpeg 官网：http://ffmpeg.org/download.html#build-windows
# 【注意】：使用该方案的前提是：windows 环境中已经安装好了 ffmpeg 环境，安装参考：http://www.360doc.com/content/21/0204/15/54508727_960674843.shtml
# ffmpeg 合并文件方案参考（这里选用的就是参考地址里的 <方案三>）：https://www.cnblogs.com/duanxiaojun/articles/6904878.html
# FFmpeg concat 分离器 合并文件方案
# 这种方法成功率很高，也是最好的，但是需要 FFmpeg 1.1 以上版本。先创建一个文本文件filelist.txt
def combine_ts_by_ffmpeg(tsvideoRoot, tsFileDir, saveFileDir, saveFilePath, log_print):
    tsvideoRoot = tsvideoRoot.replace('/','\\')
    tsFileDir = tsFileDir.replace('/','\\')
    saveFilePath = saveFilePath.replace('/','\\')
    # drive 参数是设定的输出的磁盘
    drive_name = tsvideoRoot[0] # 输出的盘符就是当前工程所在的盘符

    # 利用 windows 的 cmd 指令完成合并
    ts_dir_file_list = os.listdir(tsFileDir)
    ts_file_list = [i for i in ts_dir_file_list if '.ts' in i]
    ts_file_list = bubbleSortTsFile(ts_file_list)
    log_print('准备合并的文件列表----------------------------')
    log_print(ts_file_list)
    # 把要合并的所有 .ts 文件都预先排列好的写入到一个 txt 文件中
    filelist_path = '{0}/{1}'.format(saveFileDir,filelist_name)
    log_print('把要合并的所有 .ts 文件都预先排列好的写入到一个 txt 文件中----------------------------')
    log_print(filelist_path)
    write_tslist_into_txt(filelist_path,tsFileDir,ts_file_list)
    # 然后通过 ffmpeg 指令合并文件
    tsvideoDirCmdStr = drive_name + ": && cd " + tsvideoRoot
    cmdStr = f'{tsvideoDirCmdStr} && {ffmpeg_bin_dir}/ffmpeg -f concat -safe 0 -i {filelist_path} -c copy {saveFilePath}'
    log_print("CMD合成指令：{}".format(cmdStr))
    os.system(cmdStr)
    log_print("{}视频合成完成".format(saveFilePath))
    
    # 移除合并文件时，临时使用的 filelist.txt 文件
    os.remove(filelist_path)

def write_tslist_into_txt2(filelist_path,ts_file_list):
    if os.path.exists(filelist_path):
        os.remove(filelist_path)
    str_content = ''
    ts_end_idx = len(ts_file_list) - 1    
    f_path = filelist_path
    for ts_idx,ts_path in enumerate(ts_file_list):
        rn_str = ''
        if ts_idx < ts_end_idx:
            rn_str = '\n'
        # 写入文本
        str_content = f"file '{ts_path}'"
        str_content = str_content.replace('/','\\')
        str_content = f'{str_content}{rn_str}'
        fp = open(f_path,"a",encoding="utf-8")
        fp.write('{0}'.format(str_content))
        fp.close()  

def combine_ts_by_ffmpeg2(tsvideoRoot, ts_file_list, saveFileDir, saveFilePath, log_print):
    tsvideoRoot = tsvideoRoot.replace('/','\\')
    # tsFileDir = tsFileDir.replace('/','\\')
    saveFilePath = saveFilePath.replace('/','\\')
    # drive 参数是设定的输出的磁盘
    drive_name = tsvideoRoot[0] # 输出的盘符就是当前工程所在的盘符

    # # 利用 windows 的 cmd 指令完成合并
    # ts_dir_file_list = os.listdir(tsFileDir)
    # ts_file_list = [i for i in ts_dir_file_list if sourceFormat in i]
    # ts_file_list = bubbleSortTsFile(ts_file_list)
    log_print('准备合并的文件列表----------------------------')
    log_print(ts_file_list)
    # 把要合并的所有 .ts 文件都预先排列好的写入到一个 txt 文件中
    filelist_path = '{0}/{1}'.format(saveFileDir,filelist_name)
    log_print('把要合并的所有 .ts 文件都预先排列好的写入到一个 txt 文件中----------------------------')
    log_print(filelist_path)
    write_tslist_into_txt2(filelist_path,ts_file_list)
    # 然后通过 ffmpeg 指令合并文件
    tsvideoDirCmdStr = drive_name + ": && cd " + tsvideoRoot
    cmdStr = f'{tsvideoDirCmdStr} && {ffmpeg_bin_dir}/ffmpeg -f concat -safe 0 -i {filelist_path} -c copy {saveFilePath}'
    log_print("CMD合成指令：{}".format(cmdStr))
    os.system(cmdStr)
    log_print("{}视频合成完成".format(saveFilePath))
    
    # 移除合并文件时，临时使用的 filelist.txt 文件
    os.remove(filelist_path)
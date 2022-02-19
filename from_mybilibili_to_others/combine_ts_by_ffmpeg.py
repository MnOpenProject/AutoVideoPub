import os
from .common_config import ffmpeg_bin_dir

# 为 .ts 文件的（1.ts,2.ts,3.ts,...,101.ts,...）这样的文件列表进行从小到大排序
def bubbleSortTsFile(arr):
    n = len(arr)
    # 遍历所有数组元素
    for i in range(n):
        # Last i elements are already in place
        for j in range(0, n-i-1):
            if int(str(arr[j]).replace('.ts','')) > int(str(arr[j+1]).replace('.ts','')) :
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

filelist_name = 'filelist.txt'
def write_tslist_into_txt(filelist_path,ts_file_list):
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

def combine_ts_by_ffmpeg(tsvideoRoot,video_name_dir,ts_file_list, saveFileDir, saveFilePath, log_print):
    # tsvideoRoot = tsvideoRoot.replace('/','\\')
    # tsFileDir = tsFileDir.replace('/','\\')
    # saveFilePath = saveFilePath.replace('/','\\')
    # 合并的所有 .ts 文件时存储组合列表的 txt 文件
    filelist_path = '{0}/{1}__{2}'.format(saveFileDir,video_name_dir,filelist_name)
    if os.path.exists(filelist_path):
        os.remove(filelist_path)
    
    # drive 参数是设定的输出的磁盘
    drive_name = tsvideoRoot[0] # 输出的盘符就是当前工程所在的盘符

    # 删除旧文件（避免 ffmpeg 发现已存在相同文件时会在终端发出询问请求是否覆盖）
    if not os.path.exists(saveFileDir):
        os.makedirs(saveFileDir)
    if os.path.exists(saveFilePath):
        os.remove(saveFilePath)

    # # 利用 windows 的 cmd 指令完成合并
    # ts_dir_file_list = os.listdir(tsFileDir)
    # ts_file_list = [i for i in ts_dir_file_list if sourceFormat in i]
    # ts_file_list = bubbleSortTsFile(ts_file_list)
    log_print('准备合并的文件列表----------------------------')
    log_print(f'ts_file_list: \n{ts_file_list}')

    # 把要合并的所有 .ts 文件都预先排列好的写入到一个 txt 文件中
    # filelist_path = '{0}/{1}__{2}'.format(saveFileDir,video_name_dir,filelist_name)
    log_print('把要合并的所有 .ts 文件都预先排列好的写入到一个 txt 文件中----------------------------')
    log_print(filelist_path)
    write_tslist_into_txt(filelist_path,ts_file_list)
    # 然后通过 ffmpeg 指令合并文件
    tsvideoDirCmdStr = drive_name + ": && cd " + tsvideoRoot
    cmdStr = f'{tsvideoDirCmdStr} && {ffmpeg_bin_dir}/ffmpeg -f concat -safe 0 -i {filelist_path} -c copy {saveFilePath}'
    log_print("CMD合成指令：{}".format(cmdStr))
    os.system(cmdStr)
    log_print("{}视频合成完成".format(saveFilePath))
    
    # 移除合并文件时，临时使用的 filelist.txt 文件
    os.remove(filelist_path)
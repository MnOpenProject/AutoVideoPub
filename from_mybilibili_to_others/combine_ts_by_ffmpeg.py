import os
from .common_config import ffmpeg_bin_dir

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

def combine_ts_by_ffmpeg(tsvideoRoot, ts_file_list, saveFileDir, saveFilePath, log_print):
    # tsvideoRoot = tsvideoRoot.replace('/','\\')
    # tsFileDir = tsFileDir.replace('/','\\')
    saveFilePath = saveFilePath.replace('/','\\')
    # drive 参数是设定的输出的磁盘
    drive_name = tsvideoRoot[0] # 输出的盘符就是当前工程所在的盘符

    if not os.path.exists(saveFileDir):
        os.makedirs(saveFileDir)
    if os.path.exists(saveFilePath):
        os.remove(saveFilePath)

    # # 利用 windows 的 cmd 指令完成合并
    # ts_dir_file_list = os.listdir(tsFileDir)
    # ts_file_list = [i for i in ts_dir_file_list if sourceFormat in i]
    # ts_file_list = bubbleSortTsFile(ts_file_list)
    log_print('准备合并的文件列表----------------------------')
    # 对 .ts 文件列表进行排序，确保按照从小到大 1.ts,2.ts,3.ts,.. 的规则有序排列，否则会造成重组视频发生混乱（重组视频会按照该列表的顺序把视频依次重组）
    ts_file_name_list = [str(i).replace(f'{tsvideoRoot}/','') for i in ts_file_list]
    log_print(f'ts_file_name_list：\n{ts_file_name_list}')
    ts_file_name_list = bubbleSortTsFile(ts_file_name_list)
    ts_file_list = [f'{tsvideoRoot}/{i}' for i in ts_file_name_list] # 为 ts_file_list 参数附上重新排序后的新数组
    log_print(f'ts_file_list\n{ts_file_list}')

    # 把要合并的所有 .ts 文件都预先排列好的写入到一个 txt 文件中
    filelist_path = '{0}/{1}'.format(saveFileDir,filelist_name)
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
    # os.remove(filelist_path)
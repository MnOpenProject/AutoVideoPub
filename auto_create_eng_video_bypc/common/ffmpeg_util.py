import ffmpy3,json,subprocess

# 获取视频文件的时长
# 参考地址：https://blog.csdn.net/lilongsy/article/details/121206810
# 这是基于windows系统安装的 C:\ffmpeg-5.0-essentials_build\bin 里的 ffprobe.exe 来实现的，所以一定要配置好环境变量的 path
# windows 环境变量 path 里增加 C:\ffmpeg-5.0-essentials_build\bin 路径（即 ffmpeg 的 bin 路径）
def get_duration_from_ffmpeg(url):
    print(f'get_duration_from_ffmpeg file-url: \n{url}')
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

# 获取视频文件的时长
# 参考地址：https://www.cnpython.com/qa/76885
# def get_duration_from_ffmpeg(filepath):
#   result = subprocess.Popen(["ffprobe", filepath],
#     stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
#   return [x for x in result.stdout.readlines() if "Duration" in x]

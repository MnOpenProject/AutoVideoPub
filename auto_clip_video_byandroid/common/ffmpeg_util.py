import ffmpy3,json,subprocess

# 获取视频文件的时长
# 参考地址：https://blog.csdn.net/lilongsy/article/details/121206810
def get_duration_from_ffmpeg(url):
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

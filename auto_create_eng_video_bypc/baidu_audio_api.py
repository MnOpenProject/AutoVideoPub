''' 百度文本合成语音接口 '''
'''
参考资料：https://www.jianshu.com/p/52f4c2b0c9c1
我的百度API管理平台地址：https://console.bce.baidu.com/ai/?fromai=1#/ai/speech/app/detail~appId=3133648
'''
from aip import AipSpeech


def download_audio_by_baiduapi(out_dir,content:str,se_id=1,le='zh',audio_name=None):
    # 请注意文本长度必须小于1024字节

    print(f'要转换的文字内容：\n{content}')

    # 百度语音合成 API 密钥(注释参数仅供参考而已，请自行注册获取)
    APP_ID = '' # '13726129'
    API_KEY = '' # 'aS3TcTXr9P0tLPGnomvGI4YB'
    SECRET_KEY = '' # 'GbrsKj3lOXPHWs5lhNhiFJKC2QTUt8YL'

    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
    result  = client.synthesis(content, le, 1, {
        'vol': 5, # 音量，取值0-15，默认为5中音量
        'per': 0 # (1) 普通发音人选择：度小美=0(默认)，度小宇=1，，度逍遥（基础）=3，度丫丫=4; (2) 精品发音人选择：度逍遥（精品）=5003，度小鹿=5118，度博文=106，度小童=110，度小萌=111，度米朵=103，度小娇=5;
    })
    print('result',result)
    # 识别正确返回语音二进制 错误则返回dict 参照 api 文档
    # 百度 api 文档：https://cloud.baidu.com/doc/SPEECH/s/Gk4nlz8tc
    audio_file_name = str(se_id) if audio_name == None else str(audio_name)
    fpath = f"{out_dir}/{audio_file_name}.mp3"
    if not isinstance(result, dict):
        with open('audio.mp3', 'wb') as f:
            f.write(result)
        print(f'【{content}】音频下载完成，保存路径如下\n{fpath}')
        return fpath
    # 下载失败
    print('\n！！！！！！！！！！')
    print(f'【{content}】音频下载失败，对应未下载完成的路径如下\n{fpath}')
    print('\n！！！！！！！！！！')
    return None
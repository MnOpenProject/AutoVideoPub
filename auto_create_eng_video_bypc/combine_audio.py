''' 音频文件合并 '''
# 参考资料：https://blog.csdn.net/sunnyfuyou/article/details/83692166

from pydub import AudioSegment
import os

# 合并多个音频文件
def combine_audio_files(audio_file_path_list:list[str],out_audio_full_path:str,silence_sec=2):
    # params audio_file_path_list: 所有要合并的音频文件的绝对路径的集合（会按照集合中的顺序进行合并，所以要提前根据需要进行排序）
    # params out_audio_full_path: 最终合并后的输出音频的绝对路径（.mp3）
    # params silence_sec: 每个音频文件合并后的间隔时长(2个音频文件合并后中间的静音时长)（单位：秒）

    print(f'out_audio_full_path = {out_audio_full_path}')
    if os.path.exists(out_audio_full_path):
        os.remove(out_audio_full_path)
    
    # 每个音频之间的静音时长（2个音频文件合并后中间的静音时长）
    silence_times = 1000*silence_sec

    # 检查所有音频是否都存在，只要有一个音频文件不存在，则不执行合并
    losed_audios = []
    for audio_file_path in audio_file_path_list:
        if not os.path.exists(audio_file_path):
            losed_audios.append(audio_file_path)
    if len(losed_audios) > 0:
        print(f'合并失败，以下音频文件不存在：\n{losed_audios}')
        print("********************************************************")
        return

    # 遍历音频文件列表，并逐一生成对应的音频对象
    sounds = []
    for file in audio_file_path_list:
        sounds.append(AudioSegment.from_mp3(file))

    # 生成静音的音频对象
    silence_ring = AudioSegment.silent(int(silence_times))

    # 把音频对象进行合并，每个音频对象之间添加相应的静音
    ring_lists = AudioSegment.empty()
    for sound in sounds:
        ring_lists += sound # 音频对象
        ring_lists += silence_ring  # 添加静音对象
    # 导出音频
    ring_lists.export(out_audio_full_path, format="mp3")
    # 返回最终合成后输出的音频文件的绝对路径
    return out_audio_full_path

# 在音频文件的头/尾添加一定的静音时长(音频必须是 .mp3 格式)
def add_silence_headend_for_audio(source_audio_full_path:str,out_audio_full_path:str,silence_sec=2, position='head-end'):
    # params source_audio_full_path: 原始视频文件
    # params out_audio_full_path: 最终合并后的输出音频的绝对路径（.mp3）
    # params silence_sec: 要添加的静音时长（单位：秒）
    # params position: 静音添加的位置， 'head'=在原始音频文件的前面添加一段静音; 'end'=在原始音频文件的最后添加一段静音; 'head-end'=在原始音频文件的头尾都添加一段静音;

    print(f'source_audio_full_path = {source_audio_full_path}')
    print(f'out_audio_full_path = {out_audio_full_path}')
    if os.path.exists(out_audio_full_path):
        os.remove(out_audio_full_path)
    
    # 静音时长
    silence_times = 1000*silence_sec

    # 检查原始音频是否都存在
    if not os.path.exists(source_audio_full_path):
        print(f'添加静音失败，原始音频文件不存在：\n{source_audio_full_path}')
        print("********************************************************")
        return

    # 遍历音频文件列表，并逐一生成对应的音频对象
    source_sound = AudioSegment.from_mp3(source_audio_full_path)

    # 生成静音的音频对象
    silence_ring = AudioSegment.silent(int(silence_times))

    #  把音频对象进行合并，根据参数，在相应的位置添加静音对象
    ring_lists = AudioSegment.empty()
    if position == 'head':
        ring_lists += silence_ring
        ring_lists += source_sound
    elif position == 'end':
        ring_lists += source_sound
        ring_lists += silence_ring
    else: # 'head-end'
        ring_lists += silence_ring
        ring_lists += source_sound
        ring_lists += silence_ring
    # 导出音频
    ring_lists.export(out_audio_full_path, format="mp3")
    return out_audio_full_path
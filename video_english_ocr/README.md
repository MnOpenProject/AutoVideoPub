# 视频英文字幕提取器

* 
    * 模块中的功能说明：ocr_video_caption.py （视频英文字幕提取并翻译）是主脚本，目前读取的是 auto_clip_video_byandroid/video/ 目录下的分段视频资源（若向读取其他目录，请自行修改代码，因为不同的目录，层级结构不同，读取方式也不同），主要是为了自己看美剧学英语时摘取语句能方便些，而开发了该模块，希望对各位也能有所帮助，以下是该模块的功能：
    * * 把视频逐帧分解为图片
    * * 对分解出的帧图片再次裁剪出字幕区域的截图和颜色处理
    * * 对字幕截图进行OCR识别提取出英文文本
    * （使用者可以一次性执行完整功能，也可以根据需求执行单个功能，功能已经被细分了，详细说明在执行脚本时都提供了终端提示，各位根据终端提示进行使用吧）

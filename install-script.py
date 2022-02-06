import os

# livereload 实现对 html 模板的热更新，主动调用浏览器刷新
# ffmpy 视频处理方案：合并 .ts 文件参考 -- https://blog.csdn.net/u011027547/article/details/122490254
# ffmpy 合并文件的方案参考：https://www.cnblogs.com/duanxiaojun/articles/6904878.html
cmdStr = "pip install requests tqdm selenium flask livereload threadpool pillow progressbar pycryptodome ffmpy3 eventlet"
os.system(cmdStr)

# npm 全局工具包安装
cmdStr = 'npm install -g appium'
os.system(cmdStr)
cmdStr = 'npm install -g appium-doctor'
os.system(cmdStr)
# 检查 appinum
cmdStr = 'appium-doctor --android'
os.system(cmdStr)
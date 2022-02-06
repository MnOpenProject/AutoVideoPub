import os

# 因为 python 无法从别的深层文件夹目录下直接获取工程的根目录，所以这里设置一个全局变量脚本，用于设置一些常用的公共变量

# 项目根目录
__ROOTPATH__ =  os.path.abspath(os.path.dirname(__file__)) + "\\"
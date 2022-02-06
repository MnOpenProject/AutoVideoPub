''' Flask 官方中文API: https://dormousehole.readthedocs.io/en/latest/api.html#configuration '''
import os
from flask import Flask
app = Flask(__name__)

app.config['DEBUG'] = True
# Flask热更新html模板文件
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True

""" 环境变量设置 """
# 开发环境设置：FLASK_ENV 变量用来告诉Flask当前应用所运行的环境，有两个值，分别是 “production” 和 “development”，默认缺省值是“production
os.environ["FLASK_ENV"] = "development"
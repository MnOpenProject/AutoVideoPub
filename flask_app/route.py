
import os,json
from globalvars import __ROOTPATH__

from flask import request, render_template
from flask_app.flask_app import app

@app.route('/')
def index():
    return render_template('index.html')
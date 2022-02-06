import os
import sys
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,BASE_PATH)
from flask_app.route import app
from config.setting import SERVER_PORT

# print("http://127.0.0.1:{}".format(SERVER_PORT))

if __name__ == '__main__':
    from livereload import Server
    server = Server(app.wsgi_app)
    server.watch('**/*.*')
    server.serve()
    # app.run(host='0.0.0.0',port=SERVER_PORT,debug=True)
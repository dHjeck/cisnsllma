from flask import Flask, send_file, jsonify, request
from flask.views import View, MethodView
import subprocess
import threading
import os
from flask_cors import CORS
import configparser
import baidu_chatglm2
import mysql.connector

app = Flask(__name__)
CORS().init_app(app)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="root"
    )
db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'root'
}

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        
        if user:
            # 登录成功，返回 token 或其他数据
            return jsonify({'success': True, 'data': 'fake_token'})
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'})
    
    finally:
        cursor.close()
        conn.close()

        
# 主体运行
class LLMAApi(MethodView):
    def get(self):
        def run_subprocess():
            command = "python DPA_torch.py"
            process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            process.wait()
        t = threading.Thread(target=run_subprocess)
        t.start()
        print("LLMA is running...")
        return {
            'status': 'success',
            'message': 'LLMA is runing!',
        }


# 下载log文件
class ResultDownload(MethodView):
    def get(self):
        path = "./log"
        lists=os.listdir(path)
        lists.sort(key=lambda fn: os.path.getmtime(path + "/" + fn)
                    if not os.path.isdir(path + "/" + fn) else 0)
        file = os.path.join(path, lists[-1])
        print("完整路径", file)
        if os.path.exists(file):
            return send_file(file, as_attachment=True)
        else:
            return {'status': 'error', 'message': '文件不存在或者还没有运行完成，请耐心等待。'}

#修改目标ip地址
@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.json
    targetIP = data.get('target')
    print(targetIP)
    config = configparser.ConfigParser()
    config.read('./settings/ip.ini', encoding='utf-8')
    print(config['server']['ip'])
    config.set('server', 'ip', str(targetIP))
    config.write(open('./settings/ip.ini', "w"))
    print(config['server']['ip'])

    return jsonify({'status': 'success', 'message': 'success'})


# 显示log内容
class TestResult(MethodView):
    def get(self):
        path = "./log"
        lists=os.listdir(path)
        lists.sort(key=lambda fn: os.path.getmtime(path + "/" + fn)
                    if not os.path.isdir(path + "/" + fn) else 0)
        file = os.path.join(path, lists[-1])
        print("完整路径", file)
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(content)
            return jsonify({'content': content})
        else:
            return {'status': 'error', 'message': '文件不存在或者还没有运行完成，请耐心等待。'}


# 总结得分
class Score(MethodView):
    def get(self):
        log = ""
        score = "error"
        path = "./log"
        retry = 0
        lists=os.listdir(path)
        lists.sort(key=lambda fn: os.path.getmtime(path + "/" + fn)
                    if not os.path.isdir(path + "/" + fn) else 0)
        file = os.path.join(path, lists[-1])
        print("完整路径", file)
        with open(file, 'r', encoding="utf-8") as f:
            for lin in f.readline():
                if lin == "\n":
                    pass
                else:
                    log = log + lin
            f.close()
        while score == "error":
            if retry != 3:
                score = baidu_chatglm2.get_score(log)
                retry = retry + 1
            else:
                score = 0
                return score
        return jsonify({'score': score})

#运行执行main.py
LLMA_view = LLMAApi.as_view('llma_api')
app.add_url_rule('/llma/scan', view_func=LLMA_view, methods=['GET'])
#注册下载结果
download_view = ResultDownload.as_view('result_download')
app.add_url_rule('/llma/download', view_func=download_view, methods=['GET'])
#注册结果显示
Result_view = TestResult.as_view('test_result')
app.add_url_rule('/llma/textresult', view_func=Result_view, methods=['GET'])
# 注册评分
Score_view = Score.as_view('score')
app.add_url_rule('/llma/score', view_func=Score_view, methods=['GET'])






if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
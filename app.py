from flask import Flask, send_file, jsonify, request
from flask.views import View, MethodView
import subprocess
import threading
import os
from flask_cors import CORS
import configparser


app = Flask(__name__)
CORS().init_app(app)

@app.route('/')
def index():
    return 'Hello, World!'


class LLMAApi(MethodView):
    def get(self):
        def run_subprocess():
            process = subprocess.Popen(['python', 'main.py'], stdout=subprocess.PIPE, shell=True)
            process.wait()
        t = threading.Thread(target=run_subprocess)
        t.start()
        print("LLMA is running...")
        return {
            'status': 'success',
            'message': 'LLMA is runing!',
        }

class ResultDownload(MethodView):
    def get(self):
        path = ".\\result"
        lists=os.listdir(path)
        lists.sort(key=lambda fn: os.path.getmtime(path + "\\" + fn)
                    if not os.path.isdir(path + "\\" + fn) else 0)
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



class TestResult(MethodView):
    def get(self):
        path = ".\\result"
        lists=os.listdir(path)
        lists.sort(key=lambda fn: os.path.getmtime(path + "\\" + fn)
                    if not os.path.isdir(path + "\\" + fn) else 0)
        file = os.path.join(path, lists[-1])
        print("完整路径", file)
        if os.path.exists(file):
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(content)
            return jsonify({'content': content})
        else:
            return {'status': 'error', 'message': '文件不存在或者还没有运行完成，请耐心等待。'}

class Score(MethodView):
    def get(self):
        return jsonify({'score': 10})

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
    app.run(debug=True)
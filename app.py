from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import subprocess
import socket
import json

app = Flask(__name__, static_url_path='', static_folder='uploads/')
app.config['UPLOAD_FOLDER'] = 'uploads/'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():

    if request.method == 'POST':
        f = request.files['photo']
        secure_name = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_name))

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 8999))
        task_info = {
            'pic_path': '/root/darknet/uploads/{}'.format(secure_name)
        }
        msg = json.dumps(task_info)
        client.send(msg.encode('utf-8'))
        data = client.recv(1024)
        result = json.loads(data.decode())
        print(result['result_path'])
        result_name = result['result_path'].replace('/root/darknet/uploads/', '')
        client.close()

        return jsonify({"type": "success", "msg": "上传图片成功！", "secure_name": secure_name, "result_name": result_name}), 200


if __name__ == '__main__':
    app.run(port=42366)

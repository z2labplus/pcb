import socket
import json

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 8999))

task_info = {
    'pic_path': '/root/darknet/pics/01_spur_17.jpg'
}

msg = json.dumps(task_info)
client.send(msg.encode('utf-8'))
data = client.recv(1024)
result = json.loads(data.decode())
print(result['result_path'])
client.close()

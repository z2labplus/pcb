from darknet import *
from darknet_images import *
import time
import cv2
import socket
import json


def classify(net, meta, im):
    out = predict_image(net, im)
    res = []
    for i in range(meta.classes):
        res.append((meta.names[i], out[i]))
    res = sorted(res, key=lambda x: -x[1])
    return res

def detect(net, meta, image, thresh=.5, hier_thresh=.5, nms=.45):
    im = load_image(image, 0, 0)
    pnum = pointer(c_int(0))
    predict_image(net, im)
    dets = get_network_boxes(net, im.w, im.h, thresh, hier_thresh, None, 0, pnum, 0)
    num = pnum[0]
    if (nms): do_nms_obj(dets, num, meta.classes, nms)

    res = []
    for j in range(num):
        for i in range(meta.classes):
            if dets[j].prob[i] > 0:
                b = dets[j].bbox
                res.append((meta.names[i], dets[j].prob[i], (b.x, b.y, b.w, b.h)))
    res = sorted(res, key=lambda x: -x[1])
    # free_image(im)
    # free_detections(dets, num)
    return res
    
if __name__ == "__main__":
    # 设置当前使用的GPU设备仅为0号设备  设备名称为'/gpu:0'
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    net = load_net(b"pcb.cfg", b"pcb.weights", 0)
    meta = load_meta(b"pcb.data")
    # net, class_names, class_colors = load_network("pcb.cfg", "pcb.data", "pcb.weights", batch_size=1)

    # save_dir = '/root/darknet/pics_out/'
    save_dir = '/root/darknet/uploads/'
    
    count = 0

    s = socket.socket()
    host = '127.0.0.1'
    port = 8999
    s.bind((host, port))
    s.listen(5)
    while True:
        c, addr = s.accept()
        print("socket connet from:{}".format(addr))
        try:
            recv_data = c.recv(1024)
            task_info = json.loads(recv_data)
            print(task_info)
            img = task_info['pic_path']
            r = detect(net, meta, img.encode('utf-8'))
            im = cv2.imread(img)
            for res in r:
                x1 = int(res[2][0] - (res[2][2] / 2))
                y1 = int(res[2][1] - (res[2][3] / 2))
                x2 = x1 + int(res[2][2])
                y2 = y1 + int(res[2][3])
                cv2.rectangle(im, (x1 - 5, y1 - 5), (x2 + 5, y2 + 5), (0, 0, 255), 3)
                cv2.putText(im, str(res[0]).split("'")[1], (x1 - 10, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

            result_path = save_dir + str(int(time.time())) + '.jpg'
            cv2.imwrite(result_path, im)

            result = {
                'result_path': result_path
            }

            c.send(json.dumps(result).encode('utf-8'))

        except ConnectionResetError as e:
            print('socket closed!')
            break
        c.close()


    # # 测试数据集的路径
    # test_dir = '/root/darknet/pics/'
    # # 检测结果保存路径
    # save_dir = '/root/darknet/pics_out/'
    # if not os.path.exists(save_dir):
    #     os.mkdir(save_dir)
        
    # pics = os.listdir(test_dir)
    # count = 0
    # # print(pics)
    # for im in pics:
    #     img = os.path.join(test_dir, im)
    #     s = time.time()
    #     r = detect(net, meta, img.encode('utf-8'))
    #     # image, detections = image_detection(img, net, class_names, class_colors, .25)
    #     # 输出的检测结果中坐标信息为目标的中心点坐标和box的w和h
    #     print("一张图检测耗时：%.3f秒" % (time.time() - s))
    #     im = cv2.imread(img)
    #     for res in r:
    #         x1 = int(res[2][0] - (res[2][2] / 2))
    #         y1 = int(res[2][1] - (res[2][3] / 2))
    #         x2 = x1 + int(res[2][2])
    #         y2 = y1 + int(res[2][3])
    #         cv2.rectangle(im, (x1 - 5, y1 - 5), (x2 + 5, y2 + 5), (0, 255, 0), 2)
    #         cv2.putText(im, str(res[0]).split("'")[1], (x1 - 10, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    #     cv2.imwrite(save_dir + str(count) + '.jpg', im)
    #     count += 1
    # time.sleep(100)
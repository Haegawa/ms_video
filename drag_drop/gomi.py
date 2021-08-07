#!/usr/bin/env python
from __future__ import print_function, unicode_literals
#import rospy
#from std_msgs.msg import String
#from sensor_msgs.msg import Image
import yaml
import numpy as np
import cv2
import http.server
import socketserver
from urllib.parse import unquote
import threading
from queue import Queue
import time
import requests
import json

PORT = 8000
web_recieve_que = Queue()

class ServerHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        #body部を取得
        content_len  = int(self.headers.get("content-length"))
        req_body = self.rfile.read(content_len).decode("utf-8")
        req_body = unquote(req_body)

        print( "data", req_body )

        # ブラウザからクリック位置がpostされてきたら，web_recieve_queに入れる
        if req_body.startswith("pos="):
            pos = req_body[4:]
            web_recieve_que.put( [ int(i) for i in pos.split(",") ] )

        body = "recieved"
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Content-length', len(body.encode()))
        self.end_headers()
        self.wfile.write(body.encode())


def slack(pro=True):
    TOKEN = 'xoxb-2243373668434-2292467356611-jUCuYnXNJW3V280fFwfwSsux'
    CHANNEL = 'api_test'

    url = "https://slack.com/api/chat.postMessage?channel=api_test&text=%E3%83%86%E3%82%B9%E3%83%88%E3%81%A7%E3%81%99%EF%BC%81&pretty=1"
    headers = {"Authorization": "Bearer "+TOKEN}
    data  = {
        'channel': CHANNEL,
        'text': ngrok() + '/test2.html'
    }

    proxies = {
      'http': 'http://proxy.uec.ac.jp:8080',
      'https': 'http://proxy.uec.ac.jp:8080',
    }

    if pro:
        #プロキシないとき
        r = requests.post(url, headers=headers, data=data)
    else:
        #プロキシあるとき
        r = requests.post(url, headers=headers, data=data, proxies=proxies)


def ngrok():
    respons = requests.get('http://localhost:4040/api/tunnels')
    url_ng = respons.json()['tunnels'][0]['public_url']
    print (url_ng)
    return url_ng


def main():
    #rospy.init_node('listener', anonymous=True)

    # 画像を表示するhttpサーバー
    socketserver.TCPServer.allow_reuse_address = True 
    server = socketserver.TCPServer(("", PORT), ServerHandler)
    threading.Thread( target=server.serve_forever, daemon=True ).start()
    print("serving at port", PORT)

    # 画像と物体認識結果を取得
    #data = rospy.wait_for_message( '/object_rec/object_info',  String )
    #obj_info = yaml.load(data.data)

    #data = rospy.wait_for_message( '/camera/color/image_raw',  Image )
    #img = np.frombuffer(data.data, dtype=np.uint8).reshape(data.height, data.width, -1)
    #img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    #for o in obj_info:
    #    cv2.rectangle( img, o["lefttop"], o["rightbottom"], (255,0,0), thickness=2 )

    #cv2.imwrite( "test.png" , img )
    
    # キューを空にする
    while not web_recieve_que.empty():
        web_recieve_que.get()

     # キューに情報が来るのを待機
    # ブラウザでhttp://(スクリプトを実行してるPCのIP):8000/tellme.html
    pos = web_recieve_que.get()
    pos1 = [pos[0],pos[1]]
    pos2 = [pos[2],pos[3]]
    print("物体初期位置：", pos1)
    print( "物体最終位置 : ", pos2)
    time.sleep(3)



        
if __name__ == '__main__':
    slack()
    main()
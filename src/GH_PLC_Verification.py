# -*- coding: UTF-8 -*-
#@ brief: 尝试向 plc 发送校验码

import socket               # 导入 socket 模块
import time
import argparse

class ServerPLC(object):
    def __init__(self, host='192.168.0.176', port=11223):
        """
        Args:
            host: string , 当前主机的 ip 地址
            port: int,  设置当前主机的端口号
            data: string, 向plc 发送的数据
        """
        self.host = host
        self.port = port

    def try_connect(self,data): 
        try:
            data = data.encode()
            print("data :", data)
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            print("host: %s, port: %s"%(self.host, self.port))
            s.bind((self.host, self.port))
            s.listen(5)
            print("绑定地址")
            c, addr = s.accept()
            print("发送数据....")
            c.send(data)
            print("发送成功")
            print("断开连接")
            c.close()   # 断开连接
            s.close()
            return True
        except Exception as e:
            print("连接失败，error:", e)
            return False

    def easy_send(self, data_str):
        try:
            data = data_str.encode()
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.connect((self.host,self.port))
            print("连接成功，发送数据：", data_str)
            s.send(data)
            print("发送成功")
            print("断开连接")
            s.close()
            return True
        except Exception as e:
            print("连接失败，error:", e)
            return False

    def work(self, data):
        print("尝试建立连接")
        # connect = self.try_connect(data)
        connect = self.easy_send(data)
        if not connect:
            for i in range(5):
                print("尝试第 %s 次重新连接"%i)
                time.sleep(1)
                # connect = self.try_connect(data)
                connect = self.easy_send(data)
                if connect:
                    break

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host",type=str, default="192.168.0.139")
    parser.add_argument("--port","-p", type=int, default=12345)
    parser.add_argument("--data","-d", type=str)
    global args
    args = vars(parser.parse_args())
    host = args['host']
    port = args['port']
    data = args['data']
    # data = str(int(time.time()))[-4:]
    server_plc = ServerPLC(host, port)
    server_plc.work(data)  
    # server_plc.easy_send(data)
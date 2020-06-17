# -*- coding: UTF-8 -*-

import socket
import time
# class GhClient(object):
#     def __init__(self, addr, port):
#         self.udpaddr = (addr, port)  # 接收方 服务器的ip地址和端口号
#         self.udpserver = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#         self.udpserver.bind(self.udpaddr)
#         self.ghVerification = None
    
#     def broadcast(self, msg_str):
#         LOG.info("向grasshopper 广播数据: %s"%msg_str)
#         self.udpserver.sendto(msg_str.encode("utf-8"), self.udpaddr)
#         LOG.info("广播结束")
    
#     def receiveData(self):
#         # while True:
#         data  = self.udpserver.recvfrom(256) 
#         self.ghVerification = data[0].decode("utf-8")
#         print(self.ghVerification)
#         return self.ghVerification
#             # print(ghVerification)

#     def disconnect(self):
#         self.udpserver.close()

if __name__=="__main__":
    addr = "127.0.0.1"
    port = 8849
    udpaddr = (addr, port)  # 接收方 服务器的ip地址和端口号
    udpserver = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    udpserver.bind(udpaddr)
    count = 30
    while count >0:
        time.sleep(1)
        # udpserver.bind(udpaddr)
        data = udpserver.recvfrom(1024)
        ghVerification = data[0].decode("utf-8")
        print(ghVerification)
        count -= 1
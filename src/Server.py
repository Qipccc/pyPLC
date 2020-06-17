# -*- coding: UTF-8 -*-

import socket               # 导入 socket 模块
import time
import pdb


def correct_info(c):
    print("send correct info")
    #  机械臂1
    info = "   start1 "
    for i in range(8):           
        data = str(i+2) * 10
        info += data
    info += "    end1  "  
    #  机械臂2


    info += "   start2 "
    for i in range(8):           
        data = str(8-i) * 10
        info += data
    info += "    end2  "
    c.send(info.encode())

def blank_info(c,count=5):
    while count >0:
        print("count: %s"%count)
        info_str = " "*200
        c.send(info_str.encode())
        count -= 1
        time.sleep(0.5)

def error_info(c,num=2):
    print("send error info")
    info = "errorstart"
    info += "%s         "%num
    for i in range(18):           
        data = "          "
        info += data
    c.send(info.encode())




if __name__=="__main__":
    s = socket.socket()         # 创建 socket 对象
    port = 12346           # 设置端口
    pdb.set_trace()
    s.bind(('192.168.0.226', port))        # 绑定端口
    
    s.listen(5)                 # 等待客户端连接
    time.sleep(3)
    # for i in range(8):
    c,addr = s.accept()     # 建立客户端连接
    blank_info(c,2)  # 连续发送n次空白信息
    correct_info(c) # 发送正确信息
    error_info(c,2)  # 发送错误信息
    blank_info(c,20)
    # time.sleep(10)
    correct_info(c) # 发送正确信息
    error_info(c,5)  # 发送错误信息
    
    # data = c.recv(1024)
    # print('recive:',data.decode()) #打印接收到的数据
    c.close()
    s.close()               

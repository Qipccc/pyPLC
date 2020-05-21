# -*- coding: UTF-8 -*-
#@brief: 通过  tcp/ip 通讯与plc接收来自 plc 的数据，得到数据之后再由udp 通讯 发送给 gh 
#@author: qipccc_roboticplus   qipccc@roboticplus.com

import socket               # 导入 socket 模块
import time
import struct
import argparse
import _thread


def get_time():
    end_time = time.clock()
    print("运行时长： %.2f 秒"%(end_time-start_time), end="\r")

def clientGetRes(host,  port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    s.connect((host, port))
    print("Successfully ! 连接 PLC 成功！")
    res1 , res2 = [0] * 8,[0]*8
    count = 10 
    flag = -1
    print("监听程序....")
    print("机械臂正在运动至指定位置....")
    while count > 0:   
        packet = s.recv(200)
        info = struct.unpack("!200s",packet)[0]
        info_str = str(info, encoding = "utf-8")
        is_start1 = info_str[:10].rstrip().lstrip() # 去除空格
        if is_start1 == "start1":
            print("接收得到 机械臂1 数据......")
            for i in range(8):
                d1 = info_str[(i+1)*10:(i+2)*10].rstrip().lstrip() 
                if d1:
                    res1[i] = float(d1)
                else:
                    res1[i] = -999
            flag += 1
            print("res1: ", res1)
        is_start2 = info_str[100:110].rstrip().lstrip() # 去除空格
        if is_start2 == "start2":
            print("接收得到 机械臂2 数据......")
            for i in range(10, 18):
                d2 = info_str[(i+1)*10:(i+2)*10].rstrip().lstrip() 
                if d2:
                    res2[i-10] = float(d2)
                else:
                    res2[i-10] = -999
            flag += 1
            print("res2:", res2)
        if flag >= 0:
            break
        if is_start1 == "errorstart":
            error_info = info_str[10:].rstrip().lstrip()
            # print("%s error info: %s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) , error_info))
            raise Exception("%s error info: %s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) , error_info))   # 用于后面捕获异常
        # count -= 1   # 测试用
        # print(info_str)
    return res1,res2

def ghUDP(msg):
    udpsever=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    server_address = (args['gh_addr'], args['gh_port'])  # 接收方 服务器的ip地址和端口号
    print(msg)
    udpsever.sendto(msg.encode("utf-8"), server_address) #将msg内容发送给指定接收方

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--gh-addr','-ga',type=str,default="127.0.0.1")
    parser.add_argument('--gh-port', '-gp', type=int, default=8848)
    parser.add_argument('--plc-addr','-pa', type=str, default="192.168.100.1")
    parser.add_argument('--plc-port','-pp', type=int, default=3000)
    global args
    args = vars(parser.parse_args())
    start_time = time.clock()
    print("上海大界机器人科技有限公司")
    print("\n")
    print("正在运行红外测试程序....")
    # task = MyThread(clientGetRes,)
    plc_port = args['plc_port']
    plc_addr = args['plc_addr']
    print("PLC ip: %s, port: %s"%(plc_addr, plc_port))
    _thread.start_new_thread(get_time,())
    count  = 5
    while count > 0:
        count -= 1
        try:
            res1, res2 = clientGetRes(plc_addr,plc_port)

            msg = str(res1[0])
            for i in range(1, len(res1)):
                msg = msg +   ',' + str(res1[i])
            msg += ";"
            for i in range(len(res2)):
                msg =  msg + str(res2[i]) + ','
            print("得到 plc 数据，向grasshopper 广播数据, ip: %s, port: %s"%(args['gh_addr'], args['gh_port']))
            print("向 gh 端广播从plc采集得到的数据：")
            ghUDP(msg)
            print("发送完毕，2秒后关闭程序")
            time.sleep(2)
        except Exception as e:
            print("Failure ! ", e)
            ghUDP("None")
            # print("2秒后关闭程序")
            time.sleep(2)

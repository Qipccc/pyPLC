# -*- coding: UTF-8 -*-
#@brief: 通过  tcp/ip 通讯与plc接收来自 plc 的数据，得到数据之后再由udp 通讯 发送给 gh 
#@author: qipccc_roboticplus   qipccc@roboticplus.com

import socket               # 导入 socket 模块
import time
import struct
import argparse
import _thread

from Utils import create_logger, create_TempFolder,readText2Dic

ERROR_DICT ={}
def get_time():
    end_time = time.clock()
    print("运行时长： %.2f 秒"%(end_time-start_time), end="\r")


class GhClient(object):
    def __init__(self, addr, port):
        self.udpaddr = (addr, port)  # 接收方 服务器的ip地址和端口号
        self.udpserver = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    
    def broadcast(self, msg_str):
        LOG.info("向grasshopper 广播数据: %s"%msg_str)
        self.udpserver.sendto(msg_str.encode("utf-8"), self.udpaddr)
        LOG.info("广播结束")

class PlcClient(object):
    def __init__(self,addr, port, timeout=3):
        self.addr = addr
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(timeout)
    
    def connect(self):
        self.s.connect((self.addr, self.port))
        LOG.info("Successfully ! 连接 PLC 成功！")
    
    def disconnect(self):
        LOG.info("断开与PLC的网络连接")
        self.s.close()
    
    def _decodeLaserDate(self,robot_num, info_str):
        """
            robot_num: int ,0,1,2... which robot
        """
        res = [-999] * 8 
        LOG.info("接收得到 机械臂 %d 数据......"%robot_num)
        for i in range(robot_num*10,robot_num*10+8):
            info_data = info_str[(i+1)*10:(i+2)*10].rstrip().lstrip() 
            if info_data:
                res[int(i%10)] = float(info_data)
        return res

    def sendRes(self,bufsize=200, ghclient = None):
        count = 10 
        flag = -1
        # LOG.info("机械臂正在运动至指定位置....")
        while count > 0:  
            packet = self.s.recv(bufsize)
            info = struct.unpack("!200s",packet)[0]
            info_str = str(info, encoding = "utf-8")
            head1 = info_str[:10].rstrip().lstrip() # 获得前10个字符数据并进行判断
            head2 = info_str[100:110].rstrip().lstrip()
            if head1 == "errorstart":
                error_index = info_str[10:].rstrip().lstrip()
                error_info = ERROR_DICT[int(error_index)]
                # todo 查找alarm_information
                raise Exception("Error: %s"%(error_info))   # 用于后面捕获异常
            if head1 == "start1":
                res1 = self._decodeLaserDate(0, info_str)
                flag += 1
                LOG.info("res: %s"%res1)    
            if head2 == "start2":
                res2 = self._decodeLaserDate(1, info_str)
                flag += 1
                LOG.info("res: %s"%res2)
            if ghclient and flag >= 0:
                msg = self.encodeUdpMsg([res1,res2])
                ghclient.broadcast(msg)
            # count -= 1   # 测试用

    def encodeUdpMsg(self,res_list):
        msg = ""
        for res in res_list:
            msg += ",".join([str(i) for i in res])
            msg += ";"
        return msg



if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--gh-addr','-ga',type=str,default="127.0.0.1")
    parser.add_argument('--gh-port', '-gp', type=int, default=8848)
    parser.add_argument('--plc-addr','-pa', type=str, default="192.168.100.1")
    parser.add_argument('--plc-port','-pp', type=int, default=3000)
    global args

    #=========== 变量初始化 ==========================================
    args = vars(parser.parse_args())
    start_time = time.clock() # 程序开始计时
    plc_addr = args['plc_addr']
    plc_port = args['plc_port']
    gh_addr = args['gh_addr']
    gh_port = args['gh_port']

    #=========== 创建日志文件 ==========================================
    logfilePath = create_TempFolder("RobotsPlc")
    LOG = create_logger("RobotsPlc",logfilePath)
    LOG.info("\n %s 上海大界机器人科技有限公司 %s \n  运行红外测试程序...... "%("="*15,"="*15)) 
    LOG.info("PLC ip: %s, port: %s"%(plc_addr, plc_port))
    LOG.info("Grasshopper ip :%s, port: %s"%(gh_addr, gh_port))
    LOG.info("监听程序....")

    #=========== 多线程计时 =============================================
    _thread.start_new_thread(get_time,())
    count  = 2

    #=========== 分别声明 plc 和 grasshopper 的地址和端口对象 ============= 
    client = PlcClient(plc_addr, plc_port)
    ghclient = GhClient(gh_addr, gh_port)

    #=========== 尝试与PLC建立连接 ======================================= 
    try:
        client.connect()
        ERROR_DICT = readText2Dic("alarm_information.txt")
    except Exception as e:
        LOG.error(e)

    #=========== 进入主循环 ==============================================
    while count > 0:
        try:
            client.sendRes(ghclient = ghclient)
        except Exception as e:
            LOG.error("Failure! %s"%e)
            ghclient.broadcast("None")
            count -= 1
        time.sleep(2) # 等待两秒
    client.disconnect()

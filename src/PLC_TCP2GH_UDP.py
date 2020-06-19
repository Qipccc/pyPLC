# -*- coding: UTF-8 -*-
#@brief: 通过  tcp/ip 通讯与plc接收来自 plc 的数据，得到数据之后再由udp 通讯 发送给 gh 
#@author: qipccc_roboticplus   qipccc@roboticplus.com

import socket               # 导入 socket 模块
import time
import struct
import argparse
import os
import threading
from Utils import create_logger, create_TempFolder,readText2Dic
# import ipdb
os.system('')
ERROR_DICT ={}


def get_time():
    end_time = time.clock()
    print("运行时长： %.2f 秒"%(end_time-start_time), end="\r")


class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args
 
    def run(self):
        # time.sleep(2)
        self.result = self.func(*self.args)
 
    def get_result(self):
        threading.Thread.join(self) # 等待线程执行完毕
        try:
            return self.result
        except Exception:
            return None


class GhClient(object):
    def __init__(self, addr, port):
        self.udpaddr = (addr, port)  # 接收方 服务器的ip地址和端口号
        self.udpserver = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        # self.udpserver.bind(self.udpaddr)
        # self.ghVerification = None
    
    def broadcast(self, msg_str):
        LOG.info("向grasshopper 广播数据: %s"%msg_str)
        self.udpserver.sendto(msg_str.encode("utf-8"), self.udpaddr)
        LOG.info("广播结束")
    
    # def receiveData(self):
    #     while True:
    #         data  = self.udpserver.recvfrom(8) 
    #         self.ghVerification = data[0].decode("utf-8")
    #         print(self.ghVerification)
    #         return self.ghVerification
            # print(ghVerification)

    def disconnect(self):
        self.udpserver.close()

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
    
    # @property
    # def is_connect(self):
    #     return self.s.connect
    
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

    def sendRes(self,bufsize=200, ghclient = None, gh_dict =None):
        count = 10 
        flag = -1
        # ghVerification = None
        # LOG.info("机械臂正在运动至指定位置....")
        while count > 0:
            # ipdb.set_trace()
            # print('ghVerification_dic校验码： %s'%ghVerification_dic['ghData'])
            if ghVerification_dic['ghData'] and gh_dict['ghData'] != ghVerification_dic['ghData']:
                gh_dict['ghData'] = ghVerification_dic['ghData']
                LOG.info("接收得到验证码: %s 向PLC发送验证码信息"%gh_dict['ghData'])
                data = gh_dict['ghData']
                self.s.send(data.encode())
            # ghVerification = task.get_result()
            # print("ghVerfication: %s"%ghVerification)
            # if ghVerification:
                
            # _thread.start_new_thread(get_time,())
            # ipdb.set_trace()
            packet = self.s.recv(bufsize)
            if not packet.decode('gbk'):
                continue
            info = struct.unpack("!200s",packet)[0]
            info_str = str(info, encoding = "gbk")
            head1 = info_str[:10].rstrip().lstrip() # 获得前10个字符数据并进行判断
            head2 = info_str[100:110].rstrip().lstrip()
            # ipdb.set_trace()
            if head1 == "errorstart":
                error_index = info_str[10:].rstrip().lstrip()
                error_info = ERROR_DICT[int(error_index)]
                # todo 查找alarm_information
                raise Exception("错误: %s"%(error_info))   # 用于后面捕获异常
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
                flag = -1
            # count -= 1   # 测试用

    def encodeUdpMsg(self,res_list):
        msg = ""
        for res in res_list:
            msg += ",".join([str(i) for i in res])
            msg += ";"
        return msg

def recv_msg(udp_socket,gh_dict):
    """接收数据并显示"""
    while True:
        # 1. 接收数据
        recv_msg = udp_socket.recvfrom(8)
        # 2. 解码
        recv_ip = recv_msg[1]
        recv_msg = recv_msg[0].decode("gbk")  #注意这里的编码如果是windows选择gbk,linux选择utf-8
        # ghVerification = recv_msg
        # if not gh_dict['ghData']:
        #     gh_dict['ghData'] = recv_msg
        # elif gh_dict['ghData'] != recv_msg:
        gh_dict['ghData'] = recv_msg
        LOG.info("Grasshopper information >>>%s:%s" % (str(recv_ip), recv_msg))
        # return recv_msg
    # 3. 显示接收到的数据
        


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--gh-addr','-ga',type=str,default="127.0.0.1")
    parser.add_argument('--gh-port-receive', '-gp_r', type=int, default=8849)
    parser.add_argument('--gh-port-send', '-gp_s', type=int, default=8971)
    parser.add_argument('--plc-addr','-pa', type=str, default="192.168.244.133")
    parser.add_argument('--plc-port','-pp', type=int, default=12346)
    global args
    # global ghVerification
    
    # global ghVerification

    #=========== 变量初始化 ==========================================
    args = vars(parser.parse_args())
    start_time = time.clock() # 程序开始计时
    plc_addr = args['plc_addr']
    plc_port = args['plc_port']
    gh_addr = args['gh_addr']
    gh_port_send = args['gh_port_send']
    gh_port_receive = args['gh_port_receive']

    #=========== 创建日志文件 ==========================================
    rpFolder, logfilePath = create_TempFolder("RobotsPlc")
    LOG = create_logger("RobotsPlc",logfilePath)
    LOG.info("\n %s 上海大界机器人科技有限公司 %s \n  运行红外测试程序...... "%("="*15,"="*15)) 
    LOG.info("PLC ip: %s, port: %s"%(plc_addr, plc_port))
    LOG.info("Grasshopper ip :%s, port receive: %s, port send: %s"%(gh_addr, gh_port_receive, gh_port_send))
    LOG.info("监听程序....")
    

    #=========== 分别声明 plc 和 grasshopper 的地址和端口对象 ============= 
    client = PlcClient(plc_addr, plc_port)
    ghclient = GhClient(gh_addr, gh_port_send)

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 2. 绑定本地信息
    udp_socket.bind((gh_addr, gh_port_receive))
    # t = threading.Thread(target=recv_msg, args=(udp_socket,))
    # t.start()
    ghVerification_dic = {}
    ghVerification_dic['ghData'] = None
    task =MyThread(recv_msg,(udp_socket,ghVerification_dic,))
    task.start()
    

    #=========== 尝试与PLC建立连接 ======================================= 
    try:
        client.connect()
        ERROR_DICT = readText2Dic(os.path.join(rpFolder,"alarm_information.txt"))
    except Exception as e:
        LOG.error("\033[31m !! %s !!\033[0m"%e)

    count  = 2 # 检测到 count 次报错信息之后关闭程序
    #=========== 进入主循环 ==============================================
    ghVerification_dict2 = {}
    ghVerification_dict2['ghData'] = None
    while count > 0:
        try:
            # client.connect()
            client.sendRes(ghclient = ghclient,gh_dict = ghVerification_dict2)
        except socket.timeout:
            pass
            # LOG.info("reconnect")
            # try:
            #     client.connect()
            # except socket.error as se:
            #     pass
                # LOG.error("\033[31m!! %s !!\033[0m"%se)
        except Exception as e:
            LOG.error("\033[31m!! %s !!\033[0m"%e)
            # ghclient.broadcast("None")
        time.sleep(2) # 等待两秒
    client.disconnect()
    ghclient.disconnect()

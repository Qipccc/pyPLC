# encoding: UTF-8
import sys
from datetime import datetime
from threading import *
#sys.path.append('D:\\works\\TestFile')
#print(sys.path)
from EventManager import EventManager,Event
import socket
#事件名称  新文章
EVENT_ARTICAL = "Event_Artical"

#事件源 公众号
class PublicAccounts:
    def __init__(self,eventManager):
        self.__eventManager = eventManager

    def WriteNewArtical(self):
        #事件对象，写了新文章
        event = Event(type_=EVENT_ARTICAL)
        event.dict["artical"] = u'如何写出更优雅的代码\n'
        
        #发送事件
        self.__eventManager.SendEvent(event)
        print(u'公众号发送新文章\n')

#监听器 订阅者
class Listener:
    def __init__(self,username):
        self.__username = username

    #监听器的处理函数 读文章
    def ReadArtical(self,event):
        print(u'%s 收到新文章' % self.__username)
        print(u'正在阅读新文章内容：%s'  % event.dict["artical"])

#udp 监听
class GhClient(object):
    def __init__(self, addr, port):
        self.udpaddr = (addr, port)  # 接收方 服务器的ip地址和端口号
        self.udpserver = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.udpserver.bind(self.udpaddr)
        self.ghVerification = None
    
    def broadcast(self, msg_str):
        print("向grasshopper 广播数据: %s"%msg_str)
        self.udpserver.sendto(msg_str.encode("utf-8"), self.udpaddr)
        print("广播结束")
    
    def receiveData(self):
        # while True:
        data  = self.udpserver.recvfrom(8) 
        self.ghVerification = data[0].decode("utf-8")
        print(self.ghVerification)
        return self.ghVerification
            # print(ghVerification)

    def disconnect(self):
        self.udpserver.close()

"""测试函数"""
#--------------------------------------------------------------------
def test():
    # 实例化监听器
    # listner1 = Listener("thinkroom") #订阅者1
    # listner2 = Listener("steve")     #订阅者2
    gh_port = 8849
    ghclient = GhClient("127.0.0.1", gh_port)
    
    # 实例化事件操作函数
    eventManager = EventManager()
    eventManager.AddEventListener(EVENT_ARTICAL, ghclient.receiveData)

    #绑定事件和监听器响应函数(新文章)
    # eventManager.AddEventListener(EVENT_ARTICAL, listner1.ReadArtical)
    # eventManager.AddEventListener(EVENT_ARTICAL, listner2.ReadArtical)
    # 启动事件管理器,# 启动事件处理线程
    eventManager.Start()

    # publicAcc = PublicAccounts(eventManager)
    # timer = Timer(2, publicAcc.WriteNewArtical)
    # timer.start()

if __name__ == '__main__':
    test()

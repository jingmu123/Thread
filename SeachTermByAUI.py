# coding:utf-8
import sys
sys.path.append("..")
import file_operation as fo
import threading
import datetime
import ctypes
import inspect

#线程锁的实现
#带查找列表
AUI_list=["A0006504","A0026558","A0028920","A0037508","A0042049","A0048405"]
#查找成功的key的列表
move_list = []  #定义一个全局变量，所有线程都可以操作
#定义一个锁
counter_lock = threading.Lock()
#存储获取的结果
aui_term={}


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)

class MyThread(threading.Thread):
    def __init__(self,arg,start_id):
        super(MyThread, self).__init__()#注意：一定要显式的调用父类的初始化函数。
        self.arg=arg
        self.threadName="thread_"+str(self.arg)
        self.start_dicts=start_id

    def run(self):   #定义每个线程要运行的函数
        global AUI_list,move_list,counter_lock,aui_term
        global thread_list
        #定义每个线程需要访问从起始变化开始的4个词典
        for count in range(self.start_dicts,self.start_dicts+4):
            #获取待访问词典名
            if(len(AUI_list) == len(move_list)):
                print("终止线程", self.threadName,file_name)
                stop_thread(thread_list[self.arg])
                #thread_list[self.arg].join()
            file_name="MRAUIST_"+str(count)+".json"
            dicts=fo.loadDict("./data/"+file_name)
            print(self.threadName,"打开了",file_name)
            #访问AUI元素
            for item in AUI_list:
                if(item in dicts.keys()):  #匹配成功
                    if counter_lock.acquire():  #设置锁，用于修改move_list
                        aui_term[item]=dicts[item]
                        print(self.threadName,item,dicts[item])
                        move_list.append(item)
                        counter_lock.release()

strid_list=[0,4,8,12,16,20]
thread_list = []
def test():
    for i in range(6):
        print("start",datetime.datetime.now())
        t =MyThread(i,strid_list[i])
        thread_list.append(t)
        t.start()
test()
print('main thread end!')

while True:
    if(len(AUI_list) == len(move_list)):
        print(aui_term)
        break


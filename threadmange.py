
import select
import threading


def singleton(cls):  
        instances = {}  
        def getinstance():  
            if cls not in instances:  
                instances[cls] = cls()  
            return instances[cls]  
        return getinstance  
     
@singleton    
class MyEpoll:
    __fd_to_socket_info = {}
    __epoll = None
    def __new__(self):
        print("new:", self)
    def __init__(self):
        print("init:", self)
        self.__epoll = select.epoll()
    def add_socket(self, sockid , info = None):
        self.__epoll.register(sockid.fileno(), select.EPOLLIN)
        self.__fd_to_socket_info[sockid.fileno()] = {"socket":sockid, "info":info }
    def my_wait(self, timeout = 1):
        event_ret = {}
        events = self.__epoll.poll(timeout)
        if not events:
            return None;
        for fd, event in events:
           if event & select.EPOLLIN:
               event_ret[fd] = self.__fd_to_socket_info[fd]
        return event_ret



@singleton   
class threadm(threading.Thread):
   def __init__(self, timeout = 1):
       threading.Thread.__init__(self)
       self.mypoll = MyEpoll()
       self.connectList = []
       self.cuCount = 0
       self.timeout = timeout
   def run(self):
        while True:
            evs = self.mypoll.my_wait(self.timeout)
            if evs is None:
               print("Timeout 10")
            else:
               print(evs)
               for fd in evs:
                   print("sock [%s]===> %s"  %(evs[fd]["info"]["msg"], "***"))
                   for conn in self.connectList:
                       conn.run_for_noblocking()

                   
   def add_sock(self, transport):
       self.connectList.append(transport)
       self.mypoll.add_socket(transport.sock, {"transp":transport, "msg":"here is " + str(self.cuCount)})
       self.cuCount = self.cuCount + 1



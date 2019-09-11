import socket
from settings import selenium_sk_ip, selenium_sk_port


class ConnectSelenium(object):

    __flag = None

    # 单例模式
    def __new__(cls, *args, **kwargs):
        if not cls.__flag:
            cls.__flag = super().__new__(cls)
        return cls.__flag

    def __init__(self):
        if 'sk' not in self.__dict__:
            sk = socket.socket()
            sk.connect((selenium_sk_ip, int(selenium_sk_port)))
            self.sk = sk

    def get_sk(self):
        return self.sk


if __name__ == '__main__':
    ip = '127.0.0.1'
    port = 9001
    obj1 = ConnectSelenium()
    obj2 = ConnectSelenium()
    obj3 = ConnectSelenium()
    sk = obj2.get_sk()
    # sk.send(b'123')
    # sk.send(b'456')
    sk.close()

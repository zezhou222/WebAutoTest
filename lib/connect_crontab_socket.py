import socket
from settings import crontab_sk_ip, crontab_sk_port


class ConnectCrontab(object):

    __flag = None

    # 单例模式
    def __new__(cls, *args, **kwargs):
        if not cls.__flag:
            cls.__flag = super().__new__(cls)
        return cls.__flag

    def __init__(self, flag=False):
        if 'sk' not in self.__dict__ or flag:
            sk = socket.socket()
            sk.connect((crontab_sk_ip, int(crontab_sk_port)))
            self.sk = sk

    def get_sk(self):
        return self.sk


if __name__ == '__main__':
    ip = '127.0.0.1'
    port = 9002
    obj1 = ConnectCrontab()
    obj2 = ConnectCrontab()
    obj3 = ConnectCrontab()
    sk = obj2.get_sk()
    # sk.send(b'123')
    # sk.send(b'456')
    sk.close()

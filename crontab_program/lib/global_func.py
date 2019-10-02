import json

from lib.log import Log
from lib.connect_selenim_socket import ConnectSelenium


def get_logger():
    return Log().return_logger()


# 给selenium的程序发送字典数据
def send_to_selenium(data, conn_flag=False):
    if not conn_flag:
        obj = ConnectSelenium(conn_flag)
        sk = obj.get_sk()
        sk.send(json.dumps(data).encode('utf-8'))
    else:
        ConnectSelenium(conn_flag)

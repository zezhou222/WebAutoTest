import json
import struct

from lib.log import Log
from lib.connect_selenim_socket import ConnectSelenium
from lib.connect_mysql import ConnectMysql
from lib.connect_redis import ConnectRedis
from conf.settings import execute_data_key_name


def get_logger():
    return Log().return_logger()


# 解决黏包
def send_content(conn, cont):
    # 把消息转成bytes类型
    cont_b = json.dumps(cont).encode('utf-8')
    # 得到bytes类型消息的长度
    cont_len = len(cont_b)
    # 将消息长度转成4字节的bytes类型
    cont_len_b = struct.pack('i', cont_len)
    # 发送bytes类型长度
    conn.send(cont_len_b)
    # 发送bytes类型消息
    conn.send(cont_b)


# 给selenium的程序发送字典数据
def send_to_selenium(data, conn_flag=False):
    if not conn_flag:
        obj = ConnectSelenium(conn_flag)
        sk = obj.get_sk()
        send_content(sk, data)
    else:
        ConnectSelenium(conn_flag)


def send_to_redis(data):
    obj = ConnectRedis()
    cursor = obj.get_cursor()
    ret = cursor.lpush(execute_data_key_name, json.dumps(data))
    return ret


# 获取数据库的操作光标
def get_cursor():
    obj = ConnectMysql()
    return obj.get_cursor()


# 提交数据，数据写入数据库中
def commit_data():
    obj = ConnectMysql()
    obj.commit_data()




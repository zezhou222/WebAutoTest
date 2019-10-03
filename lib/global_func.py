import json
import hashlib
import random
import struct
import time
from uuid import uuid4

from sqlalchemy.orm import sessionmaker
from create_table import engine
from lib.connect_selenim_socket import ConnectSelenium
from lib.connect_crontab_socket import ConnectCrontab


# 生成MD5的密码
def get_md5(username, password):
    md5 = hashlib.md5(username.encode('utf-8'))
    md5.update(password.encode('utf-8'))
    return md5.hexdigest()


# 获取数据库的操作句柄
def get_db():
    # 创建了那个库的会话窗口
    sql_session = sessionmaker(engine)
    # 打开会话窗口
    db = sql_session()
    return db


# 保存数据
def save_data_to_db(db, objs):
    """
    保存数据至数据库
    :param db: 数据库的句柄
    :param objs: 数据列表
    :return:
    """
    try:
        db.add_all(objs)
        # db.flush()
        db.commit()
    except Exception as e:
        print('数据库保存操作执行有误:', e)
        db.rollback()
    db.close()


# 删除数据
def del_db_data(db, objs):
    ret = 0
    try:
        ret = objs.delete()
        # 删除操作需要commit才能作用到数据库
        db.commit()
    except Exception as e:
        print('数据库删除操作执行有误:', e)
        db.rollback()
    db.close()
    # 返回删除的数量
    return ret


# 解决黏包
def _send_content(sk, cont):
    # 把消息转成bytes类型
    cont_b = json.dumps(cont).encode('utf-8')
    # 得到bytes类型消息的长度
    cont_len = len(cont_b)
    # 将消息长度转成4字节的bytes类型
    cont_len_b = struct.pack('i', cont_len)
    # 发送bytes类型长度
    sk.send(cont_len_b)
    # 发送bytes类型消息
    sk.send(cont_b)


# 给selenium的程序发送字典数据
def send_to_selenium(data, conn_flag=False):
    if not conn_flag:
        obj = ConnectSelenium(conn_flag)
        sk = obj.get_sk()
        _send_content(sk, data)
        # sk.send(json.dumps(data).encode('utf-8'))
    else:
        ConnectSelenium(conn_flag)


# 给crontab的程序发送字典数据
def send_to_crontab(data, conn_flag=False):
    if not conn_flag:
        obj = ConnectCrontab(conn_flag)
        sk = obj.get_sk()
        _send_content(sk, data)
        # sk.send(json.dumps(data).encode('utf-8'))
    else:
        ConnectCrontab(conn_flag)


def get_sk(params_type='crontab'):
    if params_type == 'crontab':
        obj = ConnectCrontab(False)
    elif params_type == 'selenium':
        obj = ConnectSelenium(False)

    sk = obj.get_sk()
    return sk


# 接收数据
def recv_content(conn):
    # 先取4个字节内容得到消息长度的bytes类型
    msg_len_b = conn.recv(4)
    # 把这4个字节内容转换成整型，得到消息的长度
    # 转换后是一个元祖类型，取第一个元素
    msg_len = struct.unpack('i', msg_len_b)[0]
    # 以得到的消息长度接收内容
    msg = conn.recv(msg_len)
    return json.loads(msg.decode('utf-8'))


# 生成随机验证码
def make_random_code():
    # 验证码取值列表
    random_list = [str(i) for i in range(0, 10)]  # 数字
    random_list += [chr(i) for i in range(97, 123)]  # 小写字母
    random_list += [chr(i) for i in range(65, 91)]  # 大写字母
    return ''.join(random.choices(k=6, population=random_list))


# 获取一个随机文件名
def get_random_filename():
    md5 = hashlib.md5(str(time.time()).encode('utf-8'))
    md5.update(str(uuid4()).encode('utf-8'))
    return md5.hexdigest() + '.png'


def get_logger():
    from run_web import main_app
    return main_app.logger


if __name__ == '__main__':
    print(make_random_code())

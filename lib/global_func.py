import json
import hashlib
import random
import time
from uuid import uuid4

from sqlalchemy.orm import sessionmaker
from create_table import engine
from lib.connect_selenim_socket import ConnectSelenium


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


# 给selenium的程序发送字典数据
def send_to_selenium(data):
    obj = ConnectSelenium()
    sk = obj.get_sk()
    sk.send(json.dumps(data).encode('utf-8'))


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


if __name__ == '__main__':
    print(make_random_code())

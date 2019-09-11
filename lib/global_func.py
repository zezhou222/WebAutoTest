import json
import hashlib
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
    db.add_all(objs)
    db.flush()
    db.commit()
    # db.close()


# 删除数据
def del_db_data(db, objs):
    ret = objs.delete()
    # 删除操作需要commit才能作用到数据库
    db.commit()
    # db.close()
    # 返回删除的数量
    return ret


# 给selenium的程序发送字典数据
def send_to_selenium(data):
    obj = ConnectSelenium()
    sk = obj.get_sk()
    sk.send(json.dumps(data).encode('utf-8'))

import hashlib
import xlrd

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from lib.models import (Model, Role, Userinfo)
from settings import (mysql_user, mysql_password, mysql_hostname, mysql_port, database_name, mysql_charset)


# 生成MD5的密码
def get_md5(username, password):
    md5 = hashlib.md5(username.encode('utf-8'))
    md5.update(password.encode('utf-8'))
    return md5.hexdigest()


def init_data():
    # 创建了那个库的会话窗口
    sql_session = sessionmaker(engine)
    db = sql_session()
    # 添加管理员
    db.add_all([Role(role_name='admin'), Role(role_name='staff')])
    db.flush()
    data = Userinfo(username='admin', password=get_md5('admin', 'admin'), email='523198313@qq.com', u2r=[db.query(Role).filter(Role.role_name == 'admin').first()])
    db.add(data)
    db.commit()
    db.close()


def read_excel_write_database(filepath):
    from lib.models import Use_case_step
    # 创建了那个库的会话窗口
    sql_session = sessionmaker(engine)
    db_session = sql_session()
    # 获取excel句柄
    workbook = xlrd.open_workbook(filepath)
    sheet = workbook.sheet_by_index(0)
    data_objs = []
    # 遍历excel数据添加到一个列表中
    for index in range(1, sheet.nrows):
        # 取excel中的数据
        step_method_name, step_name, step_length, step_case = sheet.row_values(index)
        # 实例对象
        obj = Use_case_step(step_method_name=step_method_name, step_name=step_name, step_length=step_length, step_case=step_case)
        data_objs.append(obj)
    # 数据添加至数据库中
    db_session.add_all(data_objs)
    db_session.commit()
    db_session.close()


# 注：操作的库需要手动先创建好
engine = create_engine("mysql+pymysql://%s:%s@%s:%s/%s?charset=%s" % (mysql_user, mysql_password, mysql_hostname, mysql_port, database_name, mysql_charset))

# 由于在导入该文件时候会执行一遍，所以把创表的放在main中
if __name__ == '__main__':
    # 删表
    Model.metadata.drop_all(engine)
    # 建表,在engine指向的库建表
    Model.metadata.create_all(engine)
    # 读取excel表初始化数据库数据
    read_excel_write_database(filepath=r'use_case_step.xlsx')
    # 初始化一个管理员用户
    init_data()

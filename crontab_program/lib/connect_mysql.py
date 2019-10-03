import pymysql
from conf.settings import (mysql_host, mysql_port, mysql_user, mysql_pwd, connect_to_db, db_charset)


class ConnectMysql(object):

    __flag = None

    # 单例模式
    def __new__(cls, *args, **kwargs):
        if not cls.__flag:
            cls.__flag = super().__new__(cls)
        return cls.__flag

    def __init__(self):
        if 'cursor' not in self.__dict__:
            # print('实例')
            mysql_conn = pymysql.connect(host=mysql_host, user=mysql_user, passwd=mysql_pwd, port=mysql_port, db=connect_to_db, charset=db_charset)
            # 指定参数表示返回字典结果的数据
            cursor = mysql_conn.cursor(cursor=pymysql.cursors.DictCursor)
            self.mysql_conn = mysql_conn
            self.cursor = cursor

    def get_cursor(self):
        return self.cursor

    def commit_data(self):
        self.mysql_conn.commit()


if __name__ == '__main__':
    obj1 = ConnectMysql()
    obj2 = ConnectMysql()
    cursor = obj1.get_cursor()

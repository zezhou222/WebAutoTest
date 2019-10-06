from redis import Redis
from settings import (
    redis_host,
    redis_port,
    redis_db,
    redis_password
)


class ConnectRedis(object):

    __flag = None

    # 单例模式
    def __new__(cls, *args, **kwargs):
        if not cls.__flag:
            cls.__flag = super().__new__(cls)
        return cls.__flag

    def __init__(self):
        if 'cursor' not in self.__dict__:
            redis_conn = Redis(host=redis_host, port=redis_port, db=redis_db, password=redis_password)
            self.cursor = redis_conn

    def get_cursor(self):
        return self.cursor


if __name__ == '__main__':
    obj1 = ConnectRedis()
    obj2 = ConnectRedis()
    cursor = obj1.get_cursor()
    print(obj1)
    print(obj2)

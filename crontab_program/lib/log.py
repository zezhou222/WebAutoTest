import logging
import os
from conf.settings import (
    log_path,
    log_level,
)

# 日志储存的文件名
# 先判断是否存在，不存在则创建日志文件(自动创建的)
# if not os.path.exists(log_path):
#     f = open(log_path, mode='w', encoding='utf-8')
#     f.close()

log_path = log_path

if log_level.upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
    log_level = log_level.upper()
else:
    print('日志级别有误，默认设置为DBUUG！%s' % log_level)
    log_level = 'DEBUG'


# 单例模式
class Log(object):
    __flag = None

    def __new__(cls, *args, **kwargs):
        if not cls.__flag:
            cls.__flag = super().__new__(cls)
        return cls.__flag

    def __init__(self):
        if 'logger' not in self.__dict__:
            logger = logging.getLogger()
            logger.setLevel(level=log_level)
            filehandle = logging.FileHandler(log_path, encoding='utf-8')
            streamhandle = logging.StreamHandler()
            logger.addHandler(filehandle)
            logger.addHandler(streamhandle)
            # format = logging.Formatter('%(asctime)s:%(levelname)s:%(lineno)s >>> %(message)s')
            format = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s-%(lineno)s: %(message)s')
            filehandle.setFormatter(format)
            streamhandle.setFormatter(format)

            self.logger = logger

    def return_logger(self):
        return self.logger


def get_logger():
    return Log().return_logger()


if __name__ == '__main__':
    log_path = '../temp/temp.txt'

    logger = get_logger()
    logger.debug('test222')
    logger.debug('test333')
    logger.debug('test333')

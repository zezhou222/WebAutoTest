import time
import hashlib
from uuid import uuid4
from aip import AipOcr
from lib.connect_mysql import ConnectMysql


# 获取数据库的操作光标
def get_cursor():
    obj = ConnectMysql()
    return obj.get_cursor()


# 提交数据，数据写入数据库中
def commit_data():
    obj = ConnectMysql()
    obj.commit_data()


# 获取一个随机截图文件名
def get_screen_shot_filename():
    md5 = hashlib.md5(str(time.time()).encode('utf-8'))
    md5.update(str(uuid4()).encode('utf-8'))
    return md5.hexdigest() + '.png'


def _get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


# 调用百度图片识别
def baidu_discern(filename):
    """ 你的 APPID AK SK """
    APP_ID = '16952993'
    API_KEY = 'X3xlMklHLVeEFiX0IF9imbXG'
    SECRET_KEY = 'BYqrEnfp9EGVml51DhGUYfqRBjr8SjjP'

    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    image = _get_file_content(filename)

    """ 调用网络图片文字识别, 图片参数为本地图片 """
    ret = client.webImage(image)
    words = ret.get('words_result')
    if words:
        return ''.join(words[0]['words'].split(' '))
    else:
        return ''


if __name__ == '__main__':
    ret = baidu_discern('../code.png')
    print(ret)

import socketserver
import json
import struct

from lib.global_func import (
    get_logger,
)
from core.myscheduler import MyScheduler
from lib.global_func import get_cursor


# 日志对象
logger = get_logger()


class CrontabServer(socketserver.BaseRequestHandler):

    def recv_content(self, conn):
        # 先取4个字节内容得到消息长度的bytes类型
        msg_len_b = conn.recv(4)
        # 把这4个字节内容转换成整型，得到消息的长度
        # 转换后是一个元祖类型，取第一个元素
        msg_len = struct.unpack('i', msg_len_b)[0]
        # 以得到的消息长度接收内容
        msg = conn.recv(msg_len)
        # print(msg.decode('utf-8'))
        return json.loads(msg.decode('utf-8'))

    def handle(self):
        conn = self.request   # 客户端的通道
        addr = self.client_address   # 客户端的地址
        logger.info('%s %s' % (addr, '连接--'))
        while 1:
            # 接收内容
            try:
                content = self.recv_content(conn)
            except ConnectionResetError:
                break

            if content == b'':
                break

            # 执行操作方法
            logger.debug('接收的数据: %s' % content)

            opt = content.get('opt')
            
            obj = MyScheduler()
            obj.cursor = get_cursor()
            # 发送数据的准备
            obj.conn = conn

            if hasattr(obj, opt):
                # 调用操作
                getattr(obj, opt)(content.get('data'))
            else:
                break

        logger.info("%s %s" % (addr, '断开连接--'))
        conn.close()


def run():
    print('crontab server start.')
    server = socketserver.ThreadingTCPServer(('0.0.0.0', 9002), CrontabServer)
    server.serve_forever()


if __name__ == '__main__':
    run()

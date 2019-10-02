import socketserver
import json
from lib.global_func import (
    get_logger,
)
from core.myscheduler import MyScheduler


# 日志对象
logger = get_logger()


class CrontabServer(socketserver.BaseRequestHandler):

    def handle(self):
        conn = self.request   # 客户端的通道
        addr = self.client_address   # 客户端的地址
        logger.info('%s %s' % (addr, '连接--'))
        while 1:
            # 接收内容
            try:
                content = conn.recv(1024)
            except ConnectionResetError:
                break

            if content == b'':
                break

            logger.debug('接收的数据: %s' % content)
            # 执行操作方法
            content = json.loads(content.decode('utf-8'))
            opt = content.get('opt')
            if hasattr(self, opt):
                # 调用操作
                obj = MyScheduler()
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

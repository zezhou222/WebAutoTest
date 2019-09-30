import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from lib.log import get_logger

logger = get_logger()


class MyEmail(object):

    def __init__(self, sender, receiver, username, password, smtp_server='smtp.qq.com'):
        self.sender = sender
        self.receiver = receiver
        self.username = username
        self.password = password  # 邮箱开启POP3和SMTP服务的授权码
        self.smtp_server = smtp_server

        # 连接服务器
        self.connect_server()

    # 表示一封邮件，需要邮件主题
    def create_email(self, mail_title):
        self.mail_title = mail_title
        # 创建一个带附件的实例
        message = MIMEMultipart()
        message['From'] = self.sender
        message['To'] = self.receiver
        message['Subject'] = Header(mail_title, 'utf-8')
        self.message = message

    # 附件内容，如文本文件，图片文件等
    def email_appendix(self, file_path):
        att1 = MIMEText(open(file_path, 'rb').read(), 'base64', 'utf-8')
        # 指定头部信息
        att1["Content-Type"] = 'application/octet-stream'  # 内容为二进制流
        att1["Content-Disposition"] = 'attachment; filename="%s"' % (os.path.basename(file_path))
        self.message.attach(att1)

    def email_text(self, content, content_type='plain'):
        # 邮件正文内容
        # self.message.attach(MIMEText(content, 'plain', 'utf-8'))
        self.message.attach(MIMEText(content, content_type, 'utf-8'))

    def connect_server(self):
        # 连接邮件服务器
        smtpObj = smtplib.SMTP_SSL()
        # 注意：如果遇到发送失败的情况（提示远程主机拒接连接），这里要使用SMTP_SSL方法
        smtpObj.connect(self.smtp_server)
        try:
            # 连接qq邮箱服务器
            smtpObj.login(self.username, self.password)
            # 给qq邮箱发送用户名和授权码，进行验证，如果账号没有授权会返回smtplib.SMTPAuthenticationError
        except smtplib.SMTPAuthenticationError:
            logger.error('连接邮件服务器--请检查用户名和授权码是否添加正确！')
            return
        else:
            self.smtpObj = smtpObj

    def send_mail(self):
        self.smtpObj.sendmail(self.sender, self.receiver, self.message.as_string())  # 发送一封邮件
        logger.debug("(%s) 邮件发送成功！！！" % self.mail_title)

    def __del__(self):
        self.smtpObj.close()
        # self.smtpObj.quit()


if __name__ == '__main__':
    obj = MyEmail(sender='523198313@qq.com', receiver='1776070250@qq.com', username='523198313', password='ycfnekkursixcaif')
    obj.create_email('test')
    obj.email_text('<a style="color:red;" href="https://www.baidu.com">百度一下</a>', content_type='html')
    obj.send_mail()

import os

# 项目路径
project_path = os.getcwd()

# mysql数据库的配置
database_name = "auto_test"
mysql_user = "root"
mysql_password = "wzz123"
mysql_hostname = "localhost"
mysql_port = "3306"
mysql_charset = "utf8"

# selenium的socket的ip和端口
selenium_sk_ip = '127.0.0.1'
selenium_sk_port = 9001

# 截图存储的文件夹路径，需要和selenium的一致
screen_shot_path = os.path.join(project_path, 'static', 'screen_shot')

# 发送邮件的配置
sender = '523198313@qq.com'
sender_username = '523198313'
sender_password = 'ycfnekkursixcaif'

# 临时文件夹路径
temp_path = os.path.join(project_path, 'temp')

# web日志路径
web_log_path = os.path.join(project_path, 'temp', 'web_log.txt')
# 日志级别
# 级别：debug, info, warning, error, critical
web_log_level = 'debug'

# crontab的socket的ip和端口
crontab_sk_ip = '127.0.0.1'
crontab_sk_port = 9002

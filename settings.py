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

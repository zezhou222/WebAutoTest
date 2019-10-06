import os

# 项目路径
project_path = os.getcwd()

# mysql数据库的连接配置
mysql_host = '127.0.0.1'
mysql_port = 3306
mysql_user = 'root'
mysql_pwd = 'wzz123'
connect_to_db = 'auto_test'
db_charset = 'utf8'

# mongodb数据库的连接配置
mongodb_host = '127.0.0.1'
mongodb_port = 27017
mongodb_database = 'test'
mongodb_job_table = 'jobs'

# Redis数据库的连接配置
redis_host = '192.168.1.100'
redis_port = 6379
redis_db = 1
redis_password = 'wzz123'
execute_data_key_name = 'execute_data'

# selenium的socket的ip和端口
selenium_sk_ip = '127.0.0.1'
selenium_sk_port = 9001

# 日志路径
log_path = os.path.join(project_path, 'temp', 'crontab_log.txt')
# 日志级别
# 级别：debug, info, warning, error, critical
log_level = 'debug'




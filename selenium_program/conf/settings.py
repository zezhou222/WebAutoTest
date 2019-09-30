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

# selenium执行开启的线程数(最大：CPU个数 * 5)
# 开几个线程也表示了能同时执行几个用例
thread_count = 5

# 执行用例结果的模板页面路径
step_result_template_path = os.path.join(project_path, 'file', 'step_result.html')
# 接口测试结果的模板页面路径
inteface_test_template_path = os.path.join(project_path, 'file', 'interface_test_result.html')

# 发送邮件的配置
sender = '523198313@qq.com'
sender_username = '523198313'
sender_password = 'ycfnekkursixcaif'

# 截图存放的文件夹路径
screen_shot_path = os.path.join(os.path.dirname(project_path), 'static', 'screen_shot')

# 查找标签相关的
find_ele_timeout_time = 5
find_ele_per_second = 0.5

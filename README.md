## Web自动化测试

**目的：**
通过web的形式将操作转换成selenium操作去执行
### 项目功能：
1. 关于用例		
	- 添加用例
	- 编辑用例
	- 显示用例
	- 删除用例
	- 执行用例

2. 关于用例执行结果
	- 显示用例执行结果
	- 删除用例执行结果
	- 显示用例步骤执行的详情结果
	- 显示用例步骤执行的截图

3. 用例可重用，分公共和私有用例

4. 用例执行后发送执行报告至用户的邮箱 

5. 定时执行用例(待做)


### 表结构：

![](https://i.imgur.com/OErI72S.png)


### Web端效果(图片形式)：
![添加公共用例](https://i.imgur.com/uoHKLi0.png "添加公共用例")
![添加普通用例-使用公共用例](https://i.imgur.com/vvDPJ9x.png)
![显示用例](https://i.imgur.com/YwvD14s.png)
![用例执行结果](https://i.imgur.com/kCKmKYb.png)
![步骤的执行详情](https://i.imgur.com/0UkSDrL.png)
![查看截图](https://i.imgur.com/XRpHVVV.png)
![用例的执行报告-发送到QQ邮箱的](https://i.imgur.com/c4AYpIa.png)

### 启动项目:

- 项目环境
	1. python 3.6以上
	2. mysql 5.6以上

- 启动步骤
	1. 安装项目需要的模块(最好在虚拟环境中安装)
		
		注: 由于我没在虚拟环境中，所以提供的模块文件里的内容比较多.

		pip install -r requirements.txt

	2. 创建mysql库

		create database auto_test;
	3. 修改web的settings.py文件(修改连接数据库的用户名及密码)
	4. 修改selenium_program/conf.settings.py文件(连接数据库的用户名及密码，连接的库，发送邮件的账户)
	5. 运行create_table.py文件，创建mysql表
	6. 启动数据库
	7. 启动执行selenium的程序(selenium_program/run_selenium.py)
	8. 启动web端(./run_web.py)
	9. 访问首页http:127.0.0.1:9000/index/
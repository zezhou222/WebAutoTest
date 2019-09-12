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

5. 通过excel文件导入用例数据

6. 定时执行用例(待做)

### 整体设计：

	前端：有部分内容还是模板渲染，在return_page.py文件只是返回页面的url的视图函数可以挂在nginx做返回
	
	后端：用的python的flask框架，默认9000端口启动
	
	执行selenium操作的程序：用的socketserver做服务端接收后端发来的数据，通过反射执行selenium的操作，默认9001端口启动
	
	数据库：用的mysql
	
	注：这个项目可以在一台机器上跑，也可在多台机器上跑


### 表结构：

![](https://i.imgur.com/OErI72S.png)


#### 表介绍：
1.	用例表(use_case)
	
	字段：id,name,type, desc,send\_report,user\_id

	关联：
	
	（1）user_id字段多对一关联至userinfo表的id字段(表示这个用例是哪个用户创建的)

2.	用例的执行结果表(use\_case\_result)

	字段：id,status,execute\_time,end\_time,use\_case\_id,user\_id,screen\_shot\_flag

	关联：
	
	(1)	use_case_id字段多对一关联至use_case表的id字段(表示用例的结果是哪个用例的)

	(2)	user_id字段多对一关联至userinfo表的id字段(表示是谁执行的这个用例，因为用例分公用和私有的，所有人都可以执行公用的，并拿到执行结果)

3.	用户表(userinfo)
	
	字段：id,username,password,email,create\_time,send\_mail

4.	步骤表(use\_case\_step)

	字段：id,step\_method\_name,step\_name,step\_length,step\_case

5.	用例的步骤表(step_detail)

	字段：id,uc_id ,params,execute


6.	用例结果及步骤对应的表(result_step)

	字段：id,uc\_result\_id,step\_id,status,error\_info,parent_step\_id,run\_time,screen\_shot


	关联：


	(1) uc_result_id多对一关联use\_case\_result表的id字段(表示是那一用例结果的小步骤结果)

	(2)	step_id多对一关联steo\_detail表的id字段(表示是哪小步骤的执行结果)

	(3)	parent_step_id多对一关联step\_detail表的id字段(表示公共用例执行的是哪一步骤)



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
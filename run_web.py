import re
from flask_cors import CORS
from flask import (Flask, request, session, redirect)
from Blueprint import (test_case, return_page, login_register, use_case_result, use_case_data)
from lib.connect_selenim_socket import ConnectSelenium


app = Flask(import_name=__name__)
# 解决跨域
CORS(app)
# 热重启，修改内容自重启
app.config["DEBUG"] = True
# Form认证需要
app.config["CSRF_ENABLED"] = True
app.config["SECRET_KEY"] = '123456'

# 添加蓝图

# 返回页面的
app.register_blueprint(return_page.app)
# 用例操作相关的
app.register_blueprint(test_case.app)
# 登陆注册的
app.register_blueprint(login_register.app)
# 用例结果相关得
app.register_blueprint(use_case_result.app)
# 导入用例数据的
app.register_blueprint(use_case_data.app)


# 简单的请求中间件
@app.before_request
def login_check():
    white_list = ['/login/$', '/register/$', '/user_register/$', '/user_login/$', '/static/.+', '/favicon.ico', '/forget_password/$', '/send_forget_pwd_email/$', '/reset_pwd/$']
    for rule in white_list:
        ret = re.match(rule, request.path)
        if ret:
            return None

    # 其他路径，检查session
    # 如果没有session，就跳转至登陆界面
    if not session.get('login_user', None):
        # 记录用户要去的url，并重定向至登陆界面
        session['request_url'] = request.path
        return redirect('/login/')

    # 如果有request_url，就让其跳转他之前要去的界面
    if session.get('request_url'):
        jump_url = session.pop('request_url')
        # print(session, jump_url)
        return redirect(jump_url)


if __name__ == '__main__':
    try:
        # 通过socket连接Selenium
        ConnectSelenium()
    except ConnectionRefusedError as e:
        print(e)
        print('请先启动执行selenium的程序。')
    else:
        # 运行web
        app.run(host="0.0.0.0", port=9000)

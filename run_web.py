from flask_cors import CORS
from flask import Flask
from logging.config import dictConfig
from settings import web_log_level, web_log_path

if web_log_level.upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
    web_log_level = web_log_level.upper()
else:
    print('日志级别有误，默认设置为DBUUG！%s' % web_log_level)
    web_log_level = 'DEBUG'

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s-%(lineno)s: %(message)s',
    }},
    'handlers': {
        'filehandler': {
            'class': 'logging.FileHandler',
            'filename': web_log_path,
            'encoding': 'utf-8',
            'formatter': 'default'
         },
        'streamhandler': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        }
    },
    'root': {
        'level': web_log_level,
        'handlers': ['filehandler', 'streamhandler']
    }
})

main_app = Flask(import_name=__name__)

# 由于循环导入的问题，所以有些只能在main中写
if __name__ == '__main__':
    import re
    from flask import (request, session, redirect)
    from Blueprint import (test_case, return_page, login_register, use_case_result, use_case_data, project, interface_test, crontab)
    from lib.connect_selenim_socket import ConnectSelenium
    from lib.connect_crontab_socket import ConnectCrontab

    # 解决跨域
    CORS(main_app)
    # 热重启，修改内容自重启
    # 当DEBUG模式开启，日志级别会强行变成debug最低级别
    main_app.config["DEBUG"] = True
    # Form认证需要
    main_app.config["CSRF_ENABLED"] = True
    main_app.config["SECRET_KEY"] = '123456'

    # 添加蓝图

    # 返回页面的
    main_app.register_blueprint(return_page.app)
    # 用例操作相关的
    main_app.register_blueprint(test_case.app)
    # 登陆注册的
    main_app.register_blueprint(login_register.app)
    # 用例结果相关得
    main_app.register_blueprint(use_case_result.app)
    # 导入用例数据的
    main_app.register_blueprint(use_case_data.app)
    # 后台--项目的
    main_app.register_blueprint(project.app)
    # 接口测试相关的
    main_app.register_blueprint(interface_test.interface_test_app)
    # 定时任务的
    main_app.register_blueprint(crontab.app)

    # 简单的请求中间件
    # @app.before_request
    # def login_check():
    #     white_list = ['/login/$', '/register/$', '/user_register/$', '/user_login/$', '/static/.+', '/favicon.ico', '/forget_password/$', '/send_forget_pwd_email/$', '/reset_pwd/$']
    #     for rule in white_list:
    #         ret = re.match(rule, request.path)
    #         if ret:
    #             return None
    #
    #     # 其他路径，检查session
    #     # 如果没有session，就跳转至登陆界面
    #     if not session.get('login_user', None):
    #         # 记录用户要去的url，并重定向至登陆界面
    #         session['request_url'] = request.path
    #         return redirect('/login/')
    #
    #     # 如果有request_url，就让其跳转他之前要去的界面
    #     if session.get('request_url'):
    #         jump_url = session.pop('request_url')
    #         # print(session, jump_url)
    #         return redirect(jump_url)

    logger = main_app.logger
    try:
        ConnectCrontab()
    except ConnectionRefusedError as e:
        logger.error(e)
        logger.error('请先启动好执行程序。')
    else:
        # 运行web
        main_app.run(host="0.0.0.0", port=9000)

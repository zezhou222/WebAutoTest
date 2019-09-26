from flask import (Blueprint, request, session, jsonify, make_response)
from lib.global_func import (get_md5, get_db, save_data_to_db, make_random_code)
from lib.models import (Userinfo, Role)
from lib.send_mail import MyEmail
from settings import sender, sender_username, sender_password

app = Blueprint(name='login_register', import_name=__name__)


def check_username_exists(username):
    flag = False
    db = get_db()
    obj = db.query(Userinfo).filter(Userinfo.username == username).first()
    if obj:
        flag = True
    return flag


@app.route(rule='/user_register/', methods=['post'])
def register():
    ret = {'flag': 0}
    # 获取数据
    data = request.form.to_dict()
    username = data.get('username')

    # 验证数据
    # 验证用户名是否存在
    flag = check_username_exists(data.get('username'))
    if flag:
        ret = {'flag': 1, 'error_info': '%s already registered.' % username}
        return jsonify(ret)

    # 保存数据
    db = get_db()
    data["password"] = get_md5(data["username"], data["password"])

    # 保存数据至数据库
    save_data_to_db(db, [Userinfo(**data, u2r=[db.query(Role).filter(Role.role_name == 'staff').first()])])

    return jsonify(ret)


@app.route(rule='/user_login/', methods=['post'])
def login():
    ret = {'flag': 0}
    data = request.form.to_dict()

    # 验证数据
    db = get_db()
    username = data.get('username')
    # 进行md5摘要
    password = get_md5(username, data.get('password'))
    # 查询数据
    obj = db.query(Userinfo).filter(Userinfo.username == username, Userinfo.password == password).first()
    if obj:
        # 设置session
        session['user_id'] = obj.id
        session['login_user'] = username
        # 设置cookie
        response = make_response(jsonify(ret))
        response.set_cookie('username', username)
        response.set_cookie('email', obj.email)
        return response

    else:
        ret['flag'] = 1
        ret['error_info'] = 'username or password error.'

    return jsonify(ret)


@app.route(rule='/logout/')
def logout():
    ret = {'flag': 0}
    del session['login_user']
    del session['user_id']
    return jsonify(ret)


@app.route(rule='/alter_password/', methods=['post'])
def alter_pwd():
    ret = {'flag': 0}
    user_id = session.get('user_id')
    username = session.get('login_user')
    data = request.form.to_dict()
    if data.get('new_pwd1') != data.get('new_pwd2'):
        ret['flag'] = 1
        ret['error_info'] = '???'
    else:
        db = get_db()
        # 判断该用户名密码是否正确
        if db.query(Userinfo).filter(Userinfo.username == username, Userinfo.password == get_md5(username, data.get('old_pwd'))).first():
            password = get_md5(username, data.get('new_pwd1'))
            # 更新数据
            db.query(Userinfo).filter(Userinfo.id == user_id).update({'password': password})
            db.commit()
        else:
            ret['flag'] = 2
            ret['error_info'] = 'the password error!'
    return jsonify(ret)


@app.route(rule='/alter_email/', methods=['post'])
def alter_email():
    ret = {'flag': 0}
    user_id = session.get('user_id')
    email = request.form.get('email')
    send_mail = int(request.form.get('send_mail'))
    # 修改邮箱
    db = get_db()
    if email != '':
        db.query(Userinfo).filter(Userinfo.id == user_id).update({'email': email, 'send_mail': send_mail})

        # 修改cookie
        response = make_response(jsonify(ret))
        response.set_cookie('email', email)

        return response

    else:
        db.query(Userinfo).filter(Userinfo.id == user_id).update({'send_mail': send_mail})
    db.commit()

    return jsonify(ret)


@app.route(rule='/send_forget_pwd_email/')
def send_forget_pwd_email():
    ret = {'flag': 0}
    # 查询用户
    db = get_db()
    obj = db.query(Userinfo).filter(Userinfo.username == request.args.get('username')).first()
    if obj is None:
        ret['flag'] = 1
        ret['error_info'] = "the username don't exists!"
        return jsonify(ret)

    # 获取随机验证码
    code = make_random_code()
    # 设置session，用于提交验证
    session['code'] = code
    session['temp_user_id'] = obj.id
    session['temp_username'] = obj.username
    # 发送邮件
    obj = MyEmail(sender=sender, receiver=obj.email, username=sender_username, password=sender_password)
    obj.create_email('来自Web自动化测试平台的验证码.')
    obj.email_text('验证码为：%s' % code)
    obj.send_mail()

    return jsonify(ret)


@app.route(rule='/reset_pwd/', methods=['post'])
def reset_pwd():
    ret = {'flag': 0}
    # 验证验证码
    if session['code'] != request.form.get('code').strip():
        ret['flag'] = 1
        ret['error_info'] = '验证码有误！'
    else:
        new_pwd = get_md5(session.get('temp_username'), request.form.get('new_pwd'))
        # 修改密码
        db = get_db()
        db.query(Userinfo).filter(Userinfo.id == session.get('temp_user_id')).update({'password': new_pwd})
        db.commit()

    return jsonify(ret)

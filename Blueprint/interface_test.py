import json
import requests
from flask import (Blueprint, request, session, render_template, jsonify)
from flask.views import MethodView
from sqlalchemy import or_

from lib.models import (Params, Interface_test, Userinfo, Project, Interface_test_result)
from lib.global_func import (
    get_db,
    send_to_selenium,
    get_logger,
)
from lib.myrequest import MyRequest
from lib.paging import Paging

interface_test_app = Blueprint(name="interface_test", import_name=__name__)
# 日志的
logger = get_logger()


@interface_test_app.route(rule='/api/interface_test/myself/all/')
def get_my_interface_data():
    user_id = session.get('user_id')
    project_id = request.args.get('project_id')
    db = get_db()
    objs = db.query(Interface_test).filter(Interface_test.user_id == user_id, Interface_test.project_id == project_id).all()
    response_data = []
    for obj in objs:
        response_data.append({'id': obj.id, 'data': obj.interface_name})
    logger.debug('自己所有的用例数据: %s' % response_data)

    return jsonify(response_data)


@interface_test_app.route(rule='/api/temp_execute_interface_test/', methods=['post'])
def temp_interface_test():
    data = json.loads(request.data)
    logger.debug('临时执行接口测试数据: %s' % data)
    try:
        obj = MyRequest(data)
        response = obj.start()
        # print(response.status_code)
        if response.status_code == 200:
            return response.content
        elif response.status_code == 405:
            return "request method error.", 406
        elif response.status_code == 500:
            return "please verify params.", 406
        else:
            return "unknow error.", 406
    except requests.exceptions.ReadTimeout:
        return "request timeout.", 406


@interface_test_app.route(rule='/api/execute_interface_test/<int:interface_test_id>/')
def execute_interface_test(interface_test_id=None):
    if interface_test_id == None:
        return {'error': '无效的请求'}, 404

    db = get_db()
    logger = get_logger()
    user_id = session.get('user_id')
    user_obj = db.query(Userinfo).filter(Userinfo.id == user_id).first()
    logger.debug("执行内容：%s, 执行的用户id：%s, 执行的接口测试id：%s" % ('interface_test', user_obj.id, interface_test_id))

    try:
        send_to_selenium({'opt': 'execute_interface_test', 'data': {'interface_test_id': interface_test_id, 'user_id': session.get('user_id')}})
    except ConnectionResetError as error:
        # 让其重新连接，但不再发数据
        send_to_selenium({}, conn_flag=True)
        # 告诉前端这次请求失败
        logger.warning('连接selenium失败. %s' % error)
        return {'error': '执行失败! 请稍后重试.'}, 500

    return {}, 202


@interface_test_app.route(rule='/api/get_interface_test/<int:interface_test_id>/')
def get_interface_test_data(interface_test_id):
    if interface_test_id is None:
        return {'error': 'not found.'}, 404

    db = get_db()
    inter_obj = db.query(Interface_test).filter(Interface_test.id == interface_test_id).first()
    dic = {
        'interface_name': inter_obj.interface_name,
        'interface_type': inter_obj.interface_type,
        'interface_description': inter_obj.interface_description,
        'request_type': inter_obj.request_type,
        'request_url': inter_obj.request_url,
        'request_params': [],
        'header_params': [],
    }
    params_objs = db.query(Params).filter(Params.interface_test_id == interface_test_id).all()
    for obj in params_objs:
        if obj.params_type == 'request':
            dic['request_params'].append({'key': obj.key, 'value': obj.value, 'description': obj.description, 'execute': obj.execute})
        else:
            dic['header_params'].append({'key': obj.key, 'value': obj.value, 'description': obj.description, 'execute': obj.execute})
    # print(dic)
    return dic


class InterfaceTest(MethodView):

    def get(self):
        opt = request.args.get('opt')
        search_content = request.args.get('search_content')

        db = get_db()
        username = session.get('login_user')
        user_obj = db.query(Userinfo).filter(Userinfo.username == username).first()

        # 查询数据，获取数据总数，放置分页器
        if not opt:
            interface_objs = db.query(Interface_test).filter(or_(Interface_test.user_id == user_obj.id, Interface_test.interface_type == 'public'))
        else:
            search_content = '%' + search_content.strip() + '%'
            if opt == 'all':
                interface_objs = db.query(Interface_test).filter(or_(Interface_test.user_id == user_obj.id, Interface_test.interface_type == 'public'), Interface_test.interface_name.like(search_content))
            elif opt == 'project':
                project_objs = db.query(Project).filter(Project.project_name.like(search_content)).all()
                project_ids = []
                for obj in project_objs:
                    project_ids.append(obj.id)
                interface_objs = db.query(Interface_test).filter(Interface_test.project_id.in_(project_ids))
            elif opt == 'public':
                interface_objs = db.query(Interface_test).filter(Interface_test.interface_type == 'public', Interface_test.interface_name.like(search_content))
            elif opt == 'general':
                interface_objs = db.query(Interface_test).filter(Interface_test.user_id == user_obj.id, Interface_test.interface_type == 'general', Interface_test.interface_name.like(search_content))
        # 倒序
        interface_objs = interface_objs.order_by(Interface_test.id.desc())

        data_sum = interface_objs.count()
        page = Paging(request, request.args.get('page', 1), data_sum, show_num=3)

        # 取数据
        interface_objs = interface_objs[page.start: page.end]

        return render_template('interface_test.html', interface_objs=interface_objs, page=page, now_user_id=user_obj.id)

    def post(self):
        interface_test_data = json.loads(request.data)
        request_params = interface_test_data.pop('request_params')
        header_params = interface_test_data.pop('header_params')
        interface_test_data['user_id'] = session.get('user_id')

        # 验证数据,待填

        # 保存数据
        db = get_db()
        try:
            inter_obj = Interface_test(**interface_test_data)
            db.add(inter_obj)
            db.flush()
            temp_obj = []
            for dic in request_params:
                dic['interface_test_id'] = inter_obj.id
                temp_obj.append(Params(**dic))
            for dic in header_params:
                dic['interface_test_id'] = inter_obj.id
                dic['params_type'] = 'header'
                temp_obj.append(Params(**dic))
            db.add_all(temp_obj)
            db.commit()
        except Exception as err:
            # 添加数据出错执行回滚操作
            logger.error('添加接口数据出错: %s' % err)
            db.rollback()
            return {'error': '添加出错！'}, 422

        return {}, 201

    def delete(self):
        interface_test_id = request.form.get('interface_test_id', None)
        if interface_test_id is None:
            return {'error': '请求数据出错.'}, 422

        db = get_db()
        inter_obj = db.query(Interface_test).filter(Interface_test.id == interface_test_id).first()
        if not inter_obj:
            return {'error': '该数据不存在!'}, 410

        try:
            # (1) 删除接口测试结果
            db.query(Interface_test_result).filter(Interface_test_result.interface_test_id == interface_test_id).delete()
            db.commit()
            # (2) 删除接口参数
            db.query(Params).filter(Params.interface_test_id == interface_test_id).delete()
            db.commit()
            # (3) 删除接口测试数据
            db.query(Interface_test).filter(Interface_test.id == interface_test_id).delete()
            db.commit()
        except Exception as error:
            db.rollback()
            logger.error('删除接口测试数据失败: %s' % error)
            return {'error': '删除失败!'}, 500

        return {}, 204

    def put(self):
        interface_test_data = json.loads(request.data)

        logger.debug('接口测试的更新数据提交内容: %s' % interface_test_data)

        edit_interface_test_id = interface_test_data.pop('edit_interface_test_id')
        request_params = interface_test_data.pop('request_params')
        header_params = interface_test_data.pop('header_params')
        interface_test_data['user_id'] = session.get('user_id')

        # 验证数据

        # 更新数据
        db = get_db()
        try:
            # (1) 更新接口测试数据
            db.query(Interface_test).filter(Interface_test.id == edit_interface_test_id).update(interface_test_data)
            # (2) 删除旧的接口参数数据
            db.query(Params).filter(Params.interface_test_id == edit_interface_test_id).delete()
            # (3) 添加新的接口参数数据
            temp_obj = []
            for dic in request_params:
                dic['interface_test_id'] = edit_interface_test_id
                temp_obj.append(Params(**dic))
            for dic in header_params:
                dic['interface_test_id'] = edit_interface_test_id
                dic['params_type'] = 'header'
                temp_obj.append(Params(**dic))
            db.add_all(temp_obj)
            # (4) 提交
            db.commit()
        except Exception as error:
            logger.error('更新接口数据出错: %s' % error)
            db.rollback()
            return {'error': '编辑有误!'}, 500

        return {}, 201


interface_test_app.add_url_rule(rule='/api/interface_test/', endpoint='interface_test', view_func=InterfaceTest.as_view(name='interface_test'))


class InterfaceTestResult(MethodView):

    def get(self, interface_test_id):
        db = get_db()
        inter_obj = db.query(Interface_test).filter(Interface_test.id == interface_test_id).first()

        result_objs = db.query(Interface_test_result).filter(Interface_test_result.interface_test_id == interface_test_id)
        # 倒序
        result_objs = result_objs.order_by(Interface_test_result.id.desc())
        # 分页
        data_sum = result_objs.count()
        page = Paging(request, request.args.get('page', 1), data_sum, show_num=5)

        # 取数据
        result_objs = result_objs[page.start: page.end]

        return render_template('interface_test_result.html', result_objs=result_objs, inter_obj=inter_obj, page=page)

    def delete(self, interface_test_id):
        result_id = interface_test_id
        db = get_db()
        try:
            db.query(Interface_test_result).filter(Interface_test_result.id == result_id).delete()
            db.commit()
        except Exception as error:
            db.rollback()
            logger.error('删除接口测试结果失败：%s' % error)
            return {'error': '删除失败!'}, 500

        return {}, 204


interface_test_app.add_url_rule(rule='/api/interface_test_result/<int:interface_test_id>/', endpoint='interface_test_result', view_func=InterfaceTestResult.as_view(name='interface_test_result'))

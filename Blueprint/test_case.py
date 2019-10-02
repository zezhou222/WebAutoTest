from flask import (Blueprint, request, jsonify, session)
from flask.views import MethodView
from lib.flask_form import UseCaseForm
from sqlalchemy.sql import or_

from lib.models import (Use_case_step, Userinfo, Use_case, Step_detail, Use_case_result, Result_step, Project)
from lib.global_func import (get_db, save_data_to_db, del_db_data, send_to_selenium, get_logger)
from lib.use_case_func import (check_public_uc_name, check_general_uc_name, add_uc_data)


app = Blueprint(name='test_case', import_name=__name__)

logger = get_logger()


@app.route(rule='/get_step_options/')
def get_use_case_step():
    # 获取操作数据库的句柄
    db = get_db()
    # 获取所有的步骤
    objs = db.query(Use_case_step).order_by(Use_case_step.id.asc()).all()
    # 进行格式化
    step_data = {}
    for obj in objs:
        step_data[obj.step_method_name] = {'step_name': obj.step_name, 'step_length': obj.step_length}
    logger.debug('获取步骤选项数据: %s' % step_data)
    return jsonify(step_data)


@app.route(rule='/get_public_use_case/')
def get_public_use_case():
    # 获取操作数据库的句柄
    db = get_db()
    # 获取所有的公共用例
    objs = db.query(Use_case).filter(Use_case.uc_type == 'public').all()
    # 进行格式化
    public_uc_data = []
    for obj in objs:
        public_uc_data.append({"id": obj.id, "use_case_name": obj.name})
    return jsonify(public_uc_data)


@app.route(rule='/api/use_case/myself/all/')
def get_my_use_case():
    user_id = session.get('user_id')
    project_id = request.args.get('project_id')
    db = get_db()
    objs = db.query(Use_case).filter(Use_case.user_id == user_id, Use_case.project_id == project_id).all()
    response_data = []
    for obj in objs:
        response_data.append({'id': obj.id, 'data': obj.name})
    logger.debug('自己所有的用例数据: %s' % response_data)

    return jsonify(response_data)


@app.route(rule='/api/get_execute_step/')
def get_use_case_step_data():
    db = get_db()
    uc_id = request.args.get('use_case_id')
    use_case_obj = db.query(Use_case).filter(Use_case.id == uc_id).first()
    step_objs = db.query(Step_detail).filter(Step_detail.uc_id == uc_id, Step_detail.delete_status == 0).all()
    data = {'name': use_case_obj.name, 'project_id': use_case_obj.project_id, 'uc_type': use_case_obj.uc_type, 'desc': use_case_obj.desc, 'step': []}
    for obj in step_objs:
        data['step'].append(obj.params)

    return jsonify(data)


@app.route(rule='/api/get_project_data/')
def get_project_data():
    db = get_db()
    project_objs = db.query(Project).all()
    data = []
    for obj in project_objs:
        data.append({'id': obj.id, 'project_name': obj.project_name, 'project_description': obj.project_description})

    return jsonify(data)


class TestCase(MethodView):

    # 添加用例
    def post(self):
        ret = {'flag': 0}
        form = UseCaseForm()
        # 判断提交的内容
        if not form.validate_on_submit():
            # 没通过返回错误提示信息
            ret = form.errors
            ret['flag'] = 1
            return jsonify(ret)

        # form认证通过

        db = get_db()
        # 格式化出保存的数据
        data = request.form.to_dict()
        data.pop('csrf_token')
        data['user_id'] = session.get('user_id')

        # 如果是公共用例的检测重名
        flag = check_public_uc_name(data)
        if flag:
            ret['flag'] = 2
            ret['error_info'] = "添加的用例与公共用例重名"
            return jsonify(ret)

        # 如果是自己的用例重名
        # flag = check_general_uc_name(data)
        # if flag:
        #     ret['flag'] = 3
        #     ret['error_info'] = "已有该用例名称"
        #     return jsonify(ret)

        # 添加用例数据
        add_uc_data(data)

        return jsonify(ret)

    def delete(self):
        ret = {'flag': 0}

        # 获取用例id
        uc_id = request.form.get('use_case_id')
        db = get_db()
        # 删除用例逻辑，由于sqlalchemy没有级联删除，只能从没有建立外键的表删起来

        # 1. 先找出用例的步骤详情
        step_obj = db.query(Step_detail).filter(Step_detail.uc_id == uc_id).all()
        step_detail_id = [obj.id for obj in step_obj]
        # 2. 通过用例步骤的id去删除步骤执行结果的内容
        db.query(Result_step).filter(or_(Result_step.step_id.in_(step_detail_id), Result_step.parent_step_id.in_(step_detail_id))).delete(synchronize_session=False)
        db.commit()
        # 3. 删除用例步骤和用例执行结果
        del_db_data(db, db.query(Step_detail).filter(Step_detail.uc_id == uc_id))
        del_db_data(db, db.query(Use_case_result).filter(Use_case_result.use_case_id == uc_id))
        # 4. 删除用例
        result = del_db_data(db, db.query(Use_case).filter(Use_case.id == uc_id))
        # 删除会返回，删除了几条符合的结果，如果结果为0表示就没找到这条用例
        if result == 0:
            ret['flag'] = 1
            ret['error_info'] = '删除失败'

        return jsonify(ret)

    def put(self):
        ret = {'flag': 0}
        form = UseCaseForm()
        # 判断提交的内容
        if not form.validate_on_submit():
            # 没通过返回错误提示信息
            ret = form.errors
            ret['flag'] = 1
            return jsonify(ret)

        # form认证通过

        # 查找用户id
        db = get_db()
        # 格式化出保存的数据
        data = request.form.to_dict()
        data.pop('csrf_token')
        edit_id = data.pop('edit_use_case_id')
        # print(data, edit_id)

        # 如果是公共用例的检测重名
        if data['uc_type'] == 'public':
            if check_public_uc_name(data):
                ret['flag'] = 2
                ret['error_info'] = "编辑的用例与公共用例重名"
                return jsonify(ret)

        # 更新数据
        # 1.修改步骤数据（修改步骤表用例的id，由于有关联所以不能删）
        # 修改uc_id
        db.query(Step_detail).filter(Step_detail.uc_id == edit_id).update({'delete_status': 1})
        step_data = []
        # 添加新的步骤数据，进行关联
        for step in data.pop('params').split('||'):
            temp = step.split('@@')
            execute = int(temp[-1])
            step_data.append(Step_detail(uc_id=edit_id, params=step, execute=execute))
        save_data_to_db(db, step_data)

        # 2.修改用例数据
        db.query(Use_case).filter(Use_case.id == edit_id).update(data)
        # 数据保存至硬盘
        db.commit()

        return jsonify(ret)


# 添加路由
app.add_url_rule(rule="/use_case/add/", endpoint="add", view_func=TestCase.as_view(name="add"))
app.add_url_rule(rule="/use_case/del/", endpoint="del", view_func=TestCase.as_view(name="del"))
app.add_url_rule(rule="/use_case/edit/", endpoint="edit", view_func=TestCase.as_view(name="edit"))


# 执行用例的视图
@app.route(rule='/use_case/execute/', methods=['post'])
def execute_use_case():
    ret = {'flag': 0}

    db = get_db()
    user_id = session.get('user_id')
    user_obj = db.query(Userinfo).filter(Userinfo.id == user_id).first()
    to_execute_uc_id = request.form.get('use_case_id')

    logger.debug("执行内容：%s, 执行的用户id：%s, 执行的用例id：%s" % ('use_case_test', user_obj.id, to_execute_uc_id))

    # 要执行的用例，及各种数据发送至selenium端，让其执行用例(web端和执行端拆开)
    try:
        send_to_selenium({'opt': 'execute_use_case', 'data': {'use_case_id': to_execute_uc_id, 'user_id': user_obj.id, 'send_mail': user_obj.send_mail}})
    except ConnectionResetError:
        # 让其重新连接，但不再发数据
        send_to_selenium({}, conn_flag=True)
        # 告诉前端这次请求失败
        ret['flag'] = 1
        ret['error_info'] = "执行失败! 请稍后重试."

    return jsonify(ret)

import json
import hashlib
from flask import (
    Blueprint,
    session,
    request,
    render_template)
from flask.views import MethodView
from sqlalchemy import or_

from lib.global_func import (
    get_db,
    get_logger,
    send_to_crontab,
    recv_content,
    get_sk,
)
from lib.models import (
    Crontab,
    Interface_test,
    Use_case,
    # Userinfo,
    Project
)
from lib.paging import Paging

app = Blueprint(name="crontab", import_name=__name__)
# 日志的
logger = get_logger()


def get_task_id(user, name):
    md5 = hashlib.md5(user.encode('utf-8'))
    md5.update(name.encode('utf-8'))
    return md5.hexdigest()


class CrontabView(MethodView):

    def get(self):
        opt = request.args.get('opt')
        search_content = request.args.get('search_content')

        db = get_db()
        user_id = session.get('user_id')
        # user_obj = db.query(Userinfo).filter(Userinfo.id == user_id).first()

        # 查询数据，获取数据总数，放置分页器
        if not opt:
            crontab_objs = db.query(Crontab).filter(Crontab.user_id == user_id)
        else:
            search_content = '%' + search_content.strip() + '%'
            if opt == 'all':
                crontab_objs = db.query(Crontab).filter(Crontab.user_id == user_id)
            elif opt == 'project':
                project_obj = db.query(Project).filter(Project.project_name.like(search_content)).first()
                crontab_objs = db.query(Crontab).filter(Crontab.user_id == user_id, Crontab.project_id == project_obj.id)
            elif opt == 'task_name':
                crontab_objs = db.query(Crontab).filter(Crontab.user_id == user_id, Crontab.task_name.like(search_content))

        # 倒序
        crontab_objs = crontab_objs.order_by(Crontab.id.desc())

        data_sum = crontab_objs.count()
        page = Paging(request, request.args.get('page', 1), data_sum, show_num=5)

        # 取数据
        crontab_objs = crontab_objs[page.start: page.end]

        # 初始化一下数据
        for obj in crontab_objs:
            if obj.test_type == 'interface_test':
                inter_obj = db.query(Interface_test).filter(Interface_test.id == obj.test_data_id).first()
                obj.test_data = inter_obj.interface_name
            elif obj.test_type == 'use_case':
                usecase_obj = db.query(Use_case).filter(Use_case.id == obj.test_data_id).first()
                obj.test_data = usecase_obj.name

        return render_template('crontab.html', crontab_objs=crontab_objs, page=page, now_user_id=user_id)

    def check_request_data(self, crontab_data):
        db = get_db()
        # 验证名称，是否不为空
        if crontab_data['task_name'].strip() == '':
            return False, {'error': '定时任务名称不能为空'}, 422

        # 验证名称是否重名
        if db.query(Crontab).filter(Crontab.task_name == crontab_data['task_name']).first():
            return False, {'error': '定时任务重名!'}, 422

        # 验证是否有这些测试数据
        if crontab_data['test_type'] == 'interface_test':
            if not db.query(Interface_test).filter(Interface_test.id == crontab_data['test_data_id'], Interface_test.user_id == crontab_data['user_id']).first():
                return False, {'error': '请求数据有误!'}, 422
        elif crontab_data['test_type'] == 'use_case_test':
            if not db.query(Use_case).filter(Use_case.id == crontab_data['test_data_id'], Use_case.user_id == crontab_data['user_id']).first():
                return False, {'error': '请求数据有误!'}, 422

        return True, {}, 200

    def post(self):
        crontab_data = json.loads(request.data)
        crontab_data['user_id'] = session.get('user_id')
        crontab_data['task_id_name'] = get_task_id(session.get('login_user'), crontab_data['task_name'])

        logger.debug('定时任务新增数据: %s' % crontab_data)

        # 验证数据
        flag, ret, code = self.check_request_data(crontab_data)
        if not flag:
            return ret, code

        # 发送数据至定时任务的程序
        try:
            send_to_crontab({'opt': 'add_task', 'data': crontab_data})
        except ConnectionAbortedError as error:
            logger.warning('连接crontab失败. %s' % error)
            # 重连
            send_to_crontab({}, conn_flag=True)
            return {'添加定时任务失败!'}, 500

        # 接收添加任务的结果
        sk = get_sk()
        add_result = recv_content(sk)
        logger.debug('添加任务的返回结果：%s' % add_result)
        if add_result.get('add_flag') != 0:
            return {'error': '添加失败!请核实参数!'}, 422

        # 保存数据
        db = get_db()
        crontab_obj = Crontab(**crontab_data)
        db.add(crontab_obj)
        db.commit()

        # 返回前端响应内容
        return {}, 202

    def delete(self):
        crontab_id = request.form.get('crontab_id')
        logger.debug('删除的任务id: %s' % crontab_id)

        db = get_db()
        obj = db.query(Crontab).filter(Crontab.id == crontab_id).first()

        # 发送crontab程序，删除任务
        try:
            send_to_crontab({'opt': 'del_task', 'data': {'crontab_id': crontab_id, 'task_id': obj.task_id_name}})
        except ConnectionAbortedError as error:
            logger.warning('连接crontab失败. %s' % error)
            # 重连
            send_to_crontab({}, conn_flag=True)
            return {'删除任务失败!'}, 500

        # 接收删除任务的结果
        sk = get_sk()
        del_result = recv_content(sk)
        logger.debug('添加任务的返回结果：%s' % del_result)
        if del_result.get('del_flag') != 0:
            return {'error': '删除任务失败!'}, 500

        # 删除表数据
        db.query(Crontab).filter(Crontab.id == crontab_id).delete()
        db.commit()

        return {}, 204

    def put(self):
        pass


app.add_url_rule(rule='/api/crontab/', endpoint='crontab', view_func=CrontabView.as_view(name='crontab'))

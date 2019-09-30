from flask import (Blueprint, render_template, session, request, jsonify)
from flask.views import MethodView
from lib.models import (Use_case_result, Use_case, Result_step, Step_detail)
from lib.global_func import (get_db, del_db_data, get_logger)
from lib.paging import Paging


app = Blueprint(name='use_case_result', import_name=__name__)

logger = get_logger()


class UseCaseResult(MethodView):

    def get(self):
        db = get_db()
        user_id = session.get('user_id')
        use_case_id = request.args.get('use_case_id')
        # 查用例数据
        uc_obj = db.query(Use_case).filter(Use_case.id == use_case_id).first()
        # 生成sql命令，查询该用户该用例的执行结果
        result_objs = db.query(Use_case_result).filter(Use_case_result.use_case_id == use_case_id, Use_case_result.user_id == user_id)
        # 获取数据量
        data_sum = result_objs.count()
        page = Paging(request, request.args.get('page', 1), data_sum, show_num=10)
        # 获取数据
        result_objs = result_objs[page.start: page.end]

        return render_template('use_case_result.html', result_objs=result_objs, uc_obj=uc_obj, page=page)

    def delete(self):
        ret = {'flag': 0}

        db = get_db()
        user_id = session.get('user_id')
        use_result_id = request.form.get('use_result_id')

        # 删除执行结果
        # 1.删除result_step表的内容
        del_db_data(db, db.query(Result_step).filter(Result_step.uc_result_id == use_result_id))
        # 2.删除use_case_result表的内容
        result = del_db_data(db, db.query(Use_case_result).filter(Use_case_result.id == use_result_id))

        # 删除会返回，删除了几条符合的结果，如果结果为0表示就没找到这条用例
        if result == 0:
            ret['flag'] = 1
            ret['error_info'] = '删除失败'

        return jsonify(ret)


class StepResult(MethodView):

    def get(self):
        db = get_db()
        # 获取用户
        user_id = session.get('user_id')
        username = session.get('login_user')
        # 获取用例对象
        uc_id = request.args.get('uc_id')
        uc_obj = db.query(Use_case).filter(Use_case.id == uc_id).first()
        # 获取用例结果对象
        uc_result_id = request.args.get('uc_result_id')
        uc_result_obj = db.query(Use_case_result).filter(Use_case_result.id == uc_result_id).first()
        # 查询步骤得执行结果
        result_step_objs = db.query(Result_step).filter(Result_step.uc_result_id == uc_result_id).all()
        # 格式化渲染得数据
        result_list = []
        step_success_count = 0
        step_failed_count = 0
        total_run_time = 0
        for obj in result_step_objs:
            # 查询对应步骤的参数和是否执行
            step_obj = db.query(Step_detail).filter(Step_detail.id == obj.step_id).first()
            error_info = obj.error_info if obj.error_info else ''
            result_list.append({'id': obj.id, 'params': step_obj.params, 'execute': step_obj.execute, 'status': obj.status, 'error_info': error_info, 'step_id': obj.step_id, 'parent_step_id': obj.parent_step_id, 'run_time': obj.run_time})
            # 记录步骤失败和成功的数量
            if obj.status == 1:
                step_success_count += 1
            else:
                step_failed_count += 1
            # 记录总运行时间
            if not obj.parent_step_id or obj.step_id == obj.parent_step_id:
                total_run_time += obj.run_time

        return render_template('step_result.html', uc_obj=uc_obj, result_list=result_list, username=username, uc_result_obj=uc_result_obj, step_success_count=step_success_count, step_failed_count=step_failed_count, total_run_time=total_run_time)


# 添加获取用例结果得路由
app.add_url_rule(rule='/use_case_result/', endpoint='get_use_case_result', view_func=UseCaseResult.as_view(name='get_use_case_result'))
# 添加获取用例步骤的执行结果得路由
app.add_url_rule(rule='/step_result/', endpoint='get_step_result', view_func=StepResult.as_view(name='get_step_result'))


# 返回用例截图
@app.route(rule='/get_screen_shot_page/')
def get_screen_shot():
    uc_result_id = request.args.get('uc_result_id')
    db = get_db()
    result_step_obj = db.query(Result_step).filter(Result_step.uc_result_id == uc_result_id).all()
    img_file_lis = []
    for obj in result_step_obj:
        if obj.screen_shot != None:
            img_file_lis.append('/static/screen_shot/' + obj.screen_shot)
    return render_template('use_case_screen_shot.html', img_file_lis=img_file_lis)

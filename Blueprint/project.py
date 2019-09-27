from flask import (
    Blueprint,
    request,
    # jsonify,
    session)
from flask.views import MethodView

from lib.global_func import (
    get_db,
    save_data_to_db,
)
from lib.models import (
    Project,
    project_name_length,
    project_description_length,
)


app = Blueprint(name='project', import_name=__name__)


class Project_opt(MethodView):

    def check_project_name(self, db, data):
        project_name = data.get('project_name').strip()
        flag = True
        error = ''

        if len(project_name) == 0:
            flag = False
            error = '项目名称不可为空!'
        elif len(project_name) > project_name_length:
            flag = False
            error = '创建的项目名称过长！'
        elif db.query(Project).filter(Project.project_name == project_name).first():
            flag = False
            error = '该项目名称已经存在！'

        return flag, error

    def check_project_description(self, data):
        project_description = data.get('project_description').strip()
        flag = True
        error = ''

        if len(project_description) > project_description_length:
            flag = False
            error = '创建的项目描述过长！'

        return flag, error

    def post(self):
        db = get_db()
        status_code = 201
        ret = {}

        data = request.form.to_dict()
        # 验证项目名称
        flag, error = self.check_project_name(db, data)
        if not flag:
            return {'error': error}, 422
        # 验证项目描述
        flag, error = self.check_project_description(data)
        if not flag:
            return {'error': error}, 422
        # 添加项目数据
        data['user_id'] = session.get('user_id')
        save_data_to_db(db, [Project(**data)])

        return ret, status_code


app.add_url_rule(rule='/api/manager/project/', endpoint='project', view_func=Project_opt.as_view(name='project'))

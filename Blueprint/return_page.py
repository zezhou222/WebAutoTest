from flask import (Blueprint, render_template, session, request)
from sqlalchemy.sql import or_, and_
from lib.global_func import get_db
from lib.models import (Userinfo, Use_case, Project)
from lib.paging import Paging
from lib.flask_form import UseCaseForm


app = Blueprint(name='return_page', import_name=__name__)


@app.route(rule='/login/')
def login_page():
    return render_template('login.html')


@app.route(rule='/register/')
def register_page():
    return render_template('register.html')


# 首页的url及视图函数
@app.route(rule='/')
def index():
    return render_template('index.html')


app.add_url_rule(rule='/index/', endpoint='index', view_func=index)


@app.route(rule='/alter_password/')
def alter_password():
    return render_template('alter_password.html')


@app.route(rule='/alter_email/')
def alter_email():
    return render_template('alter_email.html')


@app.route(rule='/forget_password/')
def forget_pwd():
    return render_template('forget_pwd.html')


@app.route(rule='/import_use_case_data/')
def import_use_case_data():
    return render_template('import_use_case_data.html')


@app.route(rule='/interface_test/add/')
def interface_test_add():
    return render_template('add_interface_test.html', interface_test_id=None)


@app.route(rule='/interface_test/edit/<int:interface_test_id>/')
def interface_test_edit(interface_test_id=None):
    if interface_test_id is None:
        return {'error': 'not found the page.'}, 404

    return render_template('add_interface_test.html', interface_test_id=interface_test_id)


@app.route(rule='/get_use_case_page/')
def use_case_page():
    opt = request.args.get('opt')
    search_content = request.args.get('search_content')

    db = get_db()
    username = session.get('login_user')
    user_obj = db.query(Userinfo).filter(Userinfo.username == username).first()

    # 查询数据，获取数据总数，放置分页器
    if not opt:
        usecase_objs = db.query(Use_case).filter(or_(Use_case.user_id == user_obj.id, Use_case.uc_type == 'public'))
    else:
        search_content = '%' + search_content.strip() + '%'
        if opt == 'all':
            usecase_objs = db.query(Use_case).filter(or_(Use_case.user_id == user_obj.id, Use_case.uc_type == 'public'),Use_case.name.like(search_content))
        elif opt == 'project':
            project_objs = db.query(Project).filter(Project.project_name.like(search_content)).all()
            project_ids = []
            for obj in project_objs:
                project_ids.append(obj.id)
            usecase_objs = db.query(Use_case).filter(Use_case.project_id.in_(project_ids))
        elif opt == 'public':
            usecase_objs = db.query(Use_case).filter(Use_case.uc_type == 'public', Use_case.name.like(search_content))
        elif opt == 'general':
            usecase_objs = db.query(Use_case).filter(Use_case.user_id == user_obj.id, Use_case.uc_type == 'general',Use_case.name.like(search_content))
    # 倒序
    usecase_objs = usecase_objs.order_by(Use_case.id.desc())

    data_sum = usecase_objs.count()
    page = Paging(request, request.args.get('page', 1), data_sum, show_num=3)

    # 取数据
    usecase_objs = usecase_objs[page.start: page.end]

    return render_template('use_case_test.html', usecase_objs=usecase_objs, page=page, now_user_id=user_obj.id)


@app.route(rule='/use_case_operate/')
def use_case_operate():
    data = request.args.to_dict()
    opt = data['opt']
    form = UseCaseForm()
    if opt == 'add':
        return render_template('add_use_case.html', form=form, opt=opt, use_case_id=None)
    else:
        use_case_id = data['use_case_id']
        return render_template('add_use_case.html', form=form, opt=opt, use_case_id=use_case_id)


# ---------------------------------管理者的----------------------------------------------

@app.route(rule='/manager/')
def return_manager_page():
    return render_template('manager.html')


@app.route(rule='/manager/project/add/')
def add_project_page():
    return render_template('add_project.html')

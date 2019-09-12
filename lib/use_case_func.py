from lib.global_func import (get_db, save_data_to_db)
from lib.models import Use_case, Step_detail


# 检测添加的用例是否和公共用例重名
def check_public_uc_name(data):
    db = get_db()

    if data['uc_type'] == 'public':
        t = db.query(Use_case).filter(Use_case.uc_type == 'public', Use_case.name == data['name']).first()
        if t:
            return True

    return False


# 检测自己的用例重名情况
def check_general_uc_name(data):
    db = get_db()
    return True if db.query(Use_case).filter(Use_case.user_id == data['user_id'], Use_case.name == data['name']).first() else False


# 添加用例数据
def add_uc_data(data):
    db = get_db()
    params = data.pop('params')

    # 实例用例对象
    use_case_obj = Use_case(**data)
    use_case_obj.uc2step_detail = []

    # 实例用例步骤数据
    if params != '':
        many_param = params.split('||')
        for param in many_param:
            temp = param.split('@@')
            execute = int(temp[-1])
            use_case_obj.uc2step_detail.append(Step_detail(params=param, execute=execute))

    # 保存用例数据至数据库
    save_data_to_db(db, [use_case_obj])

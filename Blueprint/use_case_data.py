import xlrd
import os
from flask import (
    Blueprint,
    request,
    jsonify,
    session)

from lib.global_func import (get_random_filename, get_db, get_logger)
from settings import (temp_path)
from lib.use_case_func import (add_uc_data, check_public_uc_name)
from lib.models import (Project)


app = Blueprint(name='use_case_data', import_name='use_case_data')

logger = get_logger()


def read_file_content(f, size, read_size=4096):
    content = ""
    while size >= read_size:
        content += f.read(read_size)
        size -= read_size
    else:
        if size:
            content += f.read(size)
    return content


def read_excel_data(file_path):
    db = get_db()
    workbook = xlrd.open_workbook(file_path)
    sheet = workbook.sheet_by_index(0)
    dic = {}
    params = []
    for index in range(sheet.nrows):
        row_data = sheet.row_values(index)
        if index == 1:
            project_obj = db.query(Project).filter(Project.project_name == row_data[1].strip()).first()
            dic['name'] = row_data[0]
            dic['project_id'] = project_obj.id if project_obj else ''
            dic['uc_type'] = row_data[2]
            dic['desc'] = row_data[3]
        elif index >= 3:
            temp = []
            for data in row_data[:-1]:
                if data.strip() != '':
                    temp.append(data)
            else:
                temp.append(str(int(row_data[-1])))
            params.append('@@'.join(temp))

    dic['params'] = '||'.join(params)
    dic['user_id'] = session.get('user_id')

    return dic


@app.route(rule='/accept_excel_file/', methods=['post'])
def accept_execel_file():
    ret = {'flag': 0}
    files = request.files.getlist('files')
    for file in files:
        # 临时保存文件，由于不知道xlrd模块怎么传入二进制数据
        file_path = os.path.join(temp_path, get_random_filename() + '.xlsx')
        file.save(file_path)

        # 读取excel表数据
        use_case_data = read_excel_data(file_path)

        # 删除excel表，可以考虑每晚定时删除无用的数据(提高效率)
        os.remove(file_path)

        # 检测是否和公共用例重名
        flag = check_public_uc_name(use_case_data)
        if not flag:
            if use_case_data.get('project_id', '') != '':
                # 添加用例数据
                add_uc_data(use_case_data)
            else:
                ret['flag'] = 2
                ret['error_info'] = '所属项目不存在!'
                break
        else:
            ret['flag'] = 1
            ret['error_info'] = '用例名称和公共用例重名!'
            break

    return jsonify(ret)

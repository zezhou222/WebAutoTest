import json
import requests
from flask import (Blueprint, request, jsonify, session)
from flask.views import MethodView
from lib.models import (Params, Interface_test)
from lib.global_func import get_db
from lib.myrequest import MyRequest


app = Blueprint(name="interface_test", import_name=__name__)


@app.route(rule='/api/temp_execute_interface_test/', methods=['post'])
def temp_interface_test():
    data = json.loads(request.data)
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


class InterfaceTest(MethodView):

    def post(self):
        interface_test_data = json.loads(request.data)
        interface_test_data['interface_type'] = 0 if interface_test_data['interface_type'] == '0' else 1
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
            db.close()
        except Exception as err:
            # 添加数据出错执行回滚操作
            print('添加接口数据出错：', err)
            db.rollback()
            return {'error': '添加出错！'}, 422

        return {}, 201


app.add_url_rule(rule='/api/interface_test/', endpoint='interface_test', view_func=InterfaceTest.as_view(name='interface_test'))

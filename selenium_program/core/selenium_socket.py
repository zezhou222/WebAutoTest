import os
import socketserver
import json
from datetime import datetime
import time
from jinja2 import Template
from concurrent.futures import ThreadPoolExecutor
from lib.global_func import (get_cursor, commit_data)
from core.selenium_operate import SeleniumOperate
from conf.settings import (thread_count, step_result_template_path, sender, sender_username, sender_password, screen_shot_path)
from lib.send_mail import MyEmail


# 开启线程池
thread = ThreadPoolExecutor(thread_count)


class SeleniumServer(socketserver.BaseRequestHandler):

    def execute_public_use_case(self, public_use_case_name, execute, uc_result_id):
        # 判断这个公共用例是否执行
        if execute == 0:
            return

        # 查询公共用例的执行步骤，通过用例名查询
        self.cursor.execute("select t2.id,t2.params,t2.execute from use_case as t1 left join step_detail as t2 on t1.id=t2.uc_id where t1.name=%s and t1.uc_type='public' and t2.delete_status=0;", args=(public_use_case_name,))
        result = self.cursor.fetchall()
        if result:
            # 调用执行
            return self.execute_use_case_step(result, uc_result_id)
        else:
            # 可能是由于公共用例被修改，导致
            return [], 'failed'

    def execute_use_case_step(self, result, uc_result_id):

        # 全局的状态
        whole_status = 'success'
        # 存放result_step表的数据
        execute_data = []
        # 是否有截图
        screen_shot_flag = 0

        # 循环操作selenium步骤
        for dic in result:
            print('小步骤：', dic)
            # 单个步骤结果
            single_status = 1
            # 错误信息
            error_info = None
            # 步骤id
            step_id = dic.get('id')
            # 开始时间
            start_time = time.time()

            step_execute = dic.get('execute')  # 返回的是整型数据
            # 如果步骤非执行，则跳过执行下一步骤
            if step_execute == 0:
                # 单个步骤执行结果先写入列表中
                execute_data.append((uc_result_id, step_id, single_status, error_info))
                continue

            # 正常执行
            all_step = dic.get('params').split('@@')
            # 获取执行方法
            step_method = all_step.pop(0)
            # 步骤是否执行，由于上面判断过了，所以不用了
            is_execute = all_step.pop()

            # 判断如果是public_use_case执行公共用例
            if step_method == 'public_use_case':
                # 执行公共用例
                data, public_uc_status, _ = self.execute_public_use_case(all_step[0], is_execute, uc_result_id)
                # 设置全局步骤的执行状态
                if public_uc_status == 'failed':
                    whole_status = 'failed'

                total_time = 0
                temp_data = []
                for dic in data:
                    step_status = dic[2]
                    step_error_info = dic[3]
                    # 单个步骤的运行时长
                    run_time = dic[5]
                    # 计算总时长，给公共用例的总信息
                    total_time += run_time
                    # 截图名称
                    screen_shot = dic[6]
                    temp_data.append((uc_result_id, dic[1], step_status, step_error_info, step_id, run_time, screen_shot))

                # 添加公共用例整体的执行状态
                execute_data.append((uc_result_id, step_id, 1 if public_uc_status == 'success' else 0, '公共用例可能被修改.' if data == [] else None, step_id, total_time, None))
                # 添加公共用例小步骤的执行状态
                execute_data.extend(temp_data)

                # 公共用例执行完，执行下一步骤
                continue

            # 非公共用例的执行
            # if hasattr(self.selenium_obj, step_method):

            # 判断如果是验证码，那么先执行截图一次
            if step_method == 'identifying_code':
                ret = getattr(self.selenium_obj, 'screen_shot')([])
                self.selenium_obj.identifying_code_file = os.path.join(screen_shot_path, ret)

            # 执行步骤
            try:
                ret = getattr(self.selenium_obj, step_method)(all_step)
            except Exception as error:
                print('执行%s步骤出问题，错误信息:%s' % (dic.get('params'), error))
                # 修改状态标志
                whole_status = 'failed'
                single_status = 0
                # 错误信息
                error_info = str(error)

            # 结束时间
            end_time = round(time.time() - start_time, 5)

            # 单个步骤执行结果先写入列表中
            # 判断步骤是否是截图的
            if step_method == 'screen_shot':
                # 表示这个用例执行有截图
                screen_shot_flag = 1
                execute_data.append((uc_result_id, step_id, single_status, error_info, None, end_time, ret))
            # 识别验证码的
            elif step_method == 'identifying_code':
                # 表示这个用例执行有截图
                screen_shot_flag = 1
                code, code_path = ret
                if code == '':
                    code = '未识别出该验证码.'
                else:
                    code = '识别的验证码为:%s' % code
                execute_data.append((uc_result_id, step_id, single_status, code, None, end_time, code_path))
            else:
                execute_data.append((uc_result_id, step_id, single_status, error_info, None, end_time, None))

            # else:
            #     # 非正常请求来的
            #     return

        return execute_data, whole_status, screen_shot_flag

    def execute_use_case(self, data):
        # 读出数据库该用例的执行步骤
        uc_id = data.get('use_case_id')

        # 写入执行结果的准备工作-------------------start
        execute_time = datetime.now()
        user_id = data.get('user_id')
        # 先插入用例结果数据，小步骤存储时候需要
        self.cursor.execute('insert into use_case_result(status,execute_time,use_case_id,user_id) value(%s,%s,%s,%s);', args=('executing', execute_time, uc_id, user_id))

        # 获取新增数据的自增id
        uc_result_id = self.cursor.lastrowid
        print('新增数据的id为: ', uc_result_id)
        # 提交数据
        commit_data()

        # 写入执行结果的准备工作------------------- end

        # 获取用例的执行步骤
        self.cursor.execute('select id,params,execute from step_detail where uc_id=%s and delete_status=0;', args=(uc_id,))
        result = self.cursor.fetchall()

        # 执行全部步骤！！存放result_step表的数据，单个小步骤执行的结果及错误信息，以及全局的标志
        execute_data, whole_status, screen_shot_flag = self.execute_use_case_step(result, uc_result_id)

        print('小步骤的执行结果:', execute_data)
        print('小步骤的执行状态:', whole_status, screen_shot_flag)

        # 结束时间
        end_time = datetime.now()
        # 需要修改use_case_result的status值
        self.cursor.execute('update use_case_result set status=%s,end_time=%s,screen_shot_flag=%s where id=%s;', args=(whole_status, end_time, screen_shot_flag, uc_result_id))

        # 插入result_step数据
        self.cursor.executemany('insert into result_step(uc_result_id,step_id,status,error_info,parent_step_id,run_time,screen_shot) values(%s,%s,%s,%s,%s,%s,%s);', execute_data)
        # 提交数据，写入硬盘
        commit_data()

        # 用例执行完，添加完，判断是否发送邮件
        send_mail = data.get('send_mail')
        if send_mail:
            self.send_step_result(user_id, uc_id, uc_result_id)


    def send_step_result(self, user_id, uc_id, uc_result_id):
        # 查数据库数据
        self.cursor.execute('select t1.username,t1.email, t2.name,t2.desc,t3.params,t3.execute,t4.status,t4.execute_time,t5.status,t5.error_info,t5.run_time,t5.step_id,t5.uc_result_id,t5.parent_step_id,t5.screen_shot,t6.project_name from userinfo as t1 inner join use_case as t2 inner join step_detail as t3 inner join use_case_result as t4 inner join result_step as t5 inner join project as t6 on t1.id=t2.user_id and t1.id=t4.user_id and t3.uc_id=t2.id and t4.use_case_id=t2.id and t5.uc_result_id=t4.id and t5.step_id=t3.id where t1.id=%s and t2.id=%s and t4.id=%s and t2.project_id=t6.id;', args=(user_id, uc_id, uc_result_id))
        result = self.cursor.fetchall()

        # 格式化初始数据
        receiver_email = result[0].get('email')
        username = result[0].get('username')
        uc_name = result[0].get('name')
        project_name = result[0].get('project_name')
        uc_desc = result[0].get('desc')
        execute_time = str(result[0].get('execute_time'))
        status = result[0].get('status')
        total_run_time = 0
        result_list = []
        screen_shot_files = []
        for dic in result:
            total_run_time += float(dic.get('run_time'))
            result_list.append({'params': dic.get('params'), 'execute': dic.get('execute'), 'status': dic.get('t5.status'), 'run_time': str(dic.get('run_time')), 'error_info': dic.get('error_info') if dic.get('error_info') != None else '', 'step_id': dic.get('step_id'), 'parent_step_id': dic.get('parent_step_id')})
            # 添加截图路径
            screen_shot = dic.get('screen_shot')
            if screen_shot:
                screen_shot_files.append(os.path.join(screen_shot_path, screen_shot))

        # 读取模板文件进行渲染
        with open(step_result_template_path, 'r', encoding='utf-8') as f:
            data = f.read()
        template = Template(data)
        template_ret = template.render(locals())

        # 发送邮件
        email_obj = MyEmail(sender=sender, receiver=receiver_email, username=sender_username, password=sender_password)
        email_obj.create_email(mail_title='%s的执行报告' % uc_name)
        email_obj.email_text(template_ret, content_type='html')
        # 添加图片附件
        for file_path in screen_shot_files:
            email_obj.email_appendix(file_path)
        # 发送
        email_obj.send_mail()


    # 客户端连接成功会先到这个方法
    def handle(self):
        conn = self.request  # 客户端的通道
        addr = self.client_address  # 客户端的地址
        # 实例selenium对象，执行实例方法需要调用，为了拆分文件
        self.selenium_obj = SeleniumOperate()
        # 数据库的操作句柄
        self.cursor = get_cursor()
        print(addr, '连接--')
        while 1:
            # 接收内容
            try:
                content = conn.recv(1024)
            except ConnectionResetError:
                break
                
            if content == b'':
                break

            print('发送的数据:', content)
            # 执行操作方法
            content = json.loads(content.decode('utf-8'))
            opt = content.get('opt')
            if hasattr(self, opt):
                # 调用操作
                func = getattr(self, opt)
                # 放到线程池中执行
                thread.submit(func, content.get('data'))
            else:
                break

        print(addr, '断开连接--')
        conn.close()


def run():
    print('server start.')
    server = socketserver.ThreadingTCPServer(('0.0.0.0', 9001), SeleniumServer)
    server.serve_forever()


if __name__ == '__main__':
    run()

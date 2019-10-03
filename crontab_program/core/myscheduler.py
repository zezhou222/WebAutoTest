from pytz import timezone
from pymongo import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

from conf.settings import (
    mongodb_host,
    mongodb_port,
    mongodb_database,
    mongodb_job_table,
)
from lib.global_func import (
    send_to_selenium,
    # commit_data,
    send_content,
    get_logger
)

logger = get_logger()


class MyScheduler(object):

    __flag = None

    # 单例模式
    def __new__(cls, *args, **kwargs):
        if not cls.__flag:
            cls.__flag = super().__new__(cls)
        return cls.__flag

    def __init__(self):
        if 'scheduler' not in self.__dict__:
            # MongoDB的客户端连接配置
            client = MongoClient(host=mongodb_host, port=mongodb_port, document_class=dict)
            # 做关联
            m_job = MongoDBJobStore(database=mongodb_database, client=client, collection=mongodb_job_table)

            # 初始信息
            jobstores = {
                'default': m_job,
            }
            executors = {
                'default': ThreadPoolExecutor(20),
                # 'processpool': ProcessPoolExecutor(5)
            }
            job_defaults = {
                'coalesce': False,
                'max_instances': 3
            }
            # 实例调度器对象
            scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=timezone('Asia/Shanghai'))
            # 启动
            scheduler.start()

            self.scheduler = scheduler

    def add_task(self, data):
        task_id = data.get('task_id_name')
        task_type = data.get('task_type')
        execute_time = data.get('execute_time')
        test_data_id = data.get('test_data_id')
        test_type = data.get('test_type')
        user_id = data.get('user_id')

        args = [{'opt': 'execute_' + test_type, 'data': {test_type + '_id': test_data_id, 'user_id': user_id}}]

        if task_type == 'interval_task':
            t = execute_time.split('-')
            params = {'trigger': 'interval', t[0]: int(t[1]), 'id': task_id, 'func': send_to_selenium , 'args': args}
        elif task_type == 'once_task':
            params = {'trigger': 'date', 'run_date': execute_time,  'id': task_id, 'func': send_to_selenium, 'args': args}
        elif task_type == 'crontab_task':
            t = execute_time.split(' ')
            params = {'trigger': 'cron', 'minute': t[0], 'hour': t[1], 'day': t[2], 'month': t[3], 'week': t[4], 'id': task_id, 'func': send_to_selenium, 'args': args}

        # 添加任务
        try:
            self.scheduler.add_job(**params)
            # raise TypeError('????')
        except Exception as error:
            # 删除job
            self.scheduler.remove_job(job_id=task_id)
            # 发送后端结果
            logger.debug('添加job失败，失败原因: %s' % error)
            send_content(self.conn, {'add_flag': 1})
            return

        # 保存数据
        # self.cursor.execute('insert into crontab(task_name,project_id,test_type,test_data_id,task_type,execute_time,task_description,user_id,task_id_name) value(%s,%s,%s,%s,%s,%s,%s,%s,%s);', args=(data['task_name'],data['project_id'],test_type,test_data_id,task_type,execute_time,data['task_description'],user_id,data['task_id_name']))
        # commit_data()

        # 发送结果
        send_content(self.conn, {'add_flag': 0})

    def del_task(self, data):
        crontab_id = data.get('crontab_id')
        task_id = data.get('task_id')

        try:
            self.scheduler.remove_job(job_id=task_id)
        except Exception as error:
            # 发送后端结果
            logger.debug('删除job失败，失败原因: %s' % error)
            send_content(self.conn, {'del_flag': 1})
            return

        # 发送结果
        send_content(self.conn, {'del_flag': 0})

    def update_task(self, data):
        # 由于默认修改只能是修改触发器，不能修改执行的内容，所以采用删除新建的方式进行

        # 删除任务

        # 新建任务
        pass

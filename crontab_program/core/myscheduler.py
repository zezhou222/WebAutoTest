from apscheduler.jobstores.base import JobLookupError
from pytz import timezone
from pymongo import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
# from apscheduler.triggers.combining import AndTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from conf.settings import (
    mongodb_host,
    mongodb_port,
    mongodb_database,
    mongodb_job_table,
    redis_host,
    redis_port,
    redis_db,
    redis_password
)
from lib.global_func import (
    send_content,
    get_logger,
    send_to_redis
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
            
            # Redis存储
            # redis_job = RedisJobStore(host=redis_host, port=redis_port, db=redis_db, password=redis_password)

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

    def get_add_params(self, data):
        task_id = data.get('task_id_name')
        task_type = data.get('task_type')
        execute_time = data.get('execute_time')
        test_data_id = data.get('test_data_id')
        test_type = data.get('test_type')
        user_id = data.get('user_id')
        
        # 调用的方法
        func = send_to_redis
        
        args = [{'opt': 'execute_' + test_type, 'data': {test_type + '_id': test_data_id, 'user_id': user_id}}]

        if task_type == 'interval_task':
            t = execute_time.split('-')
            params = {'trigger': IntervalTrigger(**{t[0]: int(t[1])}), 'id': task_id, 'func': func, 'args': args}
        elif task_type == 'once_task':
            params = {'trigger': DateTrigger(**{'run_date': execute_time}), 'id': task_id, 'func': func, 'args': args}
        elif task_type == 'crontab_task':
            t = execute_time.split(' ')
            dic = {'minute': t[0], 'hour': t[1], 'day': t[2], 'month': t[3], 'week': t[4]}
            params = {'trigger': CronTrigger(**dic), 'id': task_id, 'func': func, 'args': args}

        return params

    def add_task(self, data):
        task_id = data.get('task_id_name')

        # 任务id以存在的判断
        if self.scheduler.get_job(job_id=task_id):
            # 发送后端结果
            logger.error('添加job失败，已存在%s任务，执行异常.' % task_id)
            send_content(self.conn, {'add_flag': 1})

        params = self.get_add_params(data)

        # 添加任务
        try:
            self.scheduler.add_job(**params)
        except Exception as error:
            # 删除job
            if self.scheduler.get_job(job_id=task_id):
                self.scheduler.remove_job(job_id=task_id)
            # 发送后端结果
            logger.error('添加job失败，失败原因: %s' % error)
            send_content(self.conn, {'add_flag': 1})
            return

        # 发送结果
        send_content(self.conn, {'add_flag': 0})

    def del_task(self, data):
        # crontab_id = data.get('crontab_id')
        task_id = data.get('task_id_name')

        try:
            self.scheduler.remove_job(job_id=task_id)
        except JobLookupError as error:
            logger.warning('删除时找不到job，任务执行异常!')
            send_content(self.conn, {'del_flag': 0})
        except Exception as error:
            # 发送后端结果
            logger.error('删除job失败，失败原因: %s' % error)
            send_content(self.conn, {'del_flag': 1})
            return

        # 发送结果
        send_content(self.conn, {'del_flag': 0})
    
    def update_task(self, data):
        # crontab_id = data.get('crontab_id')
        
        params = self.get_add_params(data)

        job_id = params.pop('id')

        try:
            self.scheduler.modify_job(job_id=job_id, **params)
        except Exception as error:
            # 发送后端结果
            logger.error('更新任务时失败，失败原因: %s' % error)
            send_content(self.conn, {'update_flag': 1})
            return

        # 发送结果
        send_content(self.conn, {'update_flag': 0})

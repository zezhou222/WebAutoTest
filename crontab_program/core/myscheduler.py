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
        # 拿到任务的数据的id

        # 查询数据库，查询执行任务的内容

        # 添加任务(任务的id在上一查询步骤中)
        pass

    def del_task(self, data):
        # 由于是异步的，所以web后端应该是直接连接mongodb删除持久化的数据

        # 这要做的仅是删除内存中的任务(会报错apscheduler.jobstores.base.JobLookupError)
        pass

    def update_task(self, data):
        # 由于默认修改只能是修改触发器，不能修改执行的内容，所以采用删除新建的方式进行

        # 删除任务

        # 新建任务
        pass

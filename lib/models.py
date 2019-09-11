"""
创建表结构
"""
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import DECIMAL
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


# 创表删表，表操作都要用Model这个对象
Model = declarative_base()


class Userinfo(Model):
    # 实际在数据库存储的表名
    __tablename__ = 'userinfo'
    # 列的定义
    # 注：如果列为整型并且是主键，默认是自增的，可不写autoincrement参数
    id = Column(Integer, primary_key=True, autoincrement=True)

    username = Column(String(20), nullable=False, unique=True)

    password = Column(String(32), nullable=False)

    email = Column(String(20), nullable=True)

    create_time = Column(DateTime, nullable=False, default=datetime.now())
    # 正向，反向查找时候用
    user2uc = relationship('Use_case', backref="uc2user")
    # 是否发送邮件，默认发送
    send_mail = Column(Boolean, default=1)


class Use_case(Model):
    __tablename__ = 'use_case'

    id = Column(Integer, primary_key=True)
    # 用例名称
    name = Column(String(50), nullable=False)
    # 用例的类型,general或者是public,是public表示所有用户可以公用的用例
    uc_type = Column(String(10), nullable=False, default="general")
    # 描述信息
    desc = Column(String(1024))
    # 和用户表关联，表示是哪个用户的用例
    user_id = Column(Integer, ForeignKey('userinfo.id'), nullable=False)
    # 正向查找执行步骤
    uc2step_detail = relationship("Step_detail", backref="step_detail2uc")
    # 正向查找执行结果
    uc2ucr = relationship("Use_case_result", backref="ucr2uc")


class Use_case_result(Model):
    __tablename__ = "use_case_result"

    id = Column(Integer, primary_key=True)
    # 用例的执行状态，默认executing
    status = Column(String(12), nullable=False, default='executing')
    # 开始执行的时间
    execute_time = Column(DateTime(), nullable=False, default=datetime.now())
    # 执行结束的时间
    end_time = Column(DateTime)
    # 外键字段，多对一到用例表
    use_case_id = Column(Integer, ForeignKey('use_case.id'))
    # 外键字段，多对一到用户表，表示这个用例结果是谁搞出来的
    user_id = Column(Integer, ForeignKey('userinfo.id'))
    # 是否有截图
    screen_shot_flag = Column(Boolean, default=0)


class Use_case_step(Model):
    __tablename__ = "use_case_step"

    id = Column(Integer, primary_key=True)
    # 执行的方法名，前端要以value形式嵌入
    step_method_name = Column(String(50), nullable=False)
    # 步骤名称，前端的步骤的显示名称
    step_name = Column(String(30), nullable=False)
    # 步骤的长度，用于selenium执行时候进行判断
    step_length = Column(Integer(), nullable=False, default=1)
    # 步骤的示例
    step_case = Column(String(300), nullable=False)


class Step_detail(Model):
    __tablename__ = "step_detail"

    id = Column(Integer, primary_key=True)
    # 步骤的参数
    params = Column(String(200))
    # 表示该步骤是否执行，默认执行
    execute = Column(Boolean(), default=1)
    # 删除状态
    delete_status = Column(Boolean(), default=0)
    # 建立外键
    uc_id = Column(Integer, ForeignKey('use_case.id'))


class Result_step(Model):
    __tablename__ = "result_step"

    id = Column(Integer, primary_key=True)
    uc_result_id = Column(Integer, ForeignKey('use_case_result.id'), nullable=False)
    step_id = Column(Integer, ForeignKey('step_detail.id'), nullable=False)
    # 1表示执行成功，0表示失败
    status = Column(Boolean, default=1)
    # 如果失败，失败的错误信息
    error_info = Column(String(200), nullable=True)
    # 标识是公共用例的步骤的对应，如果为空标识非公例的执行结果
    parent_step_id = Column(Integer, ForeignKey('step_detail.id'), nullable=True)
    # 每个小步骤运行的时间
    run_time = Column(DECIMAL(10, 5))
    # 截图的文件名(仅文件名)
    screen_shot = Column(String(36))

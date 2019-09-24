# 引入Form基类
from flask_wtf import FlaskForm
# 引入Form元素父类
from wtforms import StringField, PasswordField, SelectField, TextAreaField
# 引入Form验证父类
from wtforms.validators import DataRequired, Length, EqualTo
# 一些验证数据
from lib.models import (
    project_name_length,
    project_description_length
)

# 登录表单类,继承与Form类
class BaseLogin(FlaskForm):

    username = StringField('name', validators=[DataRequired(message="用户名不能为空"), Length(10, 20, message='长度位于10~20之间')])

    password = PasswordField('password', validators=[DataRequired(message="密码不能为空"), Length(10, 20, message='长度位于10~20之间')])

class RegisterForm(FlaskForm):

    username = StringField('username', validators=[DataRequired(message='用户名不能为空'), Length(6, 20, message='用户名长度需要6~20位')])

    password = PasswordField('password', validators=[DataRequired(message="密码不能为空"), Length(6, 20, message='长度位于6~20之间')])


class UseCaseForm(FlaskForm):

    name = StringField('用例名称', validators=[DataRequired(message="用例名称不能为空!"), Length(min=1, max=50, message="长度在1~50字符.")])

    uc_type = SelectField('用例类型', choices=[('general', '普通用例'), ('public', '公用用例')], default='general', coerce=str)

    desc = TextAreaField('用例描述信息', validators=[Length(min=0, max=1024, message="不能超过1024个字符,")])


# 目前没用上
class ProjectForm(FlaskForm):

    project_name = StringField(validators=[
        DataRequired(message="项目名称不可为空!"),
        Length(min=1, max=project_name_length, message="创建的项目名称过长！"),
    ])

    project_description = StringField(validators=[Length(min=0, max=project_description_length, message="创建的项目描述过长！")])

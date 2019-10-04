var server_ip = 'http://127.0.0.1:9000';

// 登陆的url
var login_url = server_ip + '/login/';

// 注册的url
var register_url = server_ip + '/register/';

// 首页的url
var index_url = server_ip + '/index/';

// 提交用户注册信息的url
var submit_user_register_info_url = server_ip + '/user_register/';

// 提交用户登陆信息的url
var submit_user_login_info_url = server_ip + '/user_login/';

// 用户注销的url
var logout_url = server_ip + '/logout/';

// 获取用例页面的url
var use_case_url = server_ip + '/get_use_case_page/';

// 获取添加用例页面的url
var add_use_case_page_url = server_ip + '/use_case_operate/?opt=add';

// 添加用例的url
var add_use_case_url = server_ip + '/use_case/add/';

// 获取编辑用例页面的url
var edit_use_case_page_url = server_ip + '/use_case_operate/?opt=edit';

// 提交编辑用例数据的url
var edit_use_case_url = server_ip + '/use_case/edit/';

// 获取用例的执行步骤的url
var get_execute_step_url = server_ip + '/api/get_execute_step/';

// 获取步骤选项的url
var get_step_url = server_ip + '/get_step_options/';

// 删除用例的url
var del_use_case_url = server_ip + '/use_case/del/';

// 执行用例的url
var execute_use_case_url = server_ip + '/use_case/execute/';

// 获取用例结果得url
var get_use_case_result_url = server_ip + '/use_case_result/';

// 删除用例结果的url
var del_use_case_result_url = get_use_case_result_url;

// 获取用例步骤得执行结果得url
var get_step_result_url = server_ip + '/step_result/';

// 获取公共用例选项的url
var get_public_use_case_url = server_ip + '/get_public_use_case/';

// 修改密码页面的url
var alter_password_url = server_ip + '/alter_password/';

// 修改邮箱的url
var alter_email_url = server_ip + '/alter_email/';

// 获取用例执行结果截图的url
var get_screen_shot_url = server_ip + '/get_screen_shot_page/';

// 忘记密码发送邮件的url
var forget_pwd_send_email_url = server_ip + '/send_forget_pwd_email/';

// 重置密码的url
var reset_pwd_url = server_ip + '/reset_pwd/';

// 导入用例数据页面url
var import_use_case_data_page_url = server_ip + '/import_use_case_data/';

// 发送excel文件的url
var send_excel_file_url = server_ip + '/accept_excel_file/';

// 项目数据的url
var get_project_data_url = server_ip + '/api/get_project_data/';

// 添加接口测试页面
var add_interface_test_page_url = server_ip + '/interface_test/add/';

// 编辑接口测试的页面url
var edit_interface_test_page_url = server_ip + '/interface_test/edit/';

// 临时的接口测试url
var temp_interface_test_url = server_ip + '/api/temp_execute_interface_test/';

// 接口测试的url(增，删，改，查)
var interface_test_url = server_ip + '/api/interface_test/';

// 编辑时候获取数据的
var get_interface_test_data =  server_ip + '/api/get_interface_test/';

// 执行接口测试的url
var execute_interface_test_url = server_ip + '/api/execute_interface_test/';

// 获取接口测试结果的，删除结果的
var interface_test_result_url = server_ip + '/api/interface_test_result/';

// 定时任务的添加界面
var add_crontab_page_url = server_ip + '/crontab/add/';

// 定时任务编辑的界面
var edit_crontab_page_url = server_ip + '/crontab/edit/';

// 所有自己的用例
var get_my_use_case_data_url = server_ip + '/api/use_case/myself/all/';

// 所有自己的接口
var get_my_interface_data_url = server_ip + '/api/interface_test/myself/all/';

// 定时任务增删改查的api接口
var crontab_url = server_ip + '/api/crontab/';

// 获取任务数据的url
var get_crontab_data = server_ip + '/api/get_crontab/';

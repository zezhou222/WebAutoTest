// 创建项目标签(添加，编辑操作 -- 用例，接口时候使用)
function create_project_label() {
    var content = '<select class="form-control" id="project_id" name="project_id">';
    for (var i = 0; i < all_project_data.length; i++) {
        content += `<option value="${all_project_data[i].id}">${all_project_data[i].project_name}</option>`
    }
    content += '</select>';
    return content;
}


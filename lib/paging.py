import copy


class Paging(object):
    def __init__(self, req, page_num, sum_num, show_num=10, show_page_num=5):
        # 请求路径，做拼接用
        self.path = req.path

        # 用户输入的是否正确，如"aaa"给他定位到第一页
        try:
            self.page_num = int(page_num)
        except:
            self.page_num = 1

        # 数据总数
        self.sum_num = sum_num

        # GET提交的参数,为了保留搜索条件
        # 提交的参数，需要深copy得到一下，因为req.GET不可修改
        try:
            self.param = copy.deepcopy(req.GET)
        # 报错可能是应为是使用flask框架的缘故，所以换个写法。
        except AttributeError:
            self.param = req.args.to_dict()

        self.show_num = show_num
        self.show_page_num = show_page_num

        # 分页数量
        self.paging_num, t = divmod(self.sum_num, self.show_num)
        if t:
            self.paging_num += 1

        # 判断用户输入的页数是否超了或小了，如-10页给他定位到第1页，超出最大页数给他定位到最后一页
        # and self.paging_num 保证数据没有的情况下什么都不显示，而不是报错索引为负数。
        if self.page_num > self.paging_num and self.paging_num:
            self.page_num = self.paging_num
        elif self.page_num < 1:
            self.page_num = 1

        # 取列表值的起始值和终止值
        self.start_num = (self.page_num - 1) * self.show_num
        self.end_num = self.page_num * self.show_num

        # 页码列表
        if self.paging_num < self.show_page_num:
            self.page_list = [i for i in range(1, self.paging_num + 1)]
        else:
            if self.page_num + self.show_page_num // 2 > self.paging_num:
                self.page_list = [i for i in range(self.paging_num - self.show_page_num + 1, self.paging_num + 1)]
            elif self.page_num - self.show_page_num // 2 < 1:
                self.page_list = [i for i in range(1, self.show_page_num + 1)]
            else:
                self.page_list = [i for i in range(self.page_num - self.show_page_num // 2,
                                                   self.page_num + self.show_page_num // 2 + 1)]

        # print(self.page_list)

        # 前一页及后一页的页码
        self.prev_page_num = self.page_num - 1 if self.page_num > 1 else 1
        self.next_page_num = self.page_num + 1 if self.page_num < self.paging_num else self.page_num

    # 返回取当前页数据的起始值
    @property
    def start(self):
        return self.start_num

    # 终止值
    @property
    def end(self):
        return self.end_num

    def join_params(self, params):
        temp = []
        for k, v in params.items():
            temp.append("%s=%s" % (k, v))
        return '&'.join(temp)

    def make_label(self):
        temp = '<nav aria-label="Page navigation"><ul class="pagination pull-right">'

        # 前一页标签
        if self.page_num == 1:
            temp += '<li class="disabled"><a aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'
        else:
            self.param["page"] = self.prev_page_num
            temp += '<li><a href="{0}?{1}" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'.format(
                self.path, self.join_params(self.param))

        # 页码
        for i in self.page_list:
            self.param["page"] = i
            if i == self.page_num:
                temp += '<li class="active"><a href="{0}?{1}">{2}<span class="sr-only">(current)</span></a></li>'.format(
                    self.path, self.join_params(self.param), i)
            else:
                temp += '<li><a href="{0}?{1}">{2}</a></li>'.format(self.path, self.join_params(self.param), i)

        # 后一页标签
        if self.next_page_num == self.page_num:
            temp += '<li class="disabled"><a aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>'
        else:
            self.param["page"] = self.next_page_num
            temp += '<li><a href="{0}?{1}" aria-label="Next"><span aria-hidden="true">&raquo;</span></a></li>'.format(
                self.path, self.join_params(self.param))

        temp += '</ul></nav>'

        return temp

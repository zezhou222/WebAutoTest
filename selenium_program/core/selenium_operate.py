import time
from selenium import webdriver
from core.find_element import FindElement
from core.execute_action import ExecuteAction


# 继承的这俩类是为了拆开成几个文件
# 当该类没有什么方法时候，会去继承的俩类中找是否有那个方法
class SeleniumOperate(FindElement, ExecuteAction):
    
    def __init__(self):
        self.driver = None

    def open_webdriver(self, data):
        # 用于打开不同的浏览器
        browser = data.pop()
        # 目前先一个谷歌，之后进行判断打开不同的
        self.driver = webdriver.Chrome(r'file/chromedriver.exe')

    def enlarge_window(self, data=None):
        self.driver.maximize_window()

    def open_url(self, data):
        # selenium.common.exceptions.InvalidArgumentException: Message: invalid argument 报错，需要带协议头，try捕获错误
        url = data[0]
        self.driver.get(url)
        print(len(self.driver.page_source))

    def sleep_second(self, data):
        second = int(data[0])
        time.sleep(second)
        # raise TypeError("自定义错误！！")

    def close_browser(self, data=None):
        self.driver.quit()

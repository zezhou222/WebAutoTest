import time
from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException
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
        if browser == 'google':
            self.driver = webdriver.Chrome(executable_path=r'file/chromedriver.exe')
        elif browser == 'firefox':
            self.driver = webdriver.Firefox(executable_path=r'file/geckodriver.exe')

        self.driver.refresh()

    def enlarge_window(self, data=None):
        self.driver.maximize_window()

    def open_url(self, data):
        url = data[0]
        try:
            self.driver.get(url)
        except InvalidArgumentException:
            raise ValueError('请求地址需要加协议头.')

    def sleep_second(self, data):
        second = int(data[0])
        time.sleep(second)

    def close_browser(self, data=None):
        self.driver.quit()

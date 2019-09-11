"""
执行seleniume各种操作，如点击或动作链什么的，被继承关系
"""
import os
from lib.global_func import get_screen_shot_filename
from conf.settings import screen_shot_path


class ExecuteAction(object):
    
    def accept_alert(self, data):
        self.driver.switch_to_alert().accept()

    def dismiss_alert(self, data):
        self.driver.switch_to_alert().dismiss()

    def find_element_click(self, data):
        mode = data[0]
        param = data[1]
        ele = getattr(self, mode)(param)
        self.driver.execute_script("arguments[0].click();", ele)

    def find_element_double_click(self, data):
        mode = data[0]
        param = data[1]
        ele = getattr(self, mode)(param)
        ele.doubleClick()

    def screen_shot(self, data):
        filename = get_screen_shot_filename()
        file_path = os.path.join(screen_shot_path, filename)
        self.driver.get_screenshot_as_file(file_path)
        return filename

    def switch_window(self, data):
        window_index = int(data[0]) - 1
        windows = self.driver.window_handles
        # 判断window_index是否正确
        if window_index >=0 and window_index < len(windows):
            # 执行切换窗口操作
            self.driver.switch_to.window(windows[window_index])
        else:
            raise ValueError('窗口切换有误，索引不在范围内.')

    def close_now_window(self, data):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[-1])


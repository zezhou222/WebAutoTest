"""
查找页面元素的类，被继承关系
"""
import os
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image
from conf.settings import (find_ele_timeout_time, find_ele_per_second, screen_shot_path)
from lib.global_func import get_screen_shot_filename, baidu_discern


class FindElement(object):

    def id(self, param):
        try:
            # WebDriverWart的参数,5表示最多等待5秒等待标签加载出来，0.5表示0.5秒找一次
            ret = WebDriverWait(self.driver, find_ele_timeout_time, find_ele_per_second).until(EC.presence_of_all_elements_located((By.ID, param)))
        except TimeoutException:
            raise ValueError('通过ID未找到%s的标签.' % param)
        else:
            # 返回的是一个列表
            return ret[0]     
        
    def xpath(self, param):
        try:
            ret = WebDriverWait(self.driver, find_ele_timeout_time, find_ele_per_second).until(EC.presence_of_all_elements_located((By.XPATH, param)))
        except TimeoutException:
            raise ValueError('通过XPATH未找到%s的标签.' % param)
        else:
            return ret[0]

    def class_name(self, param):
        try:
            ret = WebDriverWait(self.driver, find_ele_timeout_time, find_ele_per_second).until(EC.presence_of_all_elements_located((By.CLASS_NAME, param)))
        except TimeoutException:
            raise ValueError('通过类名未找到%s的标签.' % param)
        else:
            return ret[0]

    def find_element_input_content(self, data):
        mode = data[0]
        param = data[1]
        content = data[2]
        ele = getattr(self, mode)(param)
        ele.send_keys(content)

    def identifying_code(self, data):
        # 目前无法得到验证码的图片，这样就没法去识别了
        mode = data[0]
        param = data[1]
        x, y = data[2].split(',')
        x, y = int(x), int(y)
        # 查找标签
        ele = getattr(self, mode)(param)
        ele_width = int(self.driver.execute_script("return document.getElementById('%s').width" % param))
        ele_height = int(self.driver.execute_script("return document.getElementById('%s').height" % param))
        # 裁剪图片
        screen_shot_file_path = self.identifying_code_file
        imgObject = Image.open(screen_shot_file_path)  # 获得截屏的图片
        imgCaptcha = imgObject.crop((x, y, x + ele_width + 5, y + ele_height))  # 裁剪
        # 保存裁剪的图片
        filename = get_screen_shot_filename()
        save_file_path = os.path.join(screen_shot_path, filename)
        imgCaptcha.save(save_file_path)
        # 识别验证码
        code = baidu_discern(save_file_path)
        # 添加至对象空间
        self.code = code

        # 删除无用的截图
        os.remove(screen_shot_file_path)

        return code, filename

    def input_identifying_code(self, data):
        # 输入验证码通过，self的特性，当识别成功了，把验证码存入对象一份，这边直接填写即可
        mode = data[0]
        param = data[1]
        ele = getattr(self, mode)(param)
        ele.send_keys(self.code)

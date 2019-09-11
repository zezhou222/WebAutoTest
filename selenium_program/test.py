import time

from selenium import webdriver
import selenium
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# option = ChromeOptions()
# option.add_experimental_option('excludeSwitches', ['enable-automation'])
# driver = webdriver.Chrome(executable_path='file/chromedriver.exe', options=option)

# driver = webdriver.Chrome('file/chromedriver.exe')
# driver.get('https://www.baidu.com')
# t = driver.find_element_by_id('kw')
# t.send_keys('古诗文网')
# try:
#     ret = WebDriverWait(driver, 5, 0.5).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="1"]/h3/a')))
# except selenium.common.exceptions.TimeoutException:
#     print("超时")
# else:
#     print(ret)
# driver.execute_script("arguments[0].click();", ret[0])
# time.sleep(2)
# driver.quit()

# from PIL import Image
#
# file_path = '../static/screen_shot/c56848a36f795349ea2db2c3dbde359e.png'
#
# imgObject = Image.open(file_path)   # 获得截屏的图片
# imgCaptcha = imgObject.crop((480, 250, 540, 280))  # 裁剪
# filename = 'code.png'
# imgCaptcha.save(filename)

driver = webdriver.Firefox(executable_path='./file/geckodriver.exe')
driver.get('https://www.baidu.com')

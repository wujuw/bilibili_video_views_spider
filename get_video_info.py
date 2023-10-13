# -*- coding: utf-8 -*-

from selenium import webdriver
import time

# headless模式
chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')

driver = webdriver.Chrome(options=chrome_options)

driver.get("https://www.bilibili.com/video/BV12m4y1T7pw")

time.sleep(200)
# 播放视频

# 获取window.__playinfo__变量
# playinfo = driver.execute_script("return window.__playinfo__")

# print(playinfo)
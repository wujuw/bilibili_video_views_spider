# -*- coding: utf-8 -*-

from selenium import webdriver
from time import sleep

if __name__ == '__main__':
    # headless模式
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless')
    chrome_options.add_argument('--window-size=1000,800')  # 窗口大小会有影响.

    with webdriver.Chrome(options=chrome_options) as driver:
        driver.get("https://www.bilibili.com/video/BV1L44y1c7mL")
        while True:
            # 获取window.__playinfo__变量
            playinfo = driver.execute_script("return window.__playinfo__")
            print(playinfo['data']['format'])
            print(playinfo['data'])
            sleep(1)
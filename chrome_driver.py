import os
import time
import datetime
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from utils.logger import log
import pyperclip
import json
import subprocess
import signal
import math

login_cookie = {
    "name": "SESSDATA",
    "value": "6a191ca5,1725637545,90f19*32CjAVv9NF7N_f46LpFGriKktEeNKR-5T7nBR7YPWT2jv45DiS1FbD-y7I-wU5BbtlpzMSVmt0bkRtc3JzdEQ1NDUzSUR1VjNHQkpJazhJdGZMM011VzJxc2hWdU5TNjdwcGowdG4wVENydTZCdnprRTBJb1l1TEoxYU1pYVhnWUUydWNKWV9PM2l3IIEC",
    "domain": ".bilibili.com",
    "path": "/",
    "httpOnly": True,
    "HostOnly": False,
    "Secure": True
}

quality_cookie = {
    "name": "CURRENT_QUALITY",
    "value": "80",
    "domain": ".bilibili.com",
    "path": "/",
}

userID_cookie = {
    "name": "DedeUserID",
    "value": "3493121159596040",
    "domain": ".bilibili.com",
    "path": "/",
}

resolution_qn = {
    'auto': '0',
    '360p': '16',
    '480p': '32',
    '720p': '64',
    '1080p': '80',
}

class ChromeDriver:
    # global infolist=[]
    def __init__(self, head_less=False):
        opt = webdriver.ChromeOptions()
        # opt.add_argument('--window-size=1000,800')  # 窗口大小会有影响.
        opt.add_argument('--start-maximized')
        opt.set_capability('pageLoadStrategy', 'none') # 使 brower.get 异步加载
        if head_less:
            opt.add_argument('--headless')  # 无界面化.
            opt.add_argument('--disable-gpu')  # 配合上面的无界面化.
        self.opt = opt

    def get_resolution(self,browser):
        media_info = browser.execute_script("return player.getMediaInfo()")
        video_height = media_info['videoHeight']
        video_width = media_info['videoWidth']
        return str(video_width) + 'x' + str(video_height)
        
    def play(self, ip, play_resolution, fullscreen_play, proxy=None):
        """
        :param proxy: 代理
        :param ip: 播放地址
        :return:
        """

        infolist=[]
        log_file, play_info_file, source_info_file = None, None, None
        try:
            if proxy:
                self.opt.add_argument('--proxy-server=%s' % proxy)
            with webdriver.Chrome(options=self.opt,) as browser:
                # 让B站强制使用H.264编码器
                # 打开浏览器

                browser.get("https://www.bilibili.com/")
                WebDriverWait(browser, 20, 0.5).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, 'bili-header__bar'))
                )
                browser.add_cookie(login_cookie)
                quality_cookie['value'] = resolution_qn[play_resolution]
                browser.add_cookie(quality_cookie)
                browser.add_cookie(userID_cookie)
                # browser.get("https://www.bilibili.com/")
                browser.execute_script("localStorage.setItem('bilibili_player_codec_prefer_type', '2')")
                browser.execute_script("localStorage.setItem('bilibili_player_codec_prefer_reset', '1.5.2')") # 1.5.2 可能后续会变化
                # recommend_auto_play
                browser.execute_script("localStorage.setItem('recommend_auto_play', 'close')")
            

                browser.get(ip)
                print("播放地址: ",ip)
                title="url\t启播时延\t时间\t当前播放时长\t视频时长\t清晰度\t播放倍速"
                print(title)
                infolist.append(title)
                startflag=0 #是否开始播放
                startDelay=0 #启播时延
                # wait bilibili-player show
                WebDriverWait(browser, 20, 0.5).until(
                    EC.visibility_of_element_located((By.ID, 'bilibili-player'))
                )
                print("播放器已加载")
                pstime = time.time()#播放请求时间
                cpinfo_flag = False
                # we=browser.find_element(By.ID,'bilibili-player')
                while True:
                    try:
                        # 移动鼠标
                        # ActionChains(browser).move_to_element(we).perform()# 鼠标悬停                    
                        # st=browser.find_element(By.CLASS_NAME,'bpx-player-state-buff-title').text
                        #print("状态信息:",st)
                        if startflag ==0:
                            try: 
                                paused = browser.execute_script("return player.isPaused()")
                            except Exception as e:
                                print('not found player')
                                paused = True
                            if not paused:#已经开始播放
                                petime = time.time()#播放开始时间
                                print('播放开始')
                                startDelay = petime-pstime
                                startflag =1 
                                browser.execute_script("return player.danmaku.close()") 
                                # 全屏播放
                                if fullscreen_play:
                                    browser.execute_script("return player.mediaElement().requestFullscreen()")
                                # browser.execute_script('player.requestQuality(%s)' % resolution_qn[play_resolution])
                            else: 
                                time.sleep(0.1)
                        elif  startflag ==1:
                            rl =  self.get_resolution(browser)
                            #抓取播放器日志结束
                            tm=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            # ActionChains(browser).move_to_element(we).perform()# 鼠标悬停 
                            # ct=browser.find_element(By.CLASS_NAME,'bpx-player-ctrl-time-current').text
                            ct = browser.execute_script("return player.getCurrentTime()")
                            #print("当前播放时长: ",ct)     #当前播放时长
                            # vl=browser.find_element(By.CLASS_NAME,'bpx-player-ctrl-time-duration').text
                            vl = browser.execute_script("return player.getDuration()")
                            # ceil
                            ct = math.ceil(ct)
                            vl = math.ceil(vl)
                            isEnded = browser.execute_script("return player.isEnded()")
                            ps='1x'
                            rowData="%s\t%s\t%s\t%s\t%s\t%s\t%s"%(ip,startDelay,tm,ct,vl,rl,ps,)
                            print(rowData)
                            infolist.append(rowData)
                            # if ct >= vl - 4 and not cpinfo_flag:
                            #     ActionChains(browser).move_to_element(we).perform()
                            #     ActionChains(browser).context_click(we).perform()
                            #     try:
                            #         vinfo = browser.find_element(By.XPATH,'//*[@id="bilibili-player"]/div/div/div[4]/ul/li[6]')
                            #         vinfo.click()
                            #         cpinfo_flag = True
                            #     except Exception:
                            #         pass
                            if isEnded or ct == vl:
                                break
                            time.sleep(0.5)
                    except Exception as e:
                        log.error(e)
                        time.sleep(0.5)
                        pass    
                    # sleep(1)
                    if time.time() - pstime > 600:
                        return None, None, None
                playinfo = browser.execute_script("return window.__playinfo__")
                todaytime = time.strftime("%Y-%m-%d", time.localtime(time.time()))
                if len(infolist) > 1:
                    filepath=os.path.abspath('.')                    
                    log_file = 'log_'+todaytime + '.txt'
                    file = open(filepath+'\\'+log_file, 'w', encoding='utf-8')
                    str = '\n'.join(n for n in infolist)
                    file.write(str)
                    file.write('\n')
                    file.close()
                #播放结束，保存播放日志
                # if cpinfo_flag:
                # cpinfo=browser.find_element(By.XPATH,'//*[@id="bilibili-player"]/div/div/div[1]/div[1]/div[15]/div[3]/div/span[2]')
                # cpinfo.click()
                # data = pyperclip.paste()
                data = browser.execute_script("return player.getFormattedLogs(0)")
                if len(data) > 1:
                    filepath=os.path.abspath('.')
                    play_info_file = 'playInfo_log_'+todaytime + '.txt'
                    file = open(filepath+'\\'+play_info_file, 'w', encoding='utf-8')
                    # str = '\n'.join(n for n in infolist)
                    file.write(data)
                    file.close()
                if len(playinfo) > 1:
                    filepath=os.path.abspath('.')
                    todaytime = time.strftime("%Y-%m-%d", time.localtime(time.time()))
                    source_info_file = 'playinfo_'+todaytime + '.txt'
                    file = open(filepath+'\\'+source_info_file, 'w', encoding='utf-8')
                    # str = '\n'.join(n for n in playinfo.data)
                    # file.write(str)
                    str = json.dumps(playinfo, indent=4)
                    file.write(str)
                    file.write('\n')
                    file.close()
                #退出浏览器
                # browser.quit()
        except Exception as e:
            log.error(e)
        return log_file,source_info_file,play_info_file

    def play_one(self, ip, net_interface, play_resolution, fullscreen_play):
        # 关掉现有的tshark进程
        subprocess.call('taskkill /F /IM tshark.exe', shell=True, stderr=subprocess.DEVNULL)
        # 播放前开始抓包
        capture_proc, pcap_path = capturePcap(net_interface)
        log_file, source_info_file, play_info_file = self.play(ip, play_resolution, fullscreen_play)
        stopCapture(capture_proc)
        moveOutputFiles(pcap_path, log_file, source_info_file, play_info_file, ip, play_resolution)

    def play_list(self, ip_list, net_interface, play_resolution, fullscreen_play):
        for ip in ip_list:
            # 关掉现有的tshark进程
            subprocess.call('taskkill /F /IM tshark.exe', shell=True, stderr=subprocess.DEVNULL)
            # 播放前开始抓包
            capture_proc, pcap_path = capturePcap(net_interface)
            log_file, source_info_file, play_info_file = self.play(ip, play_resolution, fullscreen_play)
            stopCapture(capture_proc)
            moveOutputFiles(pcap_path, log_file, source_info_file, play_info_file, ip, play_resolution)

    def play_loop(self, ip_list):
        while True:
            self.play_list(ip_list)

def moveOutputFiles(pcap_name, log_file, source_info_file, play_info_file, ip, play_resolution):
    """
    :param pcap_path: pcap文件路径
    :param log_file: 日志文件路径
    :param source_info_file: 播放源信息文件路径
    :param play_info_file: 播放信息文件路径
    :param ip: 播放地址
    :return:
    """
    # 播放失败，删除文件
    if not log_file or not source_info_file or not play_info_file or not pcap_name:
        if log_file != None and os.path.exists(log_file):
            os.remove(log_file)
        if source_info_file != None and os.path.exists(source_info_file):
            os.remove(source_info_file)
        if play_info_file != None and os.path.exists(play_info_file):
            os.remove(play_info_file)
        if pcap_name != None and os.path.exists(pcap_name):
            os.remove(pcap_name)
        return

    # 移动文件到指定目录
    folder = 'output/' + play_resolution
    if not os.path.exists(folder):
        os.makedirs(folder)
    vid = ip.split('/')[-1]
    folder = os.path.join(folder, vid)
    if not os.path.exists(folder):
        os.mkdir(folder)
    os.rename(pcap_name, os.path.join(folder, pcap_name))
    os.rename(log_file, os.path.join(folder, log_file))
    os.rename(source_info_file, os.path.join(folder, source_info_file))
    os.rename(play_info_file, os.path.join(folder, play_info_file))


def capturePcap(interface):
    """
    :param interface: 网卡名
    :return:
    """
    # 启动tshark进程并抓包
    pcap_name = 'captured.pcap'
    tshark_cmd = ['tshark', '-i', interface, '-w', pcap_name]
    tshark_proc = subprocess.Popen(tshark_cmd)
    return tshark_proc, pcap_name

def stopCapture(tshark_proc):
    """
    :param tshark_proc: tshark进程
    :return:
    """
    # 停止抓包 ctrl + c
    tshark_proc.send_signal(signal.SIGTERM)
    tshark_proc.wait()
    subprocess.call('taskkill /F /IM tshark.exe', shell=True, stderr=subprocess.DEVNULL)

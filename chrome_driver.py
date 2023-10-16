import os
import time
import datetime
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from utils.logger import log
import pyperclip
import json
import subprocess
import signal

login_cookie = {
    "name": "SESSDATA",
    "value": "7cdb20b5,1709952538,2139a*91",
    "domain": ".bilibili.com",
    "path": "/",
    "httpOnly": False,
    "HostOnly": False,
    "Secure": False
}

class ChromeDriver:
    # global infolist=[]
    def __init__(self, head_less=False):
        opt = webdriver.ChromeOptions()
        # opt.add_argument('--window-size=1000,800')  # 窗口大小会有影响.
        opt.add_argument('--start-maximized')
        if head_less:
            opt.add_argument('--headless')  # 无界面化.
            opt.add_argument('--disable-gpu')  # 配合上面的无界面化.
        self.opt = opt

    def get_resolution(self,we,browser,startflag):
        # 复制播放信息
        restr=""
        try: 
            pi = browser.find_element(By.CLASS_NAME,'bpx-player-info-container')#播放信息窗口
        except Exception as e:
            ActionChains(browser).move_to_element(we).perform()
            ActionChains(browser).context_click(we).perform()
            try:
                vinfo = browser.find_element(By.XPATH,'//*[@id="bilibili-player"]/div/div/div[4]/ul/li[6]')
                vinfo.click()
            except Exception:
                return restr
        try:
            pi=browser.find_element(By.CLASS_NAME,'bpx-player-info-container')#播放信息窗口
                
            rls=browser.find_element(By.XPATH,'/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/div/div/div[1]/div[1]/div[15]/div[2]').text
            rllist=rls.split("\n")
            for item in rllist:
                if item.find("Resolution")>=0:
                    restr=item[item.index(": ")+2:item.index("@")]
                    break
        except Exception as e:
            ActionChains(browser).context_click(we).perform()# 鼠标右键点击
            # log.error("错误2" + str(e))     
            try:      
                vinfo=browser.find_element(By.XPATH,'//*[@id="bilibili-player"]/div/div/div[4]/ul/li[6]')
                vinfo.click()
            except Exception as e:
                # log.error(e)
                pass
        return restr
    def play(self, ip, proxy=None):
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
            with webdriver.Chrome(options=self.opt) as browser:
                # 让B站强制使用H.264编码器
                # 打开浏览器
                browser.get("https://www.bilibili.com/")
                browser.add_cookie(login_cookie)
                # browser.get("https://www.bilibili.com/")
                browser.execute_script("localStorage.setItem('bilibili_player_codec_prefer_type', '2')")
                browser.execute_script("localStorage.setItem('bilibili_player_codec_prefer_reset', '1.5.2')") # 1.5.2 可能后续会变化
                # wait input
                # input("Press any key to continue...")
                # 编辑localStroage选择H.264编码
                # browser.execute_script("window.localStorage.setItem('bilibili_player_codec_prefer_type', '2');")
                # ATIME = time.time()
                browser.get(ip)
                pstime = time.time()#播放请求时间
                title="url\t启播时延\t卡顿次数\t时间\t当前播放时长\t视频时长\t清晰度\t播放倍速\t状态信息"
                print(title)
                infolist.append(title)
                kd=0 #卡顿次数
                kdflag=0 #卡顿标志
                startflag=0 #是否开始播放
                startDelay=0 #启播时延
                # wait bilibili-player show
                WebDriverWait(browser, 20, 0.1).until(
                    EC.presence_of_element_located((By.ID, 'bilibili-player'))
                )
                while True:
                    # 移动鼠标
                    we=browser.find_element(By.ID,'bilibili-player')
                    ActionChains(browser).move_to_element(we).perform()# 鼠标悬停                    
                    st=browser.find_element(By.CLASS_NAME,'bpx-player-state-buff-title').text
                    #print("状态信息:",st)
                    if startflag ==0:
                        if st =='':#已经开始播放
                            petime = time.time()#播放开始时间
                            startDelay = petime-pstime
                            #抓取播放器日志开始
                            # rl =  self.get_resolution(we,browser,startflag)
                            startflag =1 
                            #抓取播放器日志结束
                    elif  startflag ==1:
                        #log.info(petime)
                        if st !='':#出现卡顿
                            if kdflag==0:
                                kd = kd +1
                                kdflag=1
                        elif st =='':#卡顿消除
                            kdflag=0
                        #抓取播放器日志开始
                        rl =  self.get_resolution(we,browser,startflag)
                        #抓取播放器日志结束
                        tm=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ActionChains(browser).move_to_element(we).perform()# 鼠标悬停 
                        ct=browser.find_element(By.CLASS_NAME,'bpx-player-ctrl-time-current').text
                        #print("当前播放时长: ",ct)     #当前播放时长
                        vl=browser.find_element(By.CLASS_NAME,'bpx-player-ctrl-time-duration').text
                        #print("视频时长::",vl)     #视频时长
                        #rl=browser.find_element(By.CLASS_NAME,'bpx-player-ctrl-quality-result').text
                        #print("清晰度: ",rl)    #清晰度
                        ps=browser.find_element(By.CLASS_NAME,'bpx-player-ctrl-playbackrate-result').text
                        if ps=='倍速':
                            ps='1x'
                        #print("播放倍速: ",ps)    #播放倍速
                        #print("播放信息:\n",browser.find_element(By.XPATH,'//*[@id="bilibili-player"]/div/div').text)
                        rowData="%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s"%(ip,startDelay,kd,tm,ct,vl,rl,ps,st)
                        print(rowData)
                        infolist.append(rowData)
                        if ct !='':
                            if ct == vl:
                                break
                    # sleep(1)
                playinfo = browser.execute_script("return window.__playinfo__")
                todaytime = time.strftime("%Y-%m-%d", time.localtime(time.time()))
                if len(infolist) > 1:
                    filepath=os.path.abspath('.')                    
                    log_file = 'log_'+todaytime + '.txt'
                    file = open(filepath+'\\'+log_file, 'a+', encoding='utf-8')
                    str = '\n'.join(n for n in infolist)
                    file.write(str)
                    file.write('\n')
                    file.close()
                #播放结束，保存播放日志
                cpinfo=browser.find_element(By.XPATH,'//*[@id="bilibili-player"]/div/div/div[1]/div[1]/div[15]/div[3]/div/span[2]')
                cpinfo.click()
                data = pyperclip.paste()
                filepath=os.path.abspath('.')
                source_info_file = 'playInfo_log_'+todaytime + '.txt'
                file = open(filepath+'\\'+source_info_file, 'a+', encoding='utf-8')
                # str = '\n'.join(n for n in infolist)
                file.write(data)
                file.close()
                if len(playinfo) > 1:
                    filepath=os.path.abspath('.')
                    todaytime = time.strftime("%Y-%m-%d", time.localtime(time.time()))
                    play_info_file = 'playinfo_'+todaytime + '.txt'
                    file = open(filepath+'\\'+play_info_file, 'a+', encoding='utf-8')
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

    def play_list(self, ip_list, net_interface):
        for ip in ip_list:
            # 关掉现有的tshark进程
            subprocess.call('taskkill /F /IM tshark.exe', shell=True, stderr=subprocess.DEVNULL)
            # 播放前开始抓包
            capture_proc, pcap_path = capturePcap(net_interface)
            log_file, source_info_file, play_info_file = self.play(ip)
            stopCapture(capture_proc)
            moveOutputFiles(pcap_path, log_file, source_info_file, play_info_file, ip)

    def play_loop(self, ip_list):
        while True:
            self.play_list(ip_list)

def moveOutputFiles(pcap_name, log_file, source_info_file, play_info_file, ip):
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
        if os.path.exists(log_file):
            os.remove(log_file)
        if os.path.exists(source_info_file):
            os.remove(source_info_file)
        if os.path.exists(play_info_file):
            os.remove(play_info_file)
        if os.path.exists(pcap_name):
            os.remove(pcap_name)
        return

    # 移动文件到指定目录
    folder = 'output'
    if not os.path.exists(folder):
        os.mkdir(folder)
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
    
if __name__ == '__main__':
    from utils.bili_pool import BiliPool
    # if 'Windows' in platform.platform():
    #     iface = getInterfaceByName('WLAN')
    # else:
    #     iface = 'enp2s0'
    # captureData(iface)
    ip = BiliPool().pop()
    ChromeDriver().play(ip)

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
# import pcap
# import dpkt

class ChromeDriver:
    # global infolist=[]
    def __init__(self, head_less=False):
        opt = webdriver.ChromeOptions()
        opt.add_argument('--window-size=1000,800')  # 窗口大小会有影响.
        if head_less:
            opt.add_argument('--headless')  # 无界面化.
            opt.add_argument('--disable-gpu')  # 配合上面的无界面化.
        self.opt = opt

    def get_resolution(self,we,browser,startflag):
        # 复制播放信息
        restr=""
        try:    
            pi=browser.find_element(By.CLASS_NAME,'bpx-player-info-container')#播放信息窗口
            if not pi.is_displayed():
                ActionChains(browser).context_click(we).perform()# 鼠标右键点击
                sleep(1)
                vinfo=browser.find_element(By.XPATH,'//*[@id="bilibili-player"]/div/div/div[4]/ul/li[6]')
                vinfo.click()
                
            rls=browser.find_element(By.XPATH,'/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/div/div/div[1]/div[1]/div[15]/div[2]').text
            rllist=rls.split("\n")
            for item in rllist:
                if item.find("Resolution")>=0:
                    restr=item[item.index(": ")+2:item.index("@")]
                    break
        except Exception as e:
            ActionChains(browser).context_click(we).perform()# 鼠标右键点击
            sleep(1)
            log.error("错误2")     
            try:      
                vinfo=browser.find_element(By.XPATH,'//*[@id="bilibili-player"]/div/div/div[4]/ul/li[6]')
                vinfo.click()
            except Exception as e:
                log.error(e)
        return restr
    def play(self, ip, proxy=None):
        """
        :param proxy: 代理
        :param ip: 播放地址
        :return:
        """
        # TODO 实现自动登录或者cookie登录
        # TODO 设置编码器H.264

        infolist=[]
        try:
            if proxy:
                self.opt.add_argument('--proxy-server=%s' % proxy)
            with webdriver.Chrome(options=self.opt) as browser:
                # 打开浏览器
                browser.get("https://www.bilibili.com/")
                # 移动鼠标
                browser.find_element(By.CLASS_NAME,'header-login-entry').click()
                sleep(1)
                #登陆系统
                browser.find_element(By.XPATH,'/html/body/div[3]/div/div[4]/div[2]/form/div[1]/input').send_keys("15136882846")
                browser.find_element(By.XPATH,'/html/body/div[3]/div/div[4]/div[2]/form/div[3]/input').send_keys("secret00")
                browser.find_element(By.XPATH,'/html/body/div[3]/div/div[4]/div[2]/div[2]/div[2]').click()
                sleep(10)
                #打开指定视频
                ATIME = time.time()
                browser.get(ip)
                playinfo = browser.execute_script("return window.__playinfo__")                
                pstime = time.time()#播放请求时间
                #path = '''//*[@id="bilibili-player"]//button[@class='bpx-player-ctrl-btn-icon']'''
                #log.info(ip)
                # 等待元素渲染完毕再点击播放按钮
                # WebDriverWait(browser, 40).until(browser.find_element(By.XPATH,path))
                # su = browser.find_element_by_xpath(path)
                # su.click()
                #抓取状态
                #  模拟点击视频自动播放
                #driver.find_element(By.CLASS_NAME,'bpx-player-ctrl-btn.bpx-player-ctrl-play').click()#播放按钮
                #播放状态                
                #print("all Time s%:",BTIME - ATIME)
                title="url\t启播时延\t卡顿次数\t时间\t当前播放时长\t视频时长\t清晰度\t播放倍速\t状态信息"
                print(title)
                infolist.append(title)
                kd=0 #卡顿次数
                kdflag=0 #卡顿标志
                startflag=0 #是否开始播放
                startDelay=0 #启播时延
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
                            rl =  self.get_resolution(we,browser,startflag)
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
                todaytime = time.strftime("%Y-%m-%d", time.localtime(time.time()))
                if len(infolist) > 1:
                    filepath=os.path.abspath('.')                    
                    filenamenew = 'log_'+todaytime + '.txt'
                    file = open(filepath+'\\'+filenamenew, 'a+', encoding='utf-8')
                    str = '\n'.join(n for n in infolist)
                    file.write(str)
                    file.write('\n')
                    file.close()
                #播放结束，保存播放日志
                cpinfo=browser.find_element(By.XPATH,'//*[@id="bilibili-player"]/div/div/div[1]/div[1]/div[15]/div[3]/div/span[2]')
                cpinfo.click()
                data = pyperclip.paste()
                filepath=os.path.abspath('.')
                filenamenew = 'playInfo_log_'+todaytime + '.txt'
                file = open(filepath+'\\'+filenamenew, 'a+', encoding='utf-8')
                # str = '\n'.join(n for n in infolist)
                file.write(data)
                file.close()
                if len(playinfo) > 1:
                    filepath=os.path.abspath('.')
                    todaytime = time.strftime("%Y-%m-%d", time.localtime(time.time()))
                    filenamenew = 'playinfo_'+todaytime + '.txt'
                    file = open(filepath+'\\'+filenamenew, 'a+', encoding='utf-8')
                    # str = '\n'.join(n for n in playinfo.data)
                    # file.write(str)
                    str = json.dumps(playinfo, indent=4)
                    file.write(str)
                    file.write('\n')
                    file.close()
                #退出浏览器
                browser.quit()
        except Exception as e:
            log.error(e)

    def play_list(self, ip_list):
        for ip in ip_list:
            # TODO 播放前开始抓包
            self.play(ip)
            # TODO 播放结束后停止抓包
            # TODO 转移抓包文件和日志到指定目录

    def play_loop(self, ip_list):
        while True:
            self.play_list(ip_list)

# 抓包：param1 eth_name 网卡名
# def captureData(eth_name):
#     pkt = pcap.pcap(eth_name, promisc=True, immediate=True, timeout_ms=50)
#     # filter method
#     filters = {
#         'DNS': 'udp port 53',
#         'HTTP': 'tcp port 80'
#     }
#     # pkt.setfilter(filters['HTTP'])

#     pcap_filepath = 'd:/pkts_{}.pcap'.format(time.strftime("%Y%m%d-%H%M%S",
#         time.localtime()))
#     pcap_file = open(pcap_filepath, 'wb')
#     writer = dpkt.pcap.Writer(pcap_file)
#     print('Start capture...')
#     try:
#         pkts_count = 0
#         for ptime, pdata in pkt:
#             writer.writepkt(pdata, ptime)
#             # anlysisData(pdata)
#             printRawPkt(ptime, pdata)
#             pkts_count += 1
#     except KeyboardInterrupt as e:
#         writer.close()
#         pcap_file.close()
#         if not pkts_count:
#             os.remove(pcap_filepath)
#         print('%d packets received'%(pkts_count))
# #网卡名称
# if 'Windows' in platform.platform():
#     import winreg as wr


# IF_REG = r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}'
# def getInterfaceByName(name):
#     '''Get guid of interface from regedit of windows system
#     Args:
#         name: interface name
#     Returns:
#         An valid guid value or None.
#     Example:
#         getInterfaceByName('eth0')
#     reg = wr.ConnectRegistry(None, wr.HKEY_LOCAL_MACHINE)
#     reg_key = wr.OpenKey(reg, IF_REG)
#     for i in range(wr.QueryInfoKey(reg_key)[0]):
#         subkey_name = wr.EnumKey(reg_key, i)
#         try:
#             reg_subkey = wr.OpenKey(reg_key, subkey_name + r'\Connection')
#             Name = wr.QueryValueEx(reg_subkey, 'Name')[0]
#             wr.CloseKey(reg_subkey)
#             if Name == name:
#                 return r'\Device\NPF_' + subkey_name
#         except FileNotFoundError as e:
#             pass

#     return None
# # 抓包：param1 eth_name 网卡名，如：eth0,eth3。 param2 p_type 日志捕获类型 1：sdk日志用例分析 2：目标域名过滤输出 3：原始数据包
# def catch_pack(eth_name="enp5s0", packet_type=None):
#     sniffer = pcap.pcap(eth_name)
#     sniffer.setfilter("tcp")            # 只抓取TCP包
#     # sniffer.setfilter('tcp port 80')  # 设置监听过滤器
#     if sniffer:
#         for packet_time, packet_data in sniffer:  # packet_time为收到的时间，packet_data为收到的数据
#             th = threading.Thread(target=check_pack, args=(packet_time, packet_data, packet_type))
#             th.setDaemon(True)
#             th.start()

if __name__ == '__main__':
    from utils.bili_pool import BiliPool
    # if 'Windows' in platform.platform():
    #     iface = getInterfaceByName('WLAN')
    # else:
    #     iface = 'enp2s0'
    # captureData(iface)
    ip = BiliPool().pop()
    ChromeDriver().play(ip)

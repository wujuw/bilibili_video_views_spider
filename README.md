<!-- ## driver国内镜像
http://npm.taobao.org/mirrors/chromedriver/

## bilibili_video_views_spider
自动播放视频，配合换ip等可以刷点播放量

#### 运行主目录的 main.py 看看效果 若不行试试pull1.0稳定版

若要实现伪造多个高匿ip访问
spider代理池是必要的 https://github.com/incinya/proxies
即proxies文件夹，它是基于redis的，使用它可能要改下redis配置

## redis配置，在proxies.memory.conf.py
DB = 2
PASSWORD = 123456
HOST = '10.168.1.245'
PORT = 6379

#### 修改根目录下的conf.py把视频地址，up主空间改成自己的就可以了

#### test文件测试ip变化

####提升selenium速度
driver.get()这个操作，改成不阻塞的

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
desired_capabilities = DesiredCapabilities.CHROME
desired_capabilities["pageLoadStrategy"] = "none"
driver = webdriver.Chrome(executable_path='chromedriver.exe')

--- -->

## 当前版本
### 仍需要在脚本运行前手动配置质差
### 无需再手动登录
### 视频播放列表可配置，在 main.py 中修改 play_list 变量
### 每次运行脚本，将自动进行抓包和抓日志，脚本将自动播放 play_list 的每个视频，并将每个视频的流量和日志保存到 'output\视频ID' 目录下
### 目前配置了20个视频，即每次运行脚本将自动在当前的质差条件下采集20组数据

## 依赖
### tshark，需要将 tshark 加入环境变量

## 使用方法
### 1. 在 main.py 中修改 net_interface 变量，为抓包的网卡名，请选择流量经过的网卡，可以通过 'tshark -D' 查看，也可以在 Wireshark 中查看，示例：
### tashark -D:
![Alt text](image.png)
### Wireshark:
![Alt text](image-1.png)
### 2. 手动设置质差，运行 main.py，脚本将自动播放 play_list 中的每个视频，并将每个视频的流量和日志保存到 'output\视频ID' 目录下，运行结束可以将 output 目录重命名，以采集新的数据
### 3. 视频播放过程中请不要将浏览器最小化，最小化时视频会暂停播放，但可以被其他窗口遮挡

## 目前每次运行脚本前还需要手动设置网络质差，后续可能会实现自动设置质差
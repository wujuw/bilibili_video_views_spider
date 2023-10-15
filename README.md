## driver国内镜像
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

现在不需要每次手动登录B站
脚本依赖 tshark 进行抓包，需要将 tshark 加入环境变量

在 main.py 中修改 net_interface 变量，为抓包的网卡名，可以通过 'tshark -D' 查看，也可以在 Wireshark 中查看，示例：
tshark -D:
![Alt text](image.png)
Wireshark:
![Alt text](image-1.png)

在 main.py 中可以通过 play_list 配置播放列表，脚本会自动播放每个视频并自动抓取流量和日志，并将每个视频的流量和日志保存到 'output\视频ID' 目录下

播放过程中请不要将浏览器最小化，最小化是视频会暂停播放，但可以用其他窗口遮挡住浏览器窗口

目前每次运行脚本前还需要手动设置网络质差，后续可能会实现自动设置质差
#from firefox_driver import FirefoxDriver
from chrome_driver import ChromeDriver
from utils.bili_pool import BiliPool

# ip = BiliPool().pool

play_list = [
    'https://www.bilibili.com/video/BV1rw411A7A6', # 动画 31s
    'https://www.bilibili.com/video/BV1ju4y1p7Us', # 鬼畜 27s
    'https://www.bilibili.com/video/BV1Z8411v7yW', # 舞蹈 36s
    'https://www.bilibili.com/video/BV1kB4y1Z7xS', # 娱乐 36s
    'https://www.bilibili.com/video/BV1PN411i7FE', # 科技 46s
    'https://www.bilibili.com/video/BV1RN4y1y7Lh', # 数码 26s
    'https://www.bilibili.com/video/BV1wC4y1d7gX', # 汽车 1m08s
    'https://www.bilibili.com/video/BV1dw411a7VU', # 汽车 33s 
    'https://www.bilibili.com/video/BV1z84116786', # 运动 37s
    'https://www.bilibili.com/video/BV1Rh4y1B7Zi', # 游戏 39s
    'https://www.bilibili.com/video/BV1u8411y7A3', # 音乐 34s
    'https://www.bilibili.com/video/BV1zV4y1Y7W8', # 影视 32s
    'https://www.bilibili.com/video/BV1Gw411c7Aa', # 知识 34s
    'https://www.bilibili.com/video/BV19j411s7Yr', # 资讯 39s
    'https://www.bilibili.com/video/BV1eC4y157jw', # 生活 47s
    'https://www.bilibili.com/video/BV1S34y13737', # 时尚 58s
    'https://www.bilibili.com/video/BV1Rp4y1M7et', # 动物 32s
    'https://www.bilibili.com/video/BV1VN41147kc', # 新闻 29s
    'https://www.bilibili.com/video/BV1zB4y1Z7Sv', # 游戏 33s
    'https://www.bilibili.com/video/BV1Tz4y1V7or', # 动画 37s
]

net_interface = 'WLAN'
# net_interface = '以太网'

#FirefoxDriver().play_loop(ip)
# ChromeDriver().play_loop(ip)
ChromeDriver().play_list(play_list, net_interface=net_interface)
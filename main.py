#from firefox_driver import FirefoxDriver
from chrome_driver import ChromeDriver
from utils.bili_pool import BiliPool

# ip = BiliPool().pool

play_list = [
    'https://www.bilibili.com/video/av430905526',
    'https://www.bilibili.com/video/BV11C4y1R7PT',
    'https://www.bilibili.com/video/BV1kF411U7iv',
    'https://www.bilibili.com/video/BV1R94y1h7qa',
    'https://www.bilibili.com/video/BV13w411U7GG',
    'https://www.bilibili.com/video/BV1Gz4y1F7kk',
    'https://www.bilibili.com/video/BV1KV4y1k7cj',
    'https://www.bilibili.com/video/BV1LX4y1E7PH',
    'https://www.bilibili.com/video/BV1nr4y1o7Fa',
    'https://www.bilibili.com/video/BV1hV411F7bf',
    'https://www.bilibili.com/video/BV1T34y1379J',
    'https://www.bilibili.com/video/BV1cw411y7Be',
    'https://www.bilibili.com/video/BV1Q94y1b7As',
    'https://www.bilibili.com/video/BV1Fu411M7ba',
    'https://www.bilibili.com/video/BV1xz4y1g7dX',
]

net_interface = 'WLAN'

#FirefoxDriver().play_loop(ip)
# ChromeDriver().play_loop(ip)
ChromeDriver().play_list(play_list, net_interface=net_interface)
import time
from chrome_driver import ChromeDriver
import paramiko
import yaml
import threading
import os

configure_file = 'config.yaml'
with open(configure_file, 'r', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    play_list = config['play_list']
    net_interface = config['net_interface']
    play_resolutions = config['play_resolutions']
    fullscreen_play = config['fullscreen_play']
    device_ip = config['device_ip']
    router_lan_interface = config['router_lan_interface']
    net_cond_list = config['net_cond_list']
    ssh_host = config['ssh_host']
    ssh_port = config['ssh_port']
    ssh_username = config['ssh_username']
    ssh_password = config['ssh_password']

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(ssh_host, ssh_port, ssh_username, ssh_password)


def net_cond_configure(net_cond):
    rate = net_cond['rate']
    duration = net_cond['duration']
    ssh_client.exec_command(f'tc qdisc add dev {router_lan_interface} root handle 1: htb default 1')
    ssh_client.exec_command(f'tc class add dev {router_lan_interface} parent 1: classid 1:1 htb rate 10MBps')
    ssh_client.exec_command(f'tc class add dev {router_lan_interface} parent 1: classid 1:2 htb rate {rate}Kbit')
    ssh_client.exec_command(f'tc filter add dev {router_lan_interface} protocol ip parent 1:0 prio 1 u32 match ip dst {device_ip} flowid 1:2')
    time.sleep(duration)
    ssh_client.exec_command(f'tc qdisc del root dev {router_lan_interface}')
    
def net_cond_configure_thread(net_cond):
    threading.Timer(net_cond['start_time'], net_cond_configure, args=(net_cond,)).start()

def net_cond_reset():
    cmd = f'tc qdisc del root dev {router_lan_interface}'
    ssh_client.exec_command(cmd)
    
if not os.path.exists('collection'):
    os.mkdir('collection')

for net_cond in net_cond_list:
    for play_resolution in play_resolutions:
        for ip in play_list:
            net_cond_reset()
            net_cond_configure_thread(net_cond)
            ChromeDriver().play_one(ip, net_interface=net_interface, play_resolution=play_resolution, fullscreen_play=fullscreen_play)
    # move ouput dir to collection/net_cond
    net_cond_str = f'rate_{net_cond["rate"]}Kbit'
    os.rename('output', f'collection/{net_cond_str}')
net_cond_reset()
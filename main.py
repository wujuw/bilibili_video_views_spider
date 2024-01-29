import random
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

stop_flag = False
net_log_name = 'net_cond.log'

def set_rate(rate):
    net_cond_reset()
    ssh_client.exec_command(f'tc qdisc add dev {router_lan_interface} root handle 1: htb default 1')
    ssh_client.exec_command(f'tc class add dev {router_lan_interface} parent 1: classid 1:1 htb rate 10MBps')
    ssh_client.exec_command(f'tc class add dev {router_lan_interface} parent 1: classid 1:2 htb rate {rate}Kbit')
    ssh_client.exec_command(f'tc filter add dev {router_lan_interface} protocol ip parent 1:0 prio 1 u32 match ip dst {device_ip} flowid 1:2')

def net_cond_random_bw_configure(net_cond):
    max_rate = net_cond['max_rate']
    min_rate = net_cond['min_rate']
    change_interval = net_cond['change_interval']
    net_log = open(net_log_name, 'w')
    rate = random.randint(min_rate, max_rate)
    set_rate(rate)
    start_time = time.time()
    net_log.write(f'{start_time}, {rate}Kbps\n')
    while not stop_flag:
        now_time = time.time()
        if now_time - start_time >= change_interval:
            start_time = now_time
            rate = random.randint(min_rate, max_rate)
            set_rate(rate)
            net_log.write(f'{start_time}, {rate}Kbps\n')
        time.sleep(1)
    net_log.close()


def net_cond_configure(net_cond):
    if net_cond['type'] == 'random_bandwidth':
        net_cond_random_bw_configure(net_cond)
    
def net_cond_configure_thread(net_cond):
    return threading.Thread(target=net_cond_configure, args=(net_cond,))

def net_cond_reset():
    cmd = f'tc qdisc del root dev {router_lan_interface}'
    ssh_client.exec_command(cmd)
    
if not os.path.exists('collection'):
    os.mkdir('collection')


# play_list乱序
random.shuffle(play_list)
for net_cond in net_cond_list:
    for play_resolution in play_resolutions:
        for ip in play_list:
            for i in range(0, 20):
                net_cond_reset()
                t = net_cond_configure_thread(net_cond,)
                stop_flag = False
                t.start()
                ChromeDriver(head_less=True).play_one(ip, net_interface=net_interface, play_resolution=play_resolution, fullscreen_play=fullscreen_play)
                stop_flag = True
                t.join()
                video_id = ip.split('/')[-1]
                if os.path.exists(f'output/{play_resolution}/{video_id}'):
                    if os.path.exists(net_log_name):
                        os.rename(net_log_name, f'output/{play_resolution}/{video_id}/{net_log_name}')
                    os.rename(f'output/{play_resolution}/{video_id}', f'output/{play_resolution}/{video_id}_{i+1}')
                if os.path.exists(net_log_name):
                    os.remove(net_log_name)
    # move ouput dir to collection/net_cond
    net_cond_str = f'type_{net_cond["type"]}'
    os.rename('output', f'collection/{net_cond_str}')
net_cond_reset()
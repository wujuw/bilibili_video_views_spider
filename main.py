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

need_unpack_net_conds = [net_cond for net_cond in net_cond_list if net_cond['need_unpack']]
net_cond_list = [net_cond for net_cond in net_cond_list if not net_cond['need_unpack']]
for net_cond in need_unpack_net_conds:
    if net_cond['type'] == 'constant_bandwidth':
        rates = net_cond['rates']
        for rate in rates:
            net_cond_list.append({'type': 'constant_bandwidth', 'rate': rate})

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(ssh_host, ssh_port, ssh_username, ssh_password)
transport = ssh_client.get_transport()
transport.set_keepalive(60)

single_stop_flag = False
net_log_name = 'net_cond.log'
main_stop_flag = False


def exec_command(cmd):
    try:
        ssh_client.exec_command(cmd)
    except Exception as e:
        print(e)
        if not transport.is_active():
            ssh_client.connect(ssh_host, ssh_port, ssh_username, ssh_password)
            transport = ssh_client.get_transport()
            transport.set_keepalive(60)
            exec_command(cmd)

def set_rate(rate):
    net_cond_reset()
    exec_command(f'tc qdisc add dev {router_lan_interface} root handle 1: htb default 1')
    exec_command(f'tc class add dev {router_lan_interface} parent 1: classid 1:1 htb rate 10MBps')
    exec_command(f'tc class add dev {router_lan_interface} parent 1: classid 1:2 htb rate {rate}Kbit')
    exec_command(f'tc filter add dev {router_lan_interface} protocol ip parent 1:0 prio 1 u32 match ip dst {device_ip} flowid 1:2')

def net_cond_random_bw_configure(net_cond):
    max_rate = net_cond['max_rate']
    min_rate = net_cond['min_rate']
    change_interval = net_cond['change_interval']
    net_log = open(net_log_name, 'w')
    rate = random.randint(min_rate, max_rate)
    set_rate(rate)
    start_time = time.time()
    net_log.write(f'{start_time}, {rate}Kbps\n')
    while not single_stop_flag:
        now_time = time.time()
        if now_time - start_time >= change_interval:
            start_time = now_time
            rate = random.randint(min_rate, max_rate)
            set_rate(rate)
            net_log.write(f'{start_time}, {rate}Kbps\n')
        time.sleep(1)
    net_log.close()

def net_cond_constant_bw_configure(net_cond):
    rate = net_cond['rate']
    set_rate(rate)
    net_log = open(net_log_name, 'w')
    net_log.write(f'{time.time()}, {rate}Kbps\n')
    net_log.close()

def net_cond_trace_bw_configure(net_cond):
    trace = net_cond['trace']
    net_log = open(net_log_name, 'w')
    i = 0
    rate, duration = trace[i]
    i += 1
    set_rate(rate)
    net_log.write(f'{time.time()}, {rate}Kbps\n')
    start_time = time.time()
    while not single_stop_flag:
        now_time = time.time()
        if now_time - start_time >= duration:
            if i < len(trace):
                rate, duration = trace[i]
                i += 1
                set_rate(rate)
                net_log.write(f'{now_time}, {rate}Kbps\n')
                start_time = now_time
            else:
                break
        time.sleep(1)
    net_log.close()


def net_cond_configure(net_cond):
    if net_cond['type'] == 'random_bandwidth':
        net_cond_random_bw_configure(net_cond)
    elif net_cond['type'] == 'constant_bandwidth':
        net_cond_constant_bw_configure(net_cond)
    elif net_cond['type'] == 'trace_bandwidth':
        net_cond_trace_bw_configure(net_cond)

def net_cond_to_str(net_cond):
    if net_cond['type'] == 'random_bandwidth':
        return f'random_{net_cond["min_rate"]}KBps_{net_cond["max_rate"]}KBps_{net_cond["change_interval"]}s'
    elif net_cond['type'] == 'constant_bandwidth':
        return f'constant_bandwidth_{net_cond["rate"]}KBps'
    elif net_cond['type'] == 'trace_bandwidth':
        return f'trace_{net_cond["id"]}'
    
def net_cond_configure_thread(net_cond):
    return threading.Thread(target=net_cond_configure, args=(net_cond,))

def net_cond_reset():
    cmd = f'tc qdisc del root dev {router_lan_interface}'
    exec_command(cmd)

# send heartbeat to maintain the ssh connection
def send_heartbeat():
    while not main_stop_flag:
        exec_command('echo 1')
        time.sleep(60)
    
if not os.path.exists('collection'):
    os.mkdir('collection')


# start the heartbeat thread
# heartbeat_t = threading.Thread(target=send_heartbeat)
# heartbeat_t.start()

pause_flag = False

def capture_pause_signal():
    global pause_flag
    while not main_stop_flag:
        if not pause_flag and input('press "p" to pause...\n') == 'p':
            pause_flag = True
        time.sleep(1)

pause_t = threading.Thread(target=capture_pause_signal)
pause_t.start()

# play_list乱序
random.shuffle(play_list)
for net_cond in net_cond_list:
    for play_resolution in play_resolutions:
        for ip in play_list:
            for i in range(0, 4):
                net_cond_reset()
                if pause_flag:
                    input('press any key to continue...\n')
                    pause_flag = False
                t = net_cond_configure_thread(net_cond,)
                single_stop_flag = False
                t.start()
                ChromeDriver(head_less=True).play_one(ip, net_interface=net_interface, 
                                                      play_resolution=play_resolution, 
                                                      fullscreen_play=fullscreen_play,
                                                      timeout=60*4)
                single_stop_flag = True
                t.join()
                video_id = ip.split('/')[-1]
                if os.path.exists(f'output/{play_resolution}/{video_id}'):
                    if os.path.exists(net_log_name):
                        os.rename(net_log_name, f'output/{play_resolution}/{video_id}/{net_log_name}')
                    os.rename(f'output/{play_resolution}/{video_id}', f'output/{play_resolution}/{video_id}_{i+1}')
                if os.path.exists(net_log_name):
                    os.remove(net_log_name)
    # move ouput dir to collection/net_cond
    net_cond_str = net_cond_to_str(net_cond)
    os.rename('output', f'collection/{net_cond_str}_wifi')
net_cond_reset()

main_stop_flag = True
ssh_client.close()
# heartbeat_t.join()
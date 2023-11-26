from chrome_driver import ChromeDriver
# import paramiko
import yaml

configure_file = 'config.yaml'
with open(configure_file, 'r', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    play_list = config['play_list']
    net_interface = config['net_interface']
    play_resolutions = config['play_resolutions']
    fullscreen_play = config['fullscreen_play']
    # net_cond_list = config['net_cond_list']
    # ssh_host = config['ssh_host']
    # ssh_port = config['ssh_port']
    # ssh_username = config['ssh_username']
    # ssh_password = config['ssh_password']

# ssh_client = paramiko.SSHClient()
# ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# ssh_client.connect(ssh_host, ssh_port, ssh_username, ssh_password)


# TODO 自动质差控制
# net_cond_list = []

# def net_cond_configure(net_cond):
#     # send tc command to up-level router
#     # ssh to up-level router
#     # tc command to up-level
#     ssh_client.exec_command('tc qdisc del dev {} root'.format(net_interface))
#     ssh_client.exec_command('tc qdisc add dev {} root handle 1: htb'.format(net_interface))
#     ssh_client.exec_command('tc class add dev {} parent 1: classid 1:1 htb rate {}kbit'.format(net_interface, net_cond['rate']))

for play_resolution in play_resolutions:
    ChromeDriver().play_list(play_list, net_interface=net_interface, play_resolution=play_resolution, fullscreen_play=fullscreen_play)
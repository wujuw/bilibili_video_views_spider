import subprocess
import signal
import time
import paramiko

ssh_host = '192.168.31.1'
ssh_port = 22
ssh_username = 'root'
ssh_password = '4bcc8d55'

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(ssh_host, ssh_port, ssh_username, ssh_password)

device_ip = '192.168.31.56'
rate = 8000
router_lan_interface = 'br-lan'

ssh_client.exec_command(f'tc qdisc del root dev {router_lan_interface}')
ssh_client.exec_command(f'tc qdisc add dev {router_lan_interface} root handle 1: htb default 1')
ssh_client.exec_command(f'tc class add dev {router_lan_interface} parent 1: classid 1:1 htb rate {rate}Kbit')
ssh_client.exec_command(f'tc filter add dev {router_lan_interface} protocol ip parent 1:0 prio 1 u32 match ip dst {device_ip} flowid 1:1')

ssh_client.close()
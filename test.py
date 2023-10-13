import subprocess
import signal
import time

# 启动tshark进程并抓包
tshark_cmd = ['tshark', '-i', 'WLAN', '-w', 'output.pcap']
tshark_proc = subprocess.Popen(tshark_cmd,)

time.sleep(2)

for i in range(2):
    # print(i)
    time.sleep(1)
tshark_proc.send_signal(signal.SIGTERM)
tshark_proc.wait()

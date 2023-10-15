import os
import subprocess

subprocess.call('taskkill /F /IM tshark.exe', shell=True)
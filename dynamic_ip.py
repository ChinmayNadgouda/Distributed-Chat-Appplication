import socket
import subprocess
from subprocess import Popen
import ipaddress
# LocalIP = ''.join(socket.gethostbyname_ex(socket.gethostname())[2])
#
# print(LocalIP)

def get_local_ip_and_broadcast():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 53))
    #print(s.getsockname()[0])

    IP = s.getsockname()[0]
    proc = subprocess.Popen('ipconfig',stdout=subprocess.PIPE)

    while True:
        line = proc.stdout.readline()
        if ip.encode() in line:
            line = proc.stdout.readline()
            break
    MASK = line.rstrip().split(b':')[-1].replace(b' ',b'').decode()
    #print(mask)##


    host = ipaddress.IPv4Address(IP)
    net = ipaddress.IPv4Network(IP + '/' + MASK, False)
    print('IP:', IP)
    print('Mask:', MASK)
    print('Subnet:', ipaddress.IPv4Address(int(host) & int(net.netmask)))
    print('Host:', ipaddress.IPv4Address(int(host) & int(net.hostmask)))
    print('Broadcast:', net.broadcast_address)

    return IP,net.broadcast_address
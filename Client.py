import socket
import multiprocessing
import os
from broadcastsender import broadcast
#from subprocess import run

def send_message(s_address, s_port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        message = 'Hi from ' + str(os.getpid()) + ' at ' + s_address + ':' + str(s_port)
       # message = run("python q2.py",capture_output=True)

        # Send data
        client_socket.sendto(str.encode(message), (s_address, s_port))
        print('Sent to server: ', message)

        # Receive response
        print('Waiting for response...')
        data, server = client_socket.recvfrom(1024)
        print('Received message: ', data.decode())

    finally:
        client_socket.close()
        print('Socket closed')

#def 

if __name__ == '__main__':

    # Bind the socket to the port
    server_address = '127.0.0.1'
    server_port = 10001

    for i in range(3):
        p = multiprocessing.Process(target=send_message, args=(server_address, server_port))
        p.start()
        p.join

    broadcast("192.168.70.255",10001,"hi")

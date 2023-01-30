import socket
import multiprocessing
import os
#from broadcastsender import broadcast
#from subprocess import run

broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
BROADCAST_IP = "192.168.188.255" #needs to be reconfigured depending on network
server_port = 10001
bufferSize  = 1024
#get own IP
MY_HOST = socket.gethostname()
MY_IP = "192.168.188.22" #socket.gethostbyname(MY_HOST)

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

def broadcast(ip, port, broadcast_message):
    # Create a UDP socket
    #broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Send message on broadcast address
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)   #changed_remove
    broadcast_socket.sendto(str.encode(broadcast_message), (ip, port))
    #broadcast_socket.close()

def login(userName):
    message = MY_IP + ',' + userName
    broadcast(BROADCAST_IP, server_port, message)
    broadcast_socket.close()

    client_socket.bind((MY_IP, 5000))

    print('Waiting for response...')
    data, server = client_socket.recvfrom(bufferSize)
    print('Received message: ', data.decode())
    server_ip = data.decode()
    print("Communicate with server: " + server_ip)
    after_login()

def after_login():
    return True



if __name__ == '__main__':

    # Bind the socket to the port


    

    #Input User Information
    userName = input('Enter UserName ')

    login(userName)

    #receive IP of Server where Chatroom runs, opens connection to it

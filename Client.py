import socket
import multiprocessing
import os
#from broadcastsender import broadcast
#from subprocess import run

broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
BROADCAST_IP = "192.168.0.255" #needs to be reconfigured depending on network
server_port = 10001
bufferSize  = 1024
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
    broadcast_socket.sendto(str.encode(broadcast_message), (ip, port))
    #broadcast_socket.close()




if __name__ == '__main__':

    # Bind the socket to the port


    #get own IP
    MY_HOST = socket.gethostname()
    MY_IP = "192.168.0.150" #socket.gethostbyname(MY_HOST)


    #Input User Information
    userName = input('Enter UserName ')

    message = MY_IP + ',' + userName
    broadcast(BROADCAST_IP, server_port, message)
    broadcast_socket.close()

    client_socket.bind((MY_IP, 5000))

    print('Waiting for response...')
    data, server = client_socket.recvfrom(bufferSize)
    print('Received message: ', data.decode())
    serverAdress = data.decode()

    chatID = input('Enter ChatID: ')
    client_socket.sendto(chatID.encode(), (serverAdress,5001))
    client_socket.close()

    #receive IP of Server where Chatroom runs, opens connection to it
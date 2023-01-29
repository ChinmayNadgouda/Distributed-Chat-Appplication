import socket
import multiprocessing
import os
import time
from broadcastsender import broadcast
#from subprocess import run

local_ip = "192.168.188.22"
server_ip = "192.168.188.22"

def chatroom_input(client_id,chatroom_id):
    while(True):
        message_to_send = input("Give your input:")
        if message_to_send == "!exit":
            # send_message() extting
            return True
        else:
            n = 0
            while(n<3):
                send_message(server_ip, 5553, client_id+",send_msg,"+chatroom_id+","+message_to_send)
                data = recieve_message(5566)
                if data == b'sent':
                    n = 100
                    print(data)
                elif data == b'resend':
                    send_message(server_ip, 5553, client_id + ",send_msg," + chatroom_id + "," + message_to_send)
                    n = n + 1
                    print("retry")
                    pass

def chatroom_output():
    send_message(server_ip, 5554,"client_id"+",join"+str(5553)+","+"join")
    while True:
        data = recieve_message()
        if data:
            send_message(server_ip, 5554,"client_id"+",recvd,"+str(5553)+","+"recvd")
            #data_ack2 = recieve_message()
            #if data_ack2 == b'sent':
            #print(data)
        print(data)


def send_message(s_address, s_port, message_to_b_sent):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #  message = 'Hi from ' + str(os.getpid()) + ' at ' + s_address + ':' + str(s_port)
        # # message = run("python q2.py",capture_output=True)

        # Send data
        client_socket.sendto(str.encode(message_to_b_sent+",5565,5566"), (s_address, s_port))
        print('Sent to server: ', message_to_b_sent,s_port)
    finally:
        client_socket.close()
        #print('Socket closed')

def recieve_message(port=5565):
    try:
        # Receive response
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        client_socket.bind((local_ip,port))
        #print('Waiting for response...')
        data, server = client_socket.recvfrom(1024)
        #print('Received message: ', data.decode())

        return data

    finally:
        client_socket.close()
        #print('Socket closed')

#def 
def after_login():
    selection = input("What do you want to enter? \n 1.Output window \n 2.Input Window")
    if selection == '1':
        chatroom_output()
    elif selection == '2':
        selection4 = input("Give Your ID:")
        selection3 = input("Give Chatroom ID:")
        chatroom_input(selection4, selection3)

if __name__ == '__main__':

    # Bind the socket to the port
    server_address = '127.0.0.1'
    server_port = 10001

    # for i in range(3):
    #     p = multiprocessing.Process(target=send_message, args=(server_address, server_port))
    #     p.start()
    #     p.join
    #
    # broadcast("192.168.70.255",10001,"hi")

    after_login()



import socket
import multiprocessing
import os
import time
from broadcastsender import broadcast
#from subprocess import run

def chatroom_input(client_id,chatroom_id):
    while(True):
        message_to_send = input("Give your input:")
        if message_to_send == "!exit":
            return True
        else:

            send_message("127.0.0.1", 5553, client_id+",send_msg,"+chatroom_id+","+message_to_send)

def chatroom_output(state,client_id,chatroom_id=False):
    if state=="create" and not (chatroom_id):
        send_message("127.0.0.1", 5553, client_id + ",get_msg_c")
        chatroom_id = recieve_message()
        while (True):
            time.sleep(1)
            send_message("127.0.0.1", 5553, client_id+",get_msg,"+chatroom_id.decode('utf-8'))
            message_recvd = recieve_message()
            print(message_recvd)
    if state=="join" and chatroom_id:
        previous_messages = fetch_previous_messages(chatroom_id,client_id)
        for message in previous_messages:
            print(message)
        #keep poling for new messages
        while(True):
            time.sleep(1)
            send_message("127.0.0.1", 5553, client_id+",get_msg,"+chatroom_id)
            message_recvd = recieve_message()
            print(message_recvd)

def fetch_previous_messages(chatroom_id,client_id):
    while(True):
        send_message("127.0.0.1",5553,client_id+",fetch_msg,"+chatroom_id)
        message_recieved = recieve_message()
        if message_recieved:
            return message_recieved
        else:
            continue
def send_message(s_address, s_port, message_to_b_sent):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #  message = 'Hi from ' + str(os.getpid()) + ' at ' + s_address + ':' + str(s_port)
        # # message = run("python q2.py",capture_output=True)

        # Send data
        client_socket.sendto(str.encode(message_to_b_sent), (s_address, s_port))
        print('Sent to server: ', message_to_b_sent)
    finally:
        client_socket.close()
        print('Socket closed')

def recieve_message():
    try:
        # Receive response
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.bind(("127.0.0.1",5554))
        print('Waiting for response...')
        data, server = client_socket.recvfrom(1024)
        print('Received message: ', data.decode())

        return data

    finally:
        client_socket.close()
        print('Socket closed')

#def 
def after_login():
    selection = input("What do you want to enter? \n 1.Output window \n 2.Input Window")
    if selection == '1':
        selection2 = input("Do you want to \n 1. Join Chat Room? \n 2. Create Chat Room?")
        if selection2 == '1':
            selection4 = input("Give Your ID:")
            selection3 = input("Give Chatroom ID:")
            chatroom_output('join', selection4, selection3)
        elif selection2 == '2':
            selection4 = input("Give Your ID:")
            chatroom_output('create',selection4)
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



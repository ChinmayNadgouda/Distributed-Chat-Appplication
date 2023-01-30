import socket
import multiprocessing
import os
import time
#from broadcastsender import b
import queue
#from subprocess import run

local_ip = "192.168.1.103"
server_ip = "192.168.1.105"

vector = {}
""""
# Define the client's vector clock
vector_clock = multiprocessing.Manager().dict()

# Define the message queue
message_queue = multiprocessing.Queue()

# Ordering of the message
def process_messages(vector_clock, message_queue):
    while True:
        message = message_queue.get()
        if message is None:
            break

        # Update the client's vector clock with the message's vector clock
        for key in message['vector_clock']:
            if key in vector_clock:
                vector_clock[key] = max(vector_clock[key], message['vector_clock'][key])
            else:
                vector_clock[key] = message['vector_clock'][key]

        # Process the message
        print(message['content'])
"""

def chatroom_input(client_id,chatroom_id):

    while(True):
        message_to_send = input("Give your input:")
        if message_to_send == "!exit":
            return True
        else:
            #increment vc at pointer send with message
            send_message(server_ip, 5553, client_id+",send_msg,"+chatroom_id+","+message_to_send )
            data = recieve_message(5566)
            print(data)
vector_clock[]
pointer
def chatroom_output():
    #join and no incre
    #vc and pointer
    while True:
        
        data = recieve_message()
        if data:
            #vector
            #pointer
            #max of vector
            #increment vc at given pointer and dont send
            send_message(server_ip, 5554,"client_id"+",recvd,"+str(5553)+","+"recvd")
        print(data)


def send_message(s_address, s_port, message_to_b_sent, ):
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
        #client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

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








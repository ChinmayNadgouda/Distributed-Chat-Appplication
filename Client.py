import pickle
import socket
import multiprocessing
import os
#from broadcastsender import broadcast
#from subprocess import run

#broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  #changed_remove
#client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  #changed_remove
import threading

BROADCAST_IP = "192.168.188.255" #needs to be reconfigured depending on network
server_port = 10001
bufferSize  = 1024
#get own IP
MY_HOST = socket.gethostname()
MY_IP = "192.168.188.22" #socket.gethostbyname(MY_HOST)
local_ip = MY_IP
client_inport = 5566
client_outport = 5565
server_ip = ""
server_inport = 0
server_outport =  0
def chatroom_input():
    while(True):
        message_to_send = input("Give your input:")
        if message_to_send == "!exit":
            # send_message() extting
            return True
        else:
            send_message(server_ip, server_inport, "client_id"+",send_msg,"+"chatroom_id"+","+message_to_send)
            data = recieve_message(client_inport)
            if data == b'sent':
                print(data)
            elif data == False:
                continue
            else:
                send_message(server_ip, server_inport, "client_id" + ",send_msg," + "chatroom_id" + "," + message_to_send)
                data = recieve_message(client_outport)
                print(data)


def chatroom_output():
    #send_message(server_ip, inport,"client_id"+",join,"+str(inport)+","+"join")
    while True:
        data = recieve_message(client_outport)
        if data:
            send_message(server_ip, server_outport,"client_id"+",recvd,"+str(server_inport)+","+"recvd")
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
        client_socket.sendto(str.encode(message_to_b_sent+","+str(client_outport)+","+str(client_inport)), (s_address, s_port))  #not needed
        print('Sent to server: ', message_to_b_sent,s_port)
    finally:
        client_socket.close()
        #print('Socket closed')

def recieve_message(port=5565):
    try:
        # Receive response and set timeout for every 5 sec
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        client_socket.settimeout(5)
        client_socket.bind((local_ip,port))
        #print('Waiting for response...')
        data, server = client_socket.recvfrom(1024)
        #print('Received message: ', data.decode())

        return data
    except socket.timeout:
        return False
    finally:
        client_socket.close()
        #print('Socket closed')

#def
def after_login():
    selection = input("What do you want to enter? \n 1.Output window \n 2.Input Window")
    if selection == '1':
        chatroom_output()
    elif selection == '2':
        client_id = input("Give Your ID:")
        chatroom_input()



#def 

def broadcast(ip, port, broadcast_message,broadcast_socket):
    # Create a UDP socket
    #broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Send message on broadcast address
    #broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)   #changed_remove
    if type(broadcast_message) == str:
        broadcast_socket.sendto(str.encode(broadcast_message), (ip, port))
    else:
        broadcast_socket.sendto(broadcast_message, (ip, port))
#     #broadcast_socket.close()
def keep_listening_to_leader():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind((MY_IP, 10002))       #willl need another socket and port
    print('always Waiting for response...')
    data, server = client_socket.recvfrom(bufferSize)
    #got new server
    client_socket.close()
    print(data)

    #get the server ip, in port and out port and update current values
def login(userName):
    message = MY_IP + ',' + userName
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # changed_remove
    broadcast(BROADCAST_IP, server_port, message,broadcast_socket) # changed_remove
    broadcast_socket.close()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind((MY_IP, 5000))

    print('Waiting for response...')
    data, server = client_socket.recvfrom(bufferSize)
    client_socket.close()
    server_list = pickle.loads(data)
    print('Select a server id  and corresponding chatroom id (inport) to get into a chatroom: ', server_list)
    selected_server = input("Give the server ip:  ")
    selected_chatroom = input("Give the chatroom id (inport):  ")
    for chatrooms in server_list[int(selected_server)]['chatrooms_handled']:
        if chatrooms['inPorts'][0] == int(selected_chatroom):
            print("here.///////////////")
            inport = chatrooms['inPorts']
            outport = chatrooms['outPorts']
            server_ip = server_list[int(selected_server)]['IP']

    # server_ip = data.decode()
    # print("Communicate with server: " + server_ip)
    #later loop inports and outpots to select which chatroom
    print(inport[0],outport[0])
    server_inport = inport[0]
    server_outport = outport[0]
    client = {'IP': MY_IP, "inPorts": client_inport , "outPorts": client_outport, "selected_server":selected_server, "selected_chatroom": inport[0]}
    client_object = pickle.dumps(client)
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # changed_remove
    broadcast(BROADCAST_IP, server_port, client_object, broadcast_socket)  # changed_remove

    broadcast_socket.close()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind((MY_IP, 5000))

    print('Waiting for response...')
    data, server = client_socket.recvfrom(bufferSize)
    client_socket.close()
    print(data)
    return server_ip, server_inport,server_outport
    #time.sleep(10)
    #after_login(inport[0],outport[0])

# def after_login():
#     return True



if __name__ == '__main__':

    # Bind the socket to the port


    

    #Input User Information
    userName = input('Enter UserName ')
    server_ip,server_inport,server_outport = login(userName)
    while True:
        p_leader_listen = threading.Thread(target=keep_listening_to_leader,args=())
        p_leader_listen.start()

        p_chat = threading.Thread(target=after_login, args=())
        p_chat.start()

        p_leader_listen.join()
        p_chat.join()
    #receive IP of Server where Chatroom runs, opens connection to it



import socket
import multiprocessing
import os
import time
from broadcastsender import broadcast
#from subprocess import run

local_ip = "192.168.188.22"
server_ip = "192.168.188.22"



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
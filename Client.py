import pickle
import socket
import multiprocessing
import os
from queue import Queue
import json
#from broadcastsender import broadcast
#from subprocess import run

#broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  #changed_remove
#client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  #changed_remove
import threading

BROADCAST_IP = "192.168.43.255" #needs to be reconfigured depending on network

bufferSize  = 1024
#get own IP
MY_HOST = socket.gethostname()
MY_IP = "192.168.43.205"#socket.gethostbyname(MY_HOST)
local_ip = MY_IP
client_inport = 5566
client_outport = 5565

#To implement the causality.


class Client():
    server_port = 10001
    server_inport = 0
    server_outport =  0
    server_ip = ''

    #Dictionary to store vector clock.
    vector_clock = {}
    rcvd_vc = {}
    holdback_q = Queue()
    delivery_q = Queue()

    def __init__(self):
        pass

    def update_vector_clock(self, rcvd_vc):
        for ip, value in rcvd_vc.items():
            if ip not in self.vector_clock:
                self.vector_clock[ip] = value
            else:
                #ToDo: Verify the usage!
                self.vector_clock[ip] = max(self.vector_clock[ip], rcvd_vc[ip]) 

    def check_if_new_client(self, rcvd_vc):
        for ip, value in rcvd_vc.items():
            if ip not in self.vector_clock:
                self.vector_clock[ip] = 0

    def increment_vector_clock(self):
        if local_ip not in self.vector_clock:
            self.vector_clock[local_ip] = 0

        self.vector_clock[local_ip] += 1   

    def save_vector_clock(self):
        with open("vector_clock.json", "w") as file:
            json.dump(self.vector_clock, file)

    def load_vector_clock(self):
        with open("vector_clock.json", "r") as file:
            self.vector_clock = json.load(file)

    def hold_back_processing(self):
        try:

            if self.holdback_q.empty():
                self.hold_back_processing()
            else:
                print("HB+Q",self.holdback_q)
            self.load_vector_clock()
            list = self.holdback_q.get_nowait()
            message = list[0]
            rcvd_vc_data=list[1]
            cl_ip = list[2]
            if(self.vector_clock[cl_ip] + 1 == rcvd_vc_data[cl_ip]):     
                self.increment_vector_clock()
                self.update_vector_clock(rcvd_vc_data)
                self.save_vector_clock()
                self.delivery_q.put_nowait(message)
            else:
                self.holdback_q.put_nowait([message,rcvd_vc_data,cl_ip])
        except RecursionError:
            self.hold_back_processing()

    def chatroom_input(self):
        while(True):
            p_leader_listen = threading.Thread(target=client.keep_listening_to_leader,args=(False,))
            p_leader_listen.start()
            message_to_send = input("Give your input:")
            if message_to_send == "!exit":
                # send_message() extting
                return True
            else:
                # Directly increment vc, save the vector clock in a file and send it with the message.
                self.increment_vector_clock()
                self.save_vector_clock()  
                f= open('vector_clock.json', 'r')
                vc_data = f.read()
                f.close()
                print("vector clock data pushed is\n", vc_data)

                self.send_message(self.server_ip, self.server_inport, "client_id"+",send_msg,"+"chatroom_id"+","+message_to_send+","+vc_data)
                data = self.recieve_message(client_inport)
                if data == b'sent':
                    print("[IN]",data)
                elif data == False:
                    continue
                else:
                    self.send_message(self.server_ip, self.server_inport, "client_id" + ",send_msg," + "chatroom_id" + "," + message_to_send+","+vc_data)
                    data = self.recieve_message(client_outport)
                    print("[IN]",data)


    def chatroom_output(self):
        #send_message(self.server_ip, inport,"client_id"+",join,"+str(inport)+","+"join")
        try:
            while True:
                p_leader_listen = threading.Thread(target=client.keep_listening_to_leader,args=(True,))
                p_leader_listen.start()
                data = self.recieve_message(client_outport)
                print('Listening to server',self.server_ip)

                if data:
                    rcvd_msg = data.decode().split(",")

                    message = rcvd_msg[0]
                    rcvd_vc_data = rcvd_msg[1]
                    cl_ip = rcvd_msg[2]

                    self.rcvd_vc = json.loads(rcvd_vc_data)
                    self.load_vector_clock()

                    self.check_if_new_client(self.rcvd_vc)

                    # handle the delivery and hbq continously.
                    
                    #if rcvd vector === our vector means message is duplicate and discard
                    #but if rcvd vector === our vector and cl_ip is our own ip print it and continue

                    if(self.vector_clock[cl_ip] + 1 == self.rcvd_vc[cl_ip]):

                        self.increment_vector_clock()
                        self.update_vector_clock(self.rcvd_vc)
                        self.save_vector_clock()



                        self.delivery_q.put_nowait(message)

                    else:
                        self.increment_vector_clock()
                        #self.update_vector_clock(self.rcvd_vc)
                        self.save_vector_clock()

                        self.holdback_q.put_nowait([message, self.rcvd_vc,cl_ip])
                    if self.delivery_q.empty():
                        continue
                    message_to_be_sent = self.delivery_q.get_nowait()

                    if (message_to_be_sent != None):

                        self.send_message(self.server_ip, self.server_outport,"client_id"+",recvd,"+str(self.server_inport))
                        #data_ack2 = recieve_message()
                        #if data_ack2 == b'sent':
                        #print(data)
                        print("[OUT]",message_to_be_sent)
        except Exception as e:
            print("Queue exception",e)

    def send_message(self,s_address, s_port, message_to_b_sent):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            #  message = 'Hi from ' + str(os.getpid()) + ' at ' + s_address + ':' + str(s_port)
            # # message = run("python q2.py",capture_output=True)

            # Send data
            client_socket.sendto(str.encode(message_to_b_sent+","+str(client_outport)+","+str(client_inport)), (s_address, s_port))  #not needed
            print('Sent to server {}:{}:  {}'.format( s_address,s_port,message_to_b_sent))
        finally:
            client_socket.close()
            #print('Socket closed')

    def recieve_message(self,port=5565):
        try:
            # Receive response and set timeout for every 5 sec
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

    def after_login(self):
        selection = input("What do you want to enter? \n 1.Output window \n 2.Input Window")
        if selection == '1':
            #starthere
            hold_back_processing_thread = threading.Thread(target=client.hold_back_processing ,args=())
            hold_back_processing_thread.start()
            self.chatroom_output()
        elif selection == '2':
            client_id = input("Give Your ID:")
            self.chatroom_input()


    def broadcast(self,ip, port, broadcast_message,broadcast_socket):
        # Create a UDP socket
        #broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Send message on broadcast address
        #broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)   #changed_remove
        if type(broadcast_message) == str:
            broadcast_socket.sendto(str.encode(broadcast_message), (ip, port))
        else:
            broadcast_socket.sendto(broadcast_message, (ip, port))
    #     #broadcast_socket.close()
    def keep_listening_to_leader(self,output_input):
        if output_input:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client_socket.bind((MY_IP, 10002))       #willl need another socket and port
            print('always Waiting for response...')
            data, server = client_socket.recvfrom(bufferSize)
            #got new server
            client_socket.close()
            print("NEW SERVER IP FOR CHATROOM",data.decode())
            self.server_ip = data.decode()
        else:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client_socket.bind((MY_IP, 10003))       #willl need another socket and port
            print('always Waiting for response...')
            data, server = client_socket.recvfrom(bufferSize)
            #got new server
            client_socket.close()
            print("NEW SERVER IP FOR CHATROOM", data.decode())
            self.server_ip = data.decode()

        #get the server ip, in port and out port and update current values
    def login(self,userName):
        message = MY_IP + ',' + userName
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # changed_remove
        self.broadcast(BROADCAST_IP, self.server_port, message,broadcast_socket) # changed_remove
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
                print("Configuring the chatroom")
                inport = chatrooms['inPorts']
                outport = chatrooms['outPorts']
                self.server_ip = server_list[int(selected_server)]['IP']

        # server_ip = data.decode()
        # print("Communicate with server: " + server_ip)
        #later loop inports and outpots to select which chatroom
        print("Chatroom available on ports  [IN]:[OUT] - ",inport[0],outport[0])
        self.server_inport = inport[0]
        self.server_outport = outport[0]
        client = {'IP': MY_IP, "inPorts": client_inport , "outPorts": client_outport, "selected_server":selected_server, "selected_chatroom": inport[0]}
        client_object = pickle.dumps(client)
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # changed_remove
        self.broadcast(BROADCAST_IP, self.server_port, client_object, broadcast_socket)  # changed_remove

        broadcast_socket.close()
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.bind((MY_IP, 5000))

        print('Waiting for response...')
        data, server = client_socket.recvfrom(bufferSize)
        client_socket.close()
        print(data)
        return self.server_ip, self.server_inport,self.server_outport
        #time.sleep(10)
        #after_login(inport[0],outport[0])

    # def after_login():
    #     return True

if __name__ == '__main__':

    # Bind the socket to the port
    client = Client()
    #Input User Information
    userName = input('Enter UserName ')
    client.server_ip,client.server_inport,client.server_outport = client.login(userName)
    while True:
        
        p_chat = threading.Thread(target=client.after_login, args=())
        p_chat.start()
        
        p_chat.join()
    #receive IP of Server where Chatroom runs, opens connection to it

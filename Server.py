"""
A class for the Server module which will handle the chat application
"""
import queue
import sqlite3
import socket
import time
#from broadcastlistener import broadcast_listener
import multiprocessing
from multiprocessing.pool import ThreadPool
import threading
localIP     = "192.168.188.22"
leader_ip = "192.168.188.22"
localPort   = 5553
local_server_port = 4443

bufferSize  = 1024
import datetime
proc_queue = multiprocessing.Queue(maxsize=100)
class Server():
    #to determine if the leader has been elected
    is_leader = True
    me_leader = False # not necessary
    #ip/id of the leader selected
    leader = ""
    #ip of the server itself
    ip_address = "127.0.0.1" #get_ip
    #server id
    server_id = "12012023_1919"

    #ip and id of each server in the group
    group_view = {}
    ack_counter = {}
    #ip of clients assigned to the server, is a set  {"127.0.0.1:5343"}  "ip_addr:port"
    clients_handled = [] #{"192.168.188.22:5553":"192.168.188.29,192.168.188.22","192.168.188.28:6663":False,"192.168.188.29:7773":False}
    #ip of the whole server group, is a set {"127.0.0.1:1232:0"}  "ip_addr:port:heartbeatmisscount"
    server_list = {"192.168.188.22:4443":"True","192.168.188.28:4443":"False","192.168.188.29:4443":"False"}
    server_heatbeat_list = {}
    previous_message = ""


    def __init__(self):
        pass
        #braodcast
        #update_groupview
        #start_heartbeat on one port
        #listen_to_clients on one port



    #get the messaged passed from clients ( have a message queue )
    def read_client(self,port,heartbeat_leader=False,heatbeat_server=False):
        try:
            UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            #UDPServerSocket.setblocking(0)
            if heartbeat_leader:
               UDPServerSocket.settimeout(1)
            if heatbeat_server:
                UDPServerSocket.settimeout(15)
            UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            #UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            UDPServerSocket.bind((localIP, port))
            #keep listening and get the message from clinet
            bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

            message = bytesAddressPair[0]

            address = bytesAddressPair[1]

            clientMsg = "Message from Client:{}".format(message)
            clientIP = "Client IP Address:{}".format(address)

            print(clientMsg)
            print(clientIP)

            UDPServerSocket.close()

            return [address,message]
        except socket.timeout:
            return False
        except Exception as e:
            print('Recving error: ',e)

    def write_to_client(self,server_message,client_ip,client_port):
        # Sending a reply to client
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #UDPServerSocket.bind((client_ip, client_port))
        bytesToSend = str.encode(server_message)

        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.sendto(bytesToSend, (client_ip,client_port))
        print("sent {} to client {} {}".format(bytesToSend,client_ip,client_port))
        UDPServerSocket.close()
        return True
        #pass

    def write_to_client_with_ack(self,server_message,client_ip,client_port):
        # Sending a reply to client
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # UDPServerSocket.bind((client_ip, client_port))
        bytesToSend = str.encode(server_message)

        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.sendto(bytesToSend, (client_ip, client_port))
        print("sent {} to client {} {}".format(bytesToSend, client_ip, client_port))
        UDPServerSocket.close()
        pool = ThreadPool(processes=1)

        async_result = pool.apply_async(self.read_client, (client_port, True, False))  # tuple of args for foo

        # do some other stuff in the main process

        ack_thread = async_result.get()
        if ack_thread:
            if ack_thread[1] == b'recvd':
                self.ack_counter[localPort] = self.ack_counter[localPort] + 1
        return True
        # pass

    def parse_client_message(self,client_recv_data):
        #print(client_recv_data)
        data_list = client_recv_data.split(",")
        #print(data_list)
        client_id = data_list[0]
        client_req = data_list[1]
        chatroom_id = data_list[2]
        client_message = data_list[3]
        client_port = data_list[-1]
        return [client_id,client_req,chatroom_id,client_message,client_port]


    def read_client_tcp(self,client_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((localIP,client_port))
        sock.listen(1)
        connection, client_address = sock.accept()
        data = connection.recv(1024)
        return [connection,data]
    def write_to_client_tcp(self,connection,data):
        connection.sendall(data)
        connection.close()
    def write_to_chatroom(self):
        while True:
            bytesAddressPair = self.read_client(localPort)

            print(bytesAddressPair)
            message_from_client = bytesAddressPair[1].decode('utf-8')
            # print(type(message_from_client),"tt")
            client_ip = bytesAddressPair[0][0]
            print(client_ip)
            client_id, data, chatroom_id, message, port = self.parse_client_message(message_from_client)
            print('D',data)
            self.clients_handled.append(client_ip+":"+port)
            clients_set = set(self.clients_handled)
            self.ack_counter[localPort] = 0
            for client in clients_set:
                client_addr = client.split(":")
                client_ip = client_addr[0]
                client_port = int(client_addr[1])
                thread = threading.Thread(target=self.write_to_client_with_ack,args=(message,client_ip,client_port,))
                thread.start()
                thread.join()

            if self.ack_counter[localPort] == len(clients_set):
                thread = threading.Thread(target=self.write_to_client, args=("sent", client_ip, client_port,))
                thread.start()
                thread.join()
            else:
                thread = threading.Thread(target=self.write_to_client, args=("please re-send", client_ip, client_port,))
                thread.start()
                thread.join()
    def heart_beat_recving(self):
        while True:
            leader_heartbeat = self.read_client(local_server_port,heartbeat_leader=False,heatbeat_server=True)
            if leader_heartbeat:
                if leader_heartbeat[1] == b'heartbeat':
                    thread = threading.Thread(target=self.write_to_client, args=('heartbeat_recvd', leader_ip, local_server_port,))
                    thread.start()
                    thread.join()
            else:
                print('Leader is dead,start election')
    def heart_beating(self):
        while True:
            time.sleep(10) #heartbeats after 60 seconds
            for server in self.server_list:

                server_addr = server.split(":")
                server_ip = server_addr[0]
                server_port = int(server_addr[1])
                if server_ip != localIP:
                    thread = threading.Thread(target=self.write_to_client,args=("heartbeat",server_ip,server_port,))
                    thread.start()

                    pool = ThreadPool(processes=1)

                    async_result = pool.apply_async(self.read_client, (local_server_port,True,False))  # tuple of args for foo

                    # do some other stuff in the main process

                    listen_heartbeat = async_result.get()


                    if listen_heartbeat:
                        if listen_heartbeat[1] == b'heartbeat_recvd':
                            print("Server {} is alive:".format(server_ip))
                            self.server_heatbeat_list[server_ip] = 0
                    else:
                        if self.server_heatbeat_list[server_ip] > 3:
                            print("Server {} is dead:".format(server_ip))
                            self.server_heatbeat_list[server_ip] = 0
                            #inform all other servers
                            #redirect client to new server
                        self.server_heatbeat_list[server_ip] = self.server_heatbeat_list[server_ip] + 1

    def heartbeat_mechanism(self,serve):

        if self.is_leader:
            for server in self.server_list:

                server_addr = server.split(":")
                server_ip = server_addr[0]
                self.server_heatbeat_list[server_ip] = 0
            serve.heart_beating()
        else:
            serve.heart_beat_recving()

if __name__ == "__main__":
    Leader = True
    serve = Server()
    #group_view = broadcast()
    #serve.server_list = group_view

    # p_heartbeat = multiprocessing.Process(target=serve.heartbeat_mechanism,args=(serve,))
    # p_heartbeat.start()
    #serve.heartbeat_mechanism()
    p_chat = multiprocessing.Process(target=serve.write_to_chatroom, args=())
    p_chat.start()
    #serve.write_to_chatroom()
    #p_heartbeat.join()

    #broadcast_listener()
    ############################
    ##testcode
    ##########################
    # while(False):
    #     #serve.write_to_chatroom(5553)
    #     process = []
    #     client_port = [5553,5555]
    #     i = 0
    #     for port in client_port:
    #         process.append(multiprocessing.Process(target=serve.write_to_chatroom, args=(port,)))
    #
    #         process[i].start()
    #
    #         i = i + 1
    #     i=0
    #     for port in client_port:
    #         process[i].join()
    #         i=i+1


    #     serve.broadcast_listener

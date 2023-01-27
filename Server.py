"""
A class for the Server module which will handle the chat application
"""
import queue
import sqlite3
import socket
import time
from broadcastlistener import broadcast_listener
import multiprocessing
import threading
localIP     = "192.168.188.22"

localPort   = 5553

bufferSize  = 1024
import datetime
proc_queue = multiprocessing.Queue(maxsize=100)
class Server():
    #to determine if the leader has been elected
    is_leader = False
    me_leader = False # not necessary
    #ip/id of the leader selected
    leader = ""
    #ip of the server itself
    ip_address = "127.0.0.1" #get_ip
    #server id
    server_id = "12012023_1919"

    #ip and id of each server in the group
    group_view = {}
    #ip of clients assigned to the server
    clients_handled = []

    previous_message = ""


    def __init__(self):
        pass
        #braodcast
        #update_groupview
        #start_heartbeat on one port
        #listen_to_clients on one port



    #get the messaged passed from clients ( have a message queue )
    def read_client(self):
        try:
            UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            #UDPServerSocket.setblocking(0)
            #UDPServerSocket.settimeout(1)
            UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            UDPServerSocket.bind((localIP, localPort))
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
        except Exception as e:
            print('Recving error: ',e)

    def write_to_client(self,server_message):
        # Sending a reply to client
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #UDPServerSocket.bind((client_ip, client_port))
        bytesToSend = str.encode(server_message)
        for client in self.clients_handled:
            UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            client_ip = client[0]
            client_port = client[1]
            UDPServerSocket.sendto(bytesToSend, (client_ip,client_port))
            print("sent {} to client {} {}".format(bytesToSend,client_ip,client_port))
            UDPServerSocket.close()
        return True
        #pass


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



    def write_to_chatroom(self):
        while True:
            bytesAddressPair = self.read_client()

            print(bytesAddressPair)
            message_from_client = bytesAddressPair[1].decode('utf-8')
            # print(type(message_from_client),"tt")
            client_ip = bytesAddressPair[0][0]
            print(client_ip)
            client_id, data, chatroom_id, message, port = self.parse_client_message(message_from_client)
            print('D',data)
            self.clients_handled.append([client_ip,int(port)])
            thread = threading.Thread(target=self.write_to_client,args=(message,))
            thread.start()
            thread.join()

if __name__ == "__main__":

    serve = Server()

    serve.write_to_chatroom()
    # p_heartbeat = multiprocessing.Process(target=serve.heartbeats,args=())
    # p_heartbeat.start()

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

"""
A class for the Server module which will handle the chat application
"""
import queue
import sqlite3
import socket
import time
from broadcastlistener import broadcast_listener
import multiprocessing
localIP     = "192.168.64.2"

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
    ip_address = "127.0.0.1"
    #server id
    server_id = "12012023_1919"
    #ip and id of each server in the group
    group_view = {}
    #ip of clients assigned to the server
    clients_handled = []
    #chatroom ids handled by a server
    chatrooms_handled = []
    previous_message = ""
    #UDPServerSocket = None

    def __init__(self):
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)



    #get the messaged passed from clients ( have a message queue )
    def read_client(self,client_port):
        try:
            UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            #UDPServerSocket.setblocking(0)
            UDPServerSocket.settimeout(1)
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
            proc_queue.put([message,address])
            # message_from_client = bytesAddressPair[0].decode('utf-8')
            # # print(type(message_from_client),"tt")
            # client_ip = bytesAddressPair[1][0]
            # print(client_ip)
            # data,port = self.parse_client_message(message_from_client, client_ip)
            # # print(data)
            # #print(port)
            # self.write_to_client(client_ip, int(port), data)
            #return [address,message]
        except socket.timeout:
            self.read_client(client_port)

    def write_to_client(self,client_ip,client_port,server_message):
        # Sending a reply to client
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #UDPServerSocket.bind((client_ip, client_port))
        bytesToSend = str.encode(server_message)

        UDPServerSocket.sendto(bytesToSend, (client_ip,client_port))
        print("sent {} to client {} {}".format(bytesToSend,client_ip,client_port))
        UDPServerSocket.close()
        return True
        #pass

    def connect_to_db(self,db_name):
        connection = sqlite3.connect("./db/"+db_name)
        return connection

    def create_chatroom(self,chatroom_id):
        #create table local/remote and send mapping to leader
        conn = self.connect_to_db('servername.db')
        with conn:
            conn.execute('CREATE TABLE IF NOT EXISTS {} (chatroom_id INT, message_id VARCHAR, sender_ip VARCHAR, vector_clock VARCHAR, message_content VARCHAR)'.format('CHATROOM_'+str(chatroom_id)))
        return True

    def write_to_chatroom_table(self,chatroom_id,message_id,sender_ip,vector_clock,content):
        conn = self.connect_to_db('servername.db')
        with conn:
            cmd = 'INSERT INTO {} (chatroom_id,message_id,sender_ip,vector_clock,message_content) VALUES ({},\'{}\',\'{}\',\'{}\',\'{}\');'.format('CHATROOM_'+str(chatroom_id),int(chatroom_id),message_id,sender_ip,vector_clock,content)
            print(cmd)
            conn.execute(cmd)

    def read_from_chatroom(self,chatroom_id,all,message_id=False):
        conn = self.connect_to_db('servername.db')
        with conn:
            if all:
                data = conn.execute(
                'SELECT * FROM {}'.format('CHATROOM_'+str(chatroom_id))
            )
            else:
                data = conn.execute(
                'SELECT * FROM {} ORDER BY rowid DESC LIMIT 1'.format('CHATROOM_' + str(chatroom_id))
            )
        return data

    def parse_client_message(self,client_recv_data,client_ip=""):
        #print(client_recv_data)
        data_list = client_recv_data.split(",")
        #print(data_list)
        if data_list[1] == 'send_msg' and client_ip != "":
            client_id = data_list[0]
            chatroom_id = data_list[2]
            message = data_list[3]
            message_id = '1' #way to generate unique message ids
            self.write_to_chatroom_table(chatroom_id,message_id,client_ip,'[0,0,0]',message)
            return ("sent",data_list[-1])
        elif client_ip == "":
            print("Didnt Get client IP..so aborting, please resend message")
            return  "Didnt Get client IP..so aborting, please resend message"
        if data_list[1] == 'get_msg':
            client_id = data_list[0]
            chatroom_id = data_list[2]
            all_chat_data = self.read_from_chatroom(chatroom_id,False)
            send_data = ""
            for row in all_chat_data:
                #print(send_data, row[2], row[4])
                message_is = row[4]
                send_data = send_data +"From : " +row[2] +"Message : "+row[4] +"\n"
                self.previous_message = message_is

            return (send_data,data_list[-1]) #sending port along with msg so that server can send it to client directly
        if data_list[1] == 'get_msg_c':
            client_id = data_list[0]
            chatroom_id = '1' #way to get unique chatroom id
            print('here')
            self.create_chatroom(chatroom_id)
            return (chatroom_id,data_list[-1])
        if data_list[1] == 'fetch_msg':
            client_id = data_list[0]
            chatroom_id = data_list[2]
            all_chat_data = self.read_from_chatroom(chatroom_id,True)
            send_data = ""
            for row in all_chat_data:
                #print(send_data, row[2], row[4])
                send_data = send_data + "From : " + row[2] + "Message : " + row[4] + "\n"

            return (send_data,data_list[-1])



    def write_to_chatroom(self,port):
        while True:
            self.read_client(port)
            # while(proc_queue.qsize()>0):
            bytesAddressPair = proc_queue.get()
            message_from_client = bytesAddressPair[0].decode('utf-8')
            # print(type(message_from_client),"tt")
            client_ip = bytesAddressPair[1][0]
            print(client_ip)
            data, port = self.parse_client_message(message_from_client, client_ip)
            # print(data)
            # print(port)
            self.write_to_client(client_ip, int(port), data)

if __name__ == "__main__":

    serve = Server()

    p = multiprocessing.Process(target=serve.write_to_chatroom,args=(5555,))
    # p_heartbeat = multiprocessing.Process(target=serve.heartbeats,args=())
    # p_heartbeat.start()
    p.start()
    p.join()
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

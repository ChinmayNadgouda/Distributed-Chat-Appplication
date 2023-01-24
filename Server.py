"""
A class for the Server module which will handle the chat application
"""
import sqlite3
import socket
import time
from broadcastlistener import broadcast_listener
localIP     = "127.0.0.1"

localPort   = 5553

bufferSize  = 1024

import datetime

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

    #UDPServerSocket = None

    def __init__(self):
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)



    #get the messaged passed from clients ( have a message queue )
    def read_client(self):
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
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

    def write_to_client(self,client_ip,client_port,server_message):
        # Sending a reply to client
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #UDPServerSocket.bind((client_ip, client_port))
        bytesToSend = str.encode(server_message)

        UDPServerSocket.sendto(bytesToSend, (client_ip,client_port))
        print("sent {} to client".format(bytesToSend))
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
            if(all):
                data = conn.execute(
                'SELECT * FROM {}'.format('CHATROOM_'+str(chatroom_id))
            )
            else:
                data = conn.execute(
                'SELECT * FROM {} ORDER BY rowid DESC LIMIT 1'.format('CHATROOM_' + str(chatroom_id))
            )
        return data

    def parse_client_message(self,client_recv_data,client_ip=""):
        print(client_recv_data)
        data_list = client_recv_data.split(",")
        print(data_list)
        if data_list[1] == 'send_msg' and client_ip != "":
            client_id = data_list[0]
            chatroom_id = data_list[2]
            message = data_list[3]
            message_id = '1' #way to generate unique message ids
            self.write_to_chatroom_table(chatroom_id,message_id,client_ip,'[0,0,0]',message)
            return "sent"
        elif client_ip == "":
            print("Didnt Get client IP..so aborting, please resend message")
            return  "Didnt Get client IP..so aborting, please resend message"
        if data_list[1] == 'get_msg':
            client_id = data_list[0]
            chatroom_id = data_list[2]
            all_chat_data = self.read_from_chatroom(chatroom_id,False)
            send_data = ""
            for row in all_chat_data:
                print(send_data, row[2], row[4])
                send_data = send_data +"From : " +row[2] +"Message : "+row[4] +"\n"

            return send_data
        if data_list[1] == 'get_msg_c':
            client_id = data_list[0]
            chatroom_id = '1' #way to get unique chatroom id
            print('here')
            self.create_chatroom(chatroom_id)
            return chatroom_id
        if data_list[1] == 'fetch_msg':
            client_id = data_list[0]
            chatroom_id = data_list[2]
            all_chat_data = self.read_from_chatroom(chatroom_id,True)
            send_data = ""
            for row in all_chat_data:
                print(send_data, row[2], row[4])
                send_data = send_data + "From : " + row[2] + "Message : " + row[4] + "\n"

            return send_data


    def write_to_chatroom(self):
        got_from_client = self.read_client()
        message_from_client = got_from_client[1].decode('utf-8')
        print(type(message_from_client),"tt")
        client_ip = got_from_client[0][0]
        print(client_ip)
        data = self.parse_client_message(message_from_client,client_ip)
        print(data)
        self.write_to_client(client_ip,5554,data)

if __name__ == "__main__":

    serve = Server()

    while(True):
        serve.write_to_chatroom()

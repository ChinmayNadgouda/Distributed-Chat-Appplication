"""
A class for the Server module which will handle the chat application
"""
import socket
import time
import sqlite3
#from broadcastlistener import broadcast_listener
localIP     = "192.168.70.192"

localPort   = 10001

bufferSize  = 1024

#database for th leader.
L_con = sqlite3.connect('leader.db')
L_cursor = L_con.cursor()

class Server():
    #to determine if the leader has been elected
    is_leader = False
    me_leader = False # not necessary
    #ip/id of the leader selected
    leader = ""
    #ip of the server itself
    ip_address = "192.168.1.1"
    #server id
    server_id = "12012023_1919"
    #ip and id of each server in the group
    group_view = {}
    #ip of clients assigned to the server
    clients_handled = []
    #chatroom ids handled by a server
    chatrooms_handled = []
    UDPServerSocket = None

    def __init__(self):
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((localIP, localPort))
        

    #get the messaged passed from clients ( have a message queue )
    def read_client(self):
            #keep listening and get the message from clinet
            bytesAddressPair = self.UDPServerSocket.recvfrom(bufferSize)

            message = bytesAddressPair[0]

            address = bytesAddressPair[1]

            clientMsg = "Message from Client:{}".format(message)
            clientIP = "Client IP Address:{}".format(address)

            print(clientMsg)
            print(clientIP)

            # Sending a reply to client
            msgFromServer = "Messsge received"
            print("sent to client")
            bytesToSend = str.encode(msgFromServer)
            self.UDPServerSocket.sendto(bytesToSend, ("127.0.0.1",10002))
            self.UDPServerSocket.close()
            #pass

    def create_leader_table():
        L_cursor.execute("CREATE TABLE IF NOT EXISTS leader(server_id, replica_id, chatroom_id)")

    def leader_data_entry(server_id, replica_id, chatroom_id):
        L_cursor.execute("INSERT INTO leader(server_id, replica_id, chatroom_id) VALUES(?,?,?)", (server_id, replica_id, chatroom_id))
        L_con.commit()
        L_cursor.close()
        L_con.close()

    def leader_data_fetch():
        L_con =sqlite3.connect('leader.db')
        L_cursor = L_con.cursor()
        L_cursor.execute('SELECT * FROM leader')
        data = L_cursor.fetchall()
        L_cursor.close()
        L_con.close()
        print(data)

    #create leader table only if this server is leader
    create_leader_table()
    #feed leader table
    leader_data_entry(1,1,1)
    leader_data_fetch()

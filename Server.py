"""
A class for the Server module which will handle the chat application
"""
import socket
import time
import sqlite3
from broadcastlistener import broadcast_listener

localIP     = "192.168.0.150"

localPort   = 10001

bufferSize  = 1024

class Server():
    #to determine if the leader has been elected
    is_leader = False
    me_leader = False # not necessary
    #ip/id of the leader selected
    leader = ""
    #ip of the server itself
    ip_address = "192.168.0.150"
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








if __name__ == "__main__":
    #sqlConnection
    conn = sqlite3.connect('chatDB.db')
    c = conn.cursor()
    
    ClientID = 0
    #create client Table once
    c.execute("CREATE TABLE IF NOT EXISTS clients(clientID INTEGER PRIMARY KEY, userName TEXT, IPAdress TEXT, groupID INTEGER)")
    conn.commit()
    newUser = broadcast_listener()
    c.execute("INSERT INTO clients (clientID, userName, IPAdress, groupID) VALUES (?, ?, ?, ?)",(ClientID, newUser['userName'], newUser['IP'], int(newUser['chatID'])))
    conn.commit()
    c.execute('SELECT * FROM clients')
    data = c.fetchall()
    print(data)
    for row in data:
        print(row)


    c.close
    conn.close()
    print(newUser)
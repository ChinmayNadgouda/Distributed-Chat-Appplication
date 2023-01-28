"""
A class for the Server module which will handle the chat application
"""
import socket
import time
import sqlite3
#from broadcastlistener import broadcast_listener
#neu
import select
import pickle

localIP     = "192.168.0.150"

BROADCAST_IP = "192.168.0.255" #needs to be reconfigured depending on network

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
    group_view = []
    #ip of clients assigned to the server
    clients_handled = []
    #chatroom ids handled by a server
    chatrooms_handled = []

    UDPServerSocket = None
    clientSocket = None
    broadcast_socket = None
    LeaderServerSocket = None



    #def __init__(self):
        #self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #self.UDPServerSocket.bind((localIP, localPort))
        #self.clientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #self.clientSocket.bind((localIP, 5001))
        #self.LeaderServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)




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

    def broadcastlistener(self, socket):

        print("Listening to broadcast messages")
        print(localIP)
        while True:
            data, server = socket.recvfrom(1024)
            print(data)
            if data:
                #userInformation = data.decode().split(',')
                #print(userInformation)
                #newUser = {'IP' : userInformation[0], 'userName' : userInformation[1]}
                # print(newUser['userName'], " with IP ", newUser['IP'], " wants to join Chat ", newUser['chatID'])
                return data


    def send_Message(self, ip, message):
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.sendto(message.encode(), (ip,5000))
        self.UDPServerSocket.close()

    def accept_login(self):
        #sqlConnection
        conn = sqlite3.connect('chatDB.db')
        c = conn.cursor()
        #create Server

        ClientID = 0
        #create client Table if not exist
        c.execute("CREATE TABLE IF NOT EXISTS clients(clientID INTEGER PRIMARY KEY, userName TEXT, IPAdress TEXT)")
        conn.commit()

        #set clientID
        c.execute("SELECT count(*) FROM clients")
        conn.commit()
        counter = c.fetchone()[0]
        if counter > 0:
            ClientID = counter

        #write Client to Client Table
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((localIP, localPort))
        data = self.broadcastlistener(self.UDPServerSocket)
        self.UDPServerSocket.close()
        userInformation = data.decode().split(',')
        print(userInformation)
        newUser = {'IP' : userInformation[0], 'userName' : userInformation[1]}
        c.execute("INSERT INTO clients (clientID, userName, IPAdress) VALUES (?, ?, ?)",(ClientID, newUser['userName'], newUser['IP'])) #grouplist
        conn.commit()

        c.execute('SELECT * FROM clients')
        data = c.fetchall()
        print(data)
        for row in data:
            print(row)

        #send answer
        #TODO fetch table of all available Chatrooms and send it to Client
        self.send_Message(newUser["IP"], self.ip_address)      

        #await chatID from Client
        self.clientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.clientSocket.bind((localIP, 5001))
        data, server = self.clientSocket.recvfrom(bufferSize)
        self.clientSocket.close()
        print('Received message: ', data.decode())

        #TODO check if chatID exists if not, create chat; send serverIP with chat to client
        
        c.close
        conn.close()
        print(newUser)    

    def broadcast(self, ip, port, broadcast_message):
        # Create a UDP socket
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Send message on broadcast address
        self.broadcast_socket.sendto(str.encode(broadcast_message), (ip, port))
        self.broadcast_socket.close()


    def join_Network(self):
        self.broadcast(BROADCAST_IP, 5043, self.ip_address)
        self.LeaderServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.LeaderServerSocket.bind((localIP, 5043))
        self.LeaderServerSocket.setblocking(0)
        ready = select.select([self.LeaderServerSocket],[],[], 3)
        if ready[0]:
            data, server = self.LeaderServerSocket.recvfrom(4096)
            self.LeaderServerSocket.close()
            self.group_view = pickle.loads(data)
            print("I got data: " + self.group_view)
            self.leader = server
            self.electLeader()



        else:
            print("I AM LEADER!")
            self.is_leader = True
            self.group_view.insert({"serverID": 0, "IP" : self.ip_address})
        self.LeaderServerSocket.close()


    def accept_Join(self):
        self.LeaderServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.LeaderServerSocket.bind((localIP, 5043))
        newServerIP = self.broadcastlistener(self.LeaderServerSocket)
        self.LeaderServerSocket.close()
        newServer = {"serverID": len(self.group_view),"IP" : newServerIP}
        print(newServer)
        self.group_view.insert(newServer)
        message = pickle.dumps(self.group_view)
        self.LeaderServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        for i in self.group_view:
            self.LeaderServerSocket.sendto(message, (i["IP"],5043))
        self.LeaderServerSocket.close()

    def electLeader(self):
        #TODO implement leader Election
        self.is_leader = False



if __name__ == "__main__":
    #create Server
    s = Server()

    s.join_Network()
    #TODO allow multiple Clients concurrently
    if s.is_leader == True:
        while True:
            s.accept_login()

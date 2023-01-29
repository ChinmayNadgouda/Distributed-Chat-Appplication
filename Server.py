"""
A class for the Server module which will handle the chat application
"""
import socket
import time
#from broadcastlistener import broadcast_listener
#neu
import select
import pickle
import multiprocessing
from multiprocessing.pool import ThreadPool
import threading

import uuid

localIP     = "192.168.0.164"

BROADCAST_IP = "192.168.0.255" #needs to be reconfigured depending on network

localPort   = 10001

bufferSize  = 1024

proc_queue = multiprocessing.Queue(maxsize = 100)
class Server():
    #to determine if the leader has been elected
    is_leader = False
    me_leader = False # not necessary
    #ip/id of the leader selected
    leader = ""
    #ip of the server itself
    ip_address = "192.168.0.164"
    #server id
    server_id = "12012023_1919"
    #Unique Identifier
    my_uid = str(uuid.uuid1())
    #ip and id of each server in the group
    group_view = [] #ServerID, IP, inPorts, outPorts
    #ip of clients assigned to the server
    clients_handled = []
    #list of all clients and Servers who handles them
    client_list = [] # IP, userName, chatID
    #chatroom ids handled by a server
    chatrooms_handled = []
    #list of only IPs for all Servers
    server_list = []

    UDPServerSocket = None
    clientSocket = None
    broadcast_socket = None
    LeaderServerSocket = None
    ringSocket = None



    def __init__(self):
        pass




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

#Functions for Dynamic Discovery:

    def send_Message(self, ip, message):
        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.sendto(message.encode(), (ip,5000))
        self.UDPServerSocket.close()

    def accept_login(self):

        self.UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((localIP, localPort))
        data = self.broadcastlistener(self.UDPServerSocket)
        self.UDPServerSocket.close()
        userInformation = data.decode().split(',')
        print(userInformation)
        newUser = {'IP' : userInformation[0], 'userName' : userInformation[1], "chatID": 0}


        #send answer
        #TODO fetch table of all available Chatrooms and send it to Client
        print("Send to " + newUser['IP'])
        self.send_Message(newUser['IP'], self.ip_address)    

        self.client_list.append(newUser)
        message = pickle.dumps(self.client_list)
        print(self.client_list)
        self.sendto_allServers(message, 5045)  

        #await chatID from Client
        #self.clientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #self.clientSocket.bind((localIP, 5001))
        #data, server = self.clientSocket.recvfrom(bufferSize)
        #self.clientSocket.close()
        #print('Received message: ', data.decode())
        #TODO check if chatID exists if not, create chat; send serverIP with chat to client
        
        #print(newUser)    

    def broadcast(self, ip, port, broadcast_message):
        # Create a UDP socket
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Send message on broadcast address
        self.broadcast_socket.sendto(broadcast_message.encode(), (ip, port))
        self.broadcast_socket.close()


    def join_Network(self):
        self.broadcast(BROADCAST_IP, 5043, self.ip_address)
        self.LeaderServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.LeaderServerSocket.bind((localIP, 5044))
        self.LeaderServerSocket.setblocking(0)
        ready = select.select([self.LeaderServerSocket],[],[], 3)
        if ready[0]:
            data, server = self.LeaderServerSocket.recvfrom(4096)
            self.LeaderServerSocket.close()
            self.group_view = pickle.loads(data)
            print("I got data: " + str(self.group_view))
            self.leader = server[0]
            print("Leader: " + self.leader + "GroupView: " + str(self.group_view))
            self.start_election()



        else:
            print("I AM LEADER!")
            self.is_leader = True
            self.group_view.append({"serverID": 0, "IP" : self.ip_address, "inPorts": [], "outPorts": []})
        self.LeaderServerSocket.close()


    def accept_Join(self):
        #while True:
            self.LeaderServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.LeaderServerSocket.bind((localIP, 5043))
            newServerIP = self.broadcastlistener(self.LeaderServerSocket)
            self.LeaderServerSocket.close()
            newServerID = max(self.group_view, key = lambda x:x['serverID'])['serverID'] + 1
            newServer = {"serverID": newServerID, "IP" : newServerIP.decode(), "inPorts": [], "outPorts": []}
            self.group_view.append(newServer)
            message = pickle.dumps(self.group_view)
            print(self.group_view)
            self.sendto_allServers(message, 5044)
            self.LeaderServerSocket.close()

    def sendto_allServers(self, message, port):
        #Port 5044: Groupview, Port 5045: Clientlist 
        self.LeaderServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        for i in self.group_view:
            print(i['IP'])
            self.LeaderServerSocket.sendto(message, (i['IP'],port))
        self.LeaderServerSocket.close()

    def update_groupview(self):
        self.LeaderServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.LeaderServerSocket.bind((localIP, 5044))
        data, server = self.LeaderServerSocket.recvfrom(4096)
        self.LeaderServerSocket.close()
        self.group_view = pickle.loads(data)
        print("New Groupview: " + str(self.group_view))

    def update_clientlist(self):
        self.clientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.clientSocket.bind((localIP, 5045))
        data, server = self.clientSocket.recvfrom(4096)
        self.clientSocket.close()
        self.client_list = pickle.loads(data)
        print("New Clientlist: " + str(self.client_list))
    
    
    #Functions for Leader Election:
    def start_election(self):
        #TODO implement leader Election
        print("My UID: " + self.my_uid)
        self.update_serverlist()
        ring = self.form_ring(self.server_list)
        neighbour = self.get_neighbour(ring, self.ip_address,'left')

        self.ringSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.ringSocket.bind((self.ip_address, 5892))
        message = pickle.dump({"mid": self.my_uid, "isLeader": False, "IP": self.ip_address})
        self.ringSocket.sendto(message,(neighbour,5892))
        self.ringSocket.close()

    def election(self):
        participant = False
        self.update_serverlist()
        ring = self.form_ring(self.server_list)
        neighbour = self.get_neighbour(ring, self.ip_address,'left')
        print("My neighbour: " + neighbour)
        participant = False

        self.ringSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ringSocket.bind((self.ip_address, 5892))

        print("Waiting for Election Messages")

        data, adress = self.ringSocket.recvfrom(bufferSize)
        election_message = pickle.load(data)
        print(election_message)

        if election_message['isLeader']:
            self.leader = election_message['IP']
            participant = False
            self.ringSocket.sendto(data,(neighbour,5892))

        if election_message['mid'] < self.my_uid and not participant:
            new_election_message = {
                "mid": self.my_uid, 
                "isLeader": False,
                "IP": self.ip_address
            }
            participant = True
            self.ringSocket.sendto(pickle.dump(new_election_message),(neighbour,5892))
        elif election_message['mid'] > self.my_uid:
            participant = True
            self.ringSocket.sendto(data,(neighbour,5892))
        elif election_message['mid'] == self.my_uid:
            self.leader = self.ip_address
            self.is_leader = True
            new_election_message = {
                "mid": self.my_uid,
                "isLeader": True,
                "IP": self.ip_address
            }
        
        self.ringSocket.close()


    def update_serverlist(self):
        for i in self.group_view:
            self.server_list.append(i['IP'])
        print(self.server_list)

    def form_ring(self, member_list):
        sorted_binary_ring = sorted([socket.inet_aton(member) for member in member_list])
        sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_binary_ring]
        return sorted_ip_ring
    
    def get_neighbour(self, ring, current_node_ip, direction = 'left'):
        current_node_index = ring.index(current_node_ip) if current_node_ip in ring else -1
        if current_node_ip != -1:
            if direction == 'left':
                if current_node_index +1 == len(ring):
                    return ring[0]
                else:
                    return ring[current_node_index + 1]
            else:
                if current_node_index == 0:
                    return ring[len(ring) - 1]
                else:
                    return ring[current_node_index -1]
        else:
            return None




if __name__ == "__main__":
    #create Server
    s = Server()

    s.join_Network()

    if s.is_leader == True:
        while True:
            s.accept_Join()
            #s.accept_login()
        #p_join = multiprocessing.Process(target = s.accept_Join, args = ())
        #p_join.start()
        #p_login = multiprocessing.Process(target = s.accept_login, args = ())
        #p_login.start()


    else:
        s.update_clientlist()
        #p_groupviewUpdate = multiprocessing.Process(target = s.update_groupview, args = ())
        #p_groupviewUpdate.start()
        #p_clientUpdate = multiprocessing.Process(target = s.update_clientlist, args = ())
        #p_clientUpdate.start()

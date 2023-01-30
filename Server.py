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

localIP     = "192.168.9.226"

BROADCAST_IP = "192.168.9.255" #needs to be reconfigured depending on network

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
    ip_address = "192.168.9.226"
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

    #UDPServerSocket = None
    #clientSocket = None
    #broadcast_socket = None
    #LeaderServerSocket = None
    #ringSocket = None



    def __init__(self):
        pass






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
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.sendto(message.encode(), (ip,5000))
        UDPServerSocket.close()

    def accept_login(self, server):

        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.bind((localIP, localPort))
        data = self.broadcastlistener(UDPServerSocket)
        UDPServerSocket.close()
        userInformation = data.decode().split(',')
        print(userInformation)
        newUser = {'IP' : userInformation[0], 'userName' : userInformation[1], "chatID": 0}


        #send answer
        #TODO fetch table of all available Chatrooms and send it to Client
        print("Send to " + newUser['IP'])
        self.send_Message(newUser['IP'], self.ip_address)    

        server.client_list.append(newUser)
        message = pickle.dumps(server.client_list)
        print(server.client_list)
        self.sendto_allServers(server, message, 5045)  

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
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Send message on broadcast address
        broadcast_socket.sendto(broadcast_message.encode(), (ip, port))
        broadcast_socket.close()


    def join_Network(self, server):
        self.broadcast(BROADCAST_IP, 5043, self.ip_address)
        LeaderServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        LeaderServerSocket.bind((localIP, 5044))
        LeaderServerSocket.setblocking(0)
        #TODO safe mechanism in case message gets lost
        ready = select.select([LeaderServerSocket],[],[], 3)
        if ready[0]:
            data, server = LeaderServerSocket.recvfrom(4096)
            LeaderServerSocket.close()
            server.group_view = pickle.loads(data)
            print("I got data: " + str(server.group_view))
            server.leader = server[0]
            print("Leader: " + server.leader + "GroupView: " + str(server.group_view))
            self.start_election(server)



        else:
            print("I AM LEADER!")
            server.is_leader = True
            server.group_view.append({"serverID": 0, "IP" : self.ip_address, "inPorts": [], "outPorts": []})
            print(server.group_view)
        LeaderServerSocket.close()


    def accept_Join(self, server):
        while True:
            LeaderServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            LeaderServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            LeaderServerSocket.bind((localIP, 5043))
            newServerIP = self.broadcastlistener(LeaderServerSocket)
            LeaderServerSocket.close()
            newServerID = max(server.group_view, key = lambda x:x['serverID'])['serverID'] + 1
            newServer = {"serverID": newServerID, "IP" : newServerIP.decode(), "inPorts": [], "outPorts": []}
            server.group_view.append(newServer)
            message = pickle.dumps(server.group_view)
            print(server.group_view)
            self.sendto_allServers(server, message, 5044)
            LeaderServerSocket.close()

    def sendto_allServers(self, server, message, port):
        #Port 5044: Groupview, Port 5045: Clientlist 
        LeaderServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        for i in server.group_view:
            print(i['IP'])
            LeaderServerSocket.sendto(message, (i['IP'],port))
        LeaderServerSocket.close()

    def update_groupview(self, server):
        LeaderServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        LeaderServerSocket.bind((localIP, 5044))
        data, server = LeaderServerSocket.recvfrom(4096)
        LeaderServerSocket.close()
        server.group_view = pickle.loads(data)
        print("New Groupview: " + str(server.group_view))

    def update_clientlist(self, server):
        clientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        clientSocket.bind((localIP, 5045))
        data, server = clientSocket.recvfrom(4096)
        clientSocket.close()
        server.client_list = pickle.loads(data)
        print("New Clientlist: " + str(self.client_list))
    
    
    #Functions for Leader Election:
    def start_election(self, server):
        #TODO implement leader Election
        print("My UID: " + self.my_uid)
        self.update_serverlist(server)
        ring = self.form_ring(server.server_list)
        neighbour = self.get_neighbour(ring, self.ip_address,'left')

        ringSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #ringSocket.bind((self.ip_address, 5892))
        message = pickle.dumps({"mid": self.my_uid, "isLeader": False, "IP": self.ip_address})
        ringSocket.sendto(message,(neighbour,5892))
        ringSocket.close()

    def election(self, server):
        participant = False
       
        print("My neighbour: " + neighbour)

        ringSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ringSocket.bind((self.ip_address, 5892))
        self.update_serverlist(server)
        ring = self.form_ring(server.server_list)
        neighbour = self.get_neighbour(ring, self.ip_address,'left')

        print("Waiting for Election Messages")

        data, adress = ringSocket.recvfrom(bufferSize)
        election_message = pickle.loads(data)
        print(election_message)

        if election_message['isLeader']:
            server.leader = election_message['IP']
            print("Leader is: " + server.leader)
            participant = False
            ringSocket.sendto(data,(neighbour,5892))

        if election_message['mid'] < self.my_uid and not participant:
            new_election_message = {
                "mid": self.my_uid, 
                "isLeader": False,
                "IP": self.ip_address
            }
            participant = True
            ringSocket.sendto(pickle.dumps(new_election_message),(neighbour,5892))

        elif election_message['mid'] > self.my_uid:
            participant = True
            ringSocket.sendto(data,(neighbour,5892))
        elif election_message['mid'] == self.my_uid:
            server.leader = self.ip_address
            server.is_leader = True
            new_election_message = {
                "mid": self.my_uid,
                "isLeader": True,
                "IP": self.ip_address
            }
            ringSocket.sendto(pickle.dumps(new_election_message),(neighbour,5892))
            print("I AM LEADER")
        
        ringSocket.close()
        if participant:
            self.election()


    def update_serverlist(self, server):
        for i in server.group_view:
            server.server_list.append(i['IP'])
        server.server_list = list(dict.fromkeys(server.server_list))
        print(server.server_list)

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

    s.join_Network(s)
    #while True:
    if s.is_leader == True:
         #   s.accept_Join()
          #  s.election()
            #s.accept_login()
        p_join = multiprocessing.Process(target = s.accept_Join, args = (s,))
        p_join.start()
       # p_join.join()
        p_login = multiprocessing.Process(target = s.accept_login, args = (s,))
        p_login.start()
        if len(s.server_list) != 0:
            p_election = multiprocessing.Process(target = s.election, args = (s,))
            p_election.start()


    else:
           
        #s.update_clientlist()
        p_groupviewUpdate = multiprocessing.Process(target = s.update_groupview, args = (s,))
        p_groupviewUpdate.start()
        p_clientUpdate = multiprocessing.Process(target = s.update_clientlist, args = (s,))
        p_clientUpdate.start()
        p_election = multiprocessing.Process(target = s.election, args = (s,))
        p_election.start()

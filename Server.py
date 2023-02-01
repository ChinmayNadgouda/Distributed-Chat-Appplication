"""
A class for the Server module which will handle the chat application
"""
import socket
import random
import json
import time
#from broadcastlistener import broadcast_listener
#neu
#import netifaces
import select
import pickle
import multiprocessing
from multiprocessing.pool import ThreadPool
import threading

import uuid

localIP     = "192.168.129.9"

BROADCAST_IP = "192.168.129.255" #needs to be reconfigured depending on network

localPort   = 10001      #broadcast servers

bufferSize  = 1024

proc_queue = multiprocessing.Queue(maxsize = 100)



import multiprocessing
from multiprocessing.pool import ThreadPool
import threading

leader_ip = "192.168.129.9"
localPort_in   = 5002     #chat inroom
localPort_out = 5003      #chat outroom
local_server_port = 4443   #heartbeat



from threading import Thread


class CustomThread(Thread):
    # constructor
    def __init__(self, localPort_out):
        # execute the base constructor
        Thread.__init__(self)
        # set a default value
        self.value = None
        self.localPort_out = localPort_out

    # function executed in a new thread
    def run(self):
        # block for a moment
        # sleep(1)
        # store data in an instance variable
        serve2 = Server()
        self.value = serve2.read_client(self.localPort_out,False, True, False)



class Server():

    #to determine if the leader has been elected
    is_leader = False
    me_leader = False # not necessary
    #ip/id of the leader selected
    leader = ""
    #ip of the server itself
    ip_address = "192.168.129.9"
    #server id
    server_id = "12012023_1919"
    #Unique Identifier
    my_uid = str(uuid.uuid1())
    #ip and id of each server in the group
    group_view = [] #ServerID, IP, inPorts, outPorts
    #ip of clients assigned to the server
    ack_counter = {}
    clients_handled = []  # {"192.168.188.22:5553":"192.168.188.29,192.168.188.22","192.168.188.28:6663":False,"192.168.188.29:7773":False}
    # ip of the whole server group, is a set {"127.0.0.1:1232:0"}  "ip_addr:port:heartbeatmisscount"
    ################"IP:heartbeatport:chatin:chatout"
    #list of all clients and Servers who handles them
    client_list = [] # IP, userName, chatID
    #chatroom ids handled by a server
    chatrooms_handled = []
    #list of only IPs for all Servers
    server_list = []
    server_heatbeat_list = {}
    previous_message = ""
    my_chatrooms = []  # ["5553,5554"] when replica ["5553,5554","5557,5558"]
    #UDPServerSocket = None
    #clientSocket = None
    #broadcast_socket = None
    #LeaderServerSocket = None
    #ringSocket = None



    def __init__(self):
        pass


    def broadcastlistener(self, socket, role):
        print("Listening to broadcast messages for ", role)
        print(localIP)
        while True:
            data, server = socket.recvfrom(1024)
            print(data)
            if data:
                # userInformation = data.decode().split(',')
                # print(userInformation)
                # newUser = {'IP' : userInformation[0], 'userName' : userInformation[1]}
                # print(newUser['userName'], " with IP ", newUser['IP'], " wants to join Chat ", newUser['chatID'])
                return data


#Functions for Dynamic Discovery:

    def send_Message(self, ip, message):
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.sendto(message, (ip,5000))
        UDPServerSocket.close()

    def accept_login(self, server):
        while True:
            try:
                if self.is_leader == False:
                    return
                UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                #UDPServerSocket.bind((localIP, localPort))
                UDPServerSocket.bind((localIP, localPort)) #changed_remove
                UDPServerSocket.settimeout(10)
                print("Listening to client messages")
                data = self.broadcastlistener(UDPServerSocket,'client')
                UDPServerSocket.close()
                userInformation = data.decode().split(',')
                print(userInformation)
                newUser = {'IP' : userInformation[0], 'userName' : userInformation[1], "chatID": 0}


                #send answer
                #TODO fetch table of all available Chatrooms and send it to Client
                print("Send to " + newUser['IP'])
                send_group_view_to_client = pickle.dumps(self.group_view)
                self.send_Message(newUser['IP'], send_group_view_to_client)

                ##client selection reply
                UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                # UDPServerSocket.bind((localIP, localPort))
                UDPServerSocket.bind((localIP, localPort))  # changed_remove
                #UDPServerSocket.settimeout(10)
                print("Listening to client messages response to join chatroom")
                data = self.broadcastlistener(UDPServerSocket, 'client')
                UDPServerSocket.close()
                userSelection = pickle.loads(data)
                #print(userSelection)
                selected_server_id = userSelection['selected_server']
                selected_charoom = userSelection['selected_chatroom']
                for chatrooms in self.group_view[int(selected_server_id)]['chatrooms_handled']:
                    if chatrooms['inPorts'][0] == selected_charoom:
                        new_chatroom_clients = []
                        for clients in chatrooms['clients_handled']:
                            new_chatroom_clients.append(clients)
                        new_chatroom_clients.append(json.dumps(userSelection))
                        chatrooms['clients_handled'] = set(new_chatroom_clients)
                #self.server_list[userInformation]['clients_handled'] = []
                #self.server_list[userInformation]['clients_handled'].append()
                #self.group_view[int(selected_server_id)]['clients_handled'] = set(self.group_view[int(selected_server_id)]['clients_handled'])
                #self.client_list.append(newUser)
                #message = pickle.dumps(self.client_list)
                #print(self.client_list)
                #self.sendto_allServers(server, message, 5045)

                message = pickle.dumps(self.group_view)
                print(self.group_view)
                for val in set(self.group_view[1]['chatrooms_handled'][0]['clients_handled']):
                    print('test client sets',type(json.loads(val)))
                self.sendto_allServers(server, message, 5044)  #all servers will get this and update their groupview and set clients
                self.send_Message(userSelection['IP'], b"please now connect to the server assigned and chatroom")
                #await chatID from Client
                #self.clientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                #self.clientSocket.bind((localIP, 5001))
                #data, server = self.clientSocket.recvfrom(bufferSize)
                #self.clientSocket.close()
                #print('Received message: ', data.decode())
                #TODO check if chatID exists if not, create chat; send serverIP with chat to client
                if self.is_leader == False:
                    return
                #print(newUser)    
            except socket.timeout:
                UDPServerSocket.close()
                self.accept_login(server)

    def broadcast(self, ip, port, broadcast_message):
        # Create a UDP socket
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #changed_remove
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
            self.group_view = pickle.loads(data)
            print("I got data: " + str(self.group_view))
            self.leader = server[0]
            print("Leader: " + self.leader + "GroupView: " + str(self.group_view))
            self.start_election(server)



        else:
            print("I AM LEADER!")
            self.is_leader = True
            self.group_view.append({"serverID": 0, "IP" : self.ip_address, "chatrooms_handled" : [{"inPorts": [5000], "outPorts": [5001], 'clients_handled':[]}],'heartbeat_port':4443})
            print(self.group_view)
        LeaderServerSocket.close()
    def ports_calc(self):
        current_ports = []
        for server in self.group_view:
            for chatrooms in server['chatrooms_handled']:
                current_ports.append(chatrooms['inPorts'][0])
                current_ports.append(chatrooms['outPorts'][0])

        if len(current_ports) == 0:
            new_inport = 5000
            new_outport = 5001
        else:
            current_ports.sort()
            new_inport = max(current_ports) + 1
            new_outport = new_inport + 1

        return [new_inport],[new_outport]


    def accept_Join(self, server):
        while True:
            if self.is_leader == False:
                    return
            LeaderServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            LeaderServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            #LeaderServerSocket.bind((localIP, 5043))
            LeaderServerSocket.bind((localIP, 5043)) #changed_remove
            print('Listening to Server mesages')
            newServerIP = self.broadcastlistener(LeaderServerSocket,'server')
            LeaderServerSocket.close()
            print(self.group_view)
            newServerID = max(self.group_view, key = lambda x:x['serverID'])['serverID'] + 1
            inports,outports = self.ports_calc()
            newServer = {"serverID": newServerID, "IP" : newServerIP.decode(),"chatrooms_handled" : [{"inPorts": inports, "outPorts": outports, 'clients_handled':[]}],'heartbeat_port':4444}
            self.group_view.append(newServer)
            self.server_heatbeat_list[newServerID] = 0     #later make this ip
            message = pickle.dumps(self.group_view)
            print(message)
            self.sendto_allServers(server, message, 5044)
            LeaderServerSocket.close()
            if self.is_leader == False:
                return
    def send_to_clients_new_server(self,chatroom,new_server_ip):
        for clients in chatroom['clients_handled']:
            cur_client = json.loads(clients)
            client_ip = cur_client['IP']
            client_port = 10002 #fixed port for always listen
            UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            UDPServerSocket.sendto(new_server_ip.encode(), (client_ip, client_port))
            UDPServerSocket.close()


    def sendto_allServers(self, server, message, port):
        #Port 5044: Groupview, Port 5045: Clientlist 
        LeaderServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        for i in self.group_view:
            print(i['IP'])
            LeaderServerSocket.sendto(message, (i['IP'],port))
        LeaderServerSocket.close()

    def update_groupview(self, server):
        try:
            LeaderServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            LeaderServerSocket.bind((localIP, 5044))
            LeaderServerSocket.settimeout(5)
            data, server = LeaderServerSocket.recvfrom(4096)
            LeaderServerSocket.close()
            self.group_view = pickle.loads(data)
            print("New Groupview: " + str(self.group_view))
            if self.is_leader == False:
                self.update_groupview(server)
        except socket.timeout:
            LeaderServerSocket.close()
            if self.is_leader == False:
                self.update_groupview(server)

    def update_clientlist(self, server):
        try:
            clientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            clientSocket.bind((localIP, 5045))
            clientSocket.settimeout(5)
            data, server = clientSocket.recvfrom(4096)
            clientSocket.close()
            self.client_list = pickle.loads(data)
            print("New Clientlist: " + str(self.client_list))
            if self.is_leader == False:
                self.update_clientlist(server)
        except socket.timeout:
            clientSocket.close()
            if self.is_leader == False:
                self.update_clientlist(server)    
    
    #Functions for Leader Election:
    def start_election(self, server):
        #TODO implement leader Election
        print("My UID: " + self.my_uid)
        self.update_serverlist(server)
        ring = self.form_ring(self.server_list)
        neighbour = self.get_neighbour(ring, self.ip_address,'left')

        ringSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ringSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  #changed_remove
        #ringSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)  #changed_remove
        #ringSocket.bind((self.ip_address, 5892))
        message = pickle.dumps({"mid": self.my_uid, "isLeader": False, "IP": self.ip_address})
        ringSocket.sendto(message,(neighbour,5892))
        ringSocket.close()

    def election(self, server):
        while True:
            participant = False
            ringSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ringSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #changed_remove
            #ringSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) #changed_remove
            ringSocket.bind((self.ip_address, 5892))
            self.update_serverlist(server)
            ring = self.form_ring(self.server_list)
            neighbour = self.get_neighbour(ring, self.ip_address,'left')

            print("Waiting for Election Messages")

            data, adress = ringSocket.recvfrom(bufferSize)
            election_message = pickle.loads(data)
            print(election_message)

            if election_message['isLeader']:
                self.leader = election_message['IP']
                print("Leader is: " + self.leader)
                participant = False
                ringSocket.sendto(data,(neighbour,5892))
                self.is_leader = False
                ringSocket.close()
                return
                

            if election_message['mid'] < self.my_uid and not participant:
                new_election_message = {
                    "mid": self.my_uid, 
                    "isLeader": False,
                    "IP": self.ip_address
                }
                participant = True
                ringSocket.sendto(pickle.dumps(new_election_message),(neighbour,5892))
                ringSocket.close()

            elif election_message['mid'] > self.my_uid:
                participant = True
                ringSocket.sendto(data,(neighbour,5892))
                ringSocket.close()

            elif election_message['mid'] == self.my_uid:
                self.leader = self.ip_address
                self.is_leader = True
                new_election_message = {
                    "mid": self.my_uid,
                    "isLeader": True,
                    "IP": self.ip_address
                }
                ringSocket.sendto(pickle.dumps(new_election_message),(neighbour,5892))
                print("I AM LEADER")
                ringSocket.close()
                return
                
            
            
            print("Leader is " + self.leader)


    def update_serverlist(self, server):
        for i in self.group_view:
            self.server_list.append(i['IP'])
        self.server_list = list(dict.fromkeys(self.server_list))
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
    def heart_beat_recving(self):

        leader_heartbeat = self.read_client(4444,False,heartbeat_leader=False,heatbeat_server=True)    #fix this port to own heartbeat port
        print(leader_heartbeat)
        if leader_heartbeat:
            if leader_heartbeat[1] == b'heartbeat':
                time.sleep(1)
                thread = threading.Thread(target=self.write_to_client, args=('heartbeat_recvd', self.leader, local_server_port,))    #fix localserverport to leader heartbeat
                thread.start()
                thread.join()
        else:
            print('Leader is dead,start election')
            print('Update groupview and election start')
            new_group_view = []
            dummy_server = None
            for server in self.group_view:
                if server['IP'] == self.leader:
                    pass
                else:
                    new_group_view.append(server)
            self.group_view = new_group_view
            self.sendto_allServers(dummy_server,new_group_view,5044)
            self.start_election(dummy_server)
            if self.is_leader:
                return True

    def heart_beating(self):
        for server in self.group_view:
            #time.sleep(10) #heartbeats after 60 seconds

            server_id = server['serverID']
            server_ip = server['IP']
            server_port = server['heartbeat_port']
            if server_id != 0:
                thread = threading.Thread(target=self.write_to_client,args=("heartbeat",server_ip,server_port,))
                thread.start()

                pool = ThreadPool(processes=1)

                async_result = pool.apply_async(self.read_client, (local_server_port,False,True,False))  # tuple of args for foo

                # do some other stuff in the main process

                listen_heartbeat = async_result.get()


                if listen_heartbeat:
                    if listen_heartbeat[1] == b'heartbeat_recvd':
                        print("Server {} is alive:".format(server_ip))
                        self.server_heatbeat_list[server_id] = 0      #later make this ip
                else:
                    if self.server_heatbeat_list[server_id] > 1:   #later make this ip and change to 3 tries i.e 2
                        print("Server {} {} is dead:".format(server_ip,server_id))
                        print("Update Group view and Replicate its clients to new server, choose a new server all this at next heartbeat")
                        self.server_heatbeat_list[server_id] = 0   #later make this ip
                        #inform all other servers
                        new_group_view = []
                        new_client_list = None
                        dummy_server = None
                        for server in self.group_view:
                            if server['serverID'] == server_id:
                                new_chatroom = server['chatrooms_handled']
                                pass
                            else:
                                new_group_view.append(server)

                        self.group_view = new_group_view
                        min_cli = 10000
                        clients_transfered = False
                        for servers in self.group_view:
                            if clients_transfered == True:
                                break
                            if servers['serverID'] == 0:
                                continue
                            for chatrooms in servers['chatrooms_handled']:
                                print(chatrooms)
                                if len(chatrooms['clients_handled']) == 0:
                                    servers['chatrooms_handled'].append(new_chatroom[0])  #later can be multiple chatrooms so just loop
                                    new_server_ip = servers['IP']
                                    clients_transfered = True
                                    continue
                                else:
                                    min_cli = min(len(chatrooms['clients_handled']),min_cli)
                        # if min_cli != 10000:
                        #     for servers in self.group_view:
                        #         for chatrooms in servers['chatrooms_handled']:
                        #             if len(chatrooms['clients_handled']) == min_cli:
                        #                 servers['chatrooms_handled'].append(new_chatroom)
                        #                 new_server_ip = servers['IP']
                        #                 continue


                        #logic to select new sever and append client list
                        #redirect client to new server
                        print(new_client_list)
                        print(self.group_view)
                        new_group_view = pickle.dumps(self.group_view)
                        self.sendto_allServers(dummy_server, new_group_view, 5044)
                        self.send_to_clients_new_server(new_chatroom[0],new_server_ip)
                    self.server_heatbeat_list[server_id] = self.server_heatbeat_list[server_id] + 1     #later make this ip

    def heartbeat_mechanism(self):
        while True:   #shud this while loop be inside heartbeating
            if self.is_leader:
                self.heart_beating()    #should this start new thread
            else:
                is_leader = self.heart_beat_recving()
                if is_leader:
                    return

        # get the messaged passed from clients ( have a message queue )
    def read_client(self, port, chatroom_timeout =False,heartbeat_leader=False, heatbeat_server=False):
            try:
                UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                # UDPServerSocket.setblocking(0)
                if heartbeat_leader:
                    UDPServerSocket.settimeout(5)
                if heatbeat_server:
                    UDPServerSocket.settimeout(60)
                if chatroom_timeout:
                    UDPServerSocket.settimeout(5)
                UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                #UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                #print("heree {}".format(port))
                UDPServerSocket.bind((localIP, port))
                # keep listening and get the message from clinet
                bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

                message = bytesAddressPair[0]

                address = bytesAddressPair[1]

                clientMsg = "Message from Client:{}".format(message)
                clientIP = "Client IP Address:{}".format(address)

                print(clientMsg)
                print(clientIP)

                UDPServerSocket.close()

                return [address, message]
            except socket.timeout:
                return False
            except Exception as e:
                print('Recving error: ', e)

    def write_to_client(self, server_message, client_ip, client_port):
        # Sending a reply to client
        # UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # UDPServerSocket.bind((client_ip, client_port))
        bytesToSend = str.encode(server_message)

        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.sendto(bytesToSend, (client_ip, client_port))
        print("sent {} to client {} {}".format(bytesToSend, client_ip, client_port))
        UDPServerSocket.close()
        return True
        # pass

    def write_to_client_with_ack(self, server_message, client_ip, client_port, from_client_ip,chatroom_inport,chatroom_outport):
        # Sending a reply to client
        # UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # UDPServerSocket.bind((client_ip, client_port))
        bytesToSend = str.encode(server_message)

        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPServerSocket.sendto(bytesToSend, (client_ip, client_port))
        print("sent {} to client {} {}".format(bytesToSend, client_ip, client_port))
        UDPServerSocket.close()
        # pool2 = ThreadPool(processes=1)
        # message_ack = 0
        # async_result = pool2.apply_async(self.read_client, (localPort_out, False, False))  # tuple of args for foo
        #
        # # do some other stuff in the main process
        # print("here")
        # ack_thread = async_result.get()
        # print('nhere')
        #
        # print("timout",ack_thread)

        # create a new thread
        thread = CustomThread(chatroom_outport)
        # start the thread
        thread.start()
        # wait for the thread to finish
        thread.join()
        # get the value returned from the thread
        ack_thread = thread.value
        if ack_thread:
            ackkkk = ack_thread[1].split(b',')
            if ackkkk[1] == b'recvd':
                self.ack_counter[from_client_ip][chatroom_inport] = self.ack_counter[from_client_ip][chatroom_inport] + 1
        else:
            # remove clinet from client list
            pass
        return True
        # pass

    def parse_client_message(self, client_recv_data):
        # print(client_recv_data)
        data_list = client_recv_data.split(",")
        # print(data_list)
        client_id = data_list[0]
        client_req = data_list[1]
        chatroom_id = data_list[2]
        client_message = data_list[3]
        client_port_out = data_list[-2]
        client_port = data_list[-1]
        return [client_id, client_req, chatroom_id, client_message, client_port_out, client_port]

    def collect_chatrooms(self):
        try:
            while True:

                for servers in self.group_view:
                    if servers['IP'] == self.ip_address and servers['serverID'] == 1:  # not needed
                        self.chatrooms_handled = servers['chatrooms_handled']


                        for chatrooms in self.chatrooms_handled:
                            if len(chatrooms['clients_handled']) == 0:
                                break
                            current_chatroom = chatrooms

                            clients_for_this_room = chatrooms['clients_handled']
                            chatroom_inport = current_chatroom['inPorts'][0]
                            chatroom_outport = current_chatroom['outPorts'][0]
                            p_room = threading.Thread(target=self.collect_clients,args=(chatrooms,chatroom_inport,chatroom_outport))
                            p_room.start()

                        for chatrooms in self.chatrooms_handled:
                            if len(chatrooms['clients_handled']) == 0:
                                break
                            p_room.join()
        except AttributeError:
                print("heer")


    def collect_clients(self,chatrooms,chatroom_inport,chatroom_outport):
        #print('starting chatroom for : ', clients_handled)
        for chatroom in self.chatrooms_handled:
            if len(chatroom['clients_handled']) == 0:
                                break
            for client in chatroom['clients_handled']:
                p_chat = threading.Thread(target=self.write_to_chatroom, args=(chatrooms,chatroom_inport,chatroom_outport,))
                p_chat.start()

        for chatroom in self.chatrooms_handled:
            if len(chatroom['clients_handled']) == 0:
                                break
            for client in chatroom['clients_handled']:
                p_chat.join()
    def write_to_chatroom(self,chatrooms,chatroom_inport,chatroom_outport):
        while True:
            print("Now sdfsdf    here",chatroom_inport)
            bytesAddressPair = self.read_client(chatroom_inport,True)  # localPort_in for each chatroom
            if bytesAddressPair == False:
                return
            print("Message in chatroom {} from {}".format(chatroom_inport,bytesAddressPair))
            message_from_client = bytesAddressPair[1].decode('utf-8')

            # callvector_check
            # print(type(message_from_client),"tt")

            from_client_ip = bytesAddressPair[0][0]
            client_id, data, chatroom_id, message, from_port, from_inport = self.parse_client_message(
                message_from_client)


            self.ack_counter[from_client_ip] = {}
            self.ack_counter[from_client_ip][chatroom_inport] = 0
            print("ACKcount_b2", self.ack_counter[from_client_ip][chatroom_inport])
            print('TEST, ',self.chatrooms_handled)
            for chatroom in self.chatrooms_handled:
                if int(chatroom['inPorts'][0]) == int(chatroom_inport):
                    for clients in chatroom['clients_handled']:
                        actual_client = json.loads(clients)
                        to_client_ip = actual_client['IP']
                        to_client_port = actual_client['outPorts']
                        to_client_port_ack = actual_client['inPorts']  # same as from_inport
                        # if to_client_ip == from_client_ip and to_client_port_ack == from_inport:   #notneeded
                        #     sender_inport = to_client_port_ack
                        thread = threading.Thread(target=self.write_to_client_with_ack,
                                                args=(message, to_client_ip, to_client_port, from_client_ip,chatroom_inport,chatroom_outport,))
                        thread.start()
                        thread.join()
            print("ACKcount_a", self.ack_counter[from_client_ip][chatroom_inport])
            if self.ack_counter[from_client_ip][chatroom_inport] == len(self.clients_handled):
                # for all clinets send sent!
                thread = threading.Thread(target=self.write_to_client,
                                          args=("sent", from_client_ip, int(from_inport),))
                thread.start()
                thread.join()
            else:
                thread = threading.Thread(target=self.write_to_client,
                                          args=("resend", from_client_ip, int(from_inport),))
                thread.start()
                thread.join()


def heartbeats():
    while True:
        if s.is_leader == True:
            p_heart = threading.Thread(target=s.heartbeat_mechanism, args=())
            p_heart.start()
            p_heart.join()
        else:
            p_heart_s = threading.Thread(target=s.heartbeat_mechanism, args=())
            p_heart_s.start()
            p_heart_s.join()

if __name__ == "__main__":
    #create Server
    s = Server()

    s.join_Network(s)
    print(s.group_view)

    p_H = threading.Thread(target=heartbeats, args=())
    p_H.start()

    while True:
        if s.is_leader == True:
            p_join = threading.Thread(target = s.accept_Join, args = (s,))
            p_join.start()
            p_login = threading.Thread(target = s.accept_login, args = (s,))
            p_login.start()
            p_election = threading.Thread(target = s.election, args = (s,))
            p_election.start()
            p_chat = threading.Thread(target=s.collect_chatrooms, args=())
            p_chat.start()


            p_login.join()
            p_join.join()
            p_election.join()
            p_chat.join()

        else:
            p_groupviewUpdate = threading.Thread(target = s.update_groupview, args = (s,))
            p_groupviewUpdate.start()

            p_clientUpdate = threading.Thread(target = s.update_clientlist, args = (s,))
            p_clientUpdate.start()
            p_election = threading.Thread(target = s.election, args = (s,))
            p_election.start()

            p_chat = threading.Thread(target=s.collect_chatrooms, args=())
            p_chat.start()
            p_groupviewUpdate.join()
            p_clientUpdate.join()
            p_election.join()
            p_chat.join()












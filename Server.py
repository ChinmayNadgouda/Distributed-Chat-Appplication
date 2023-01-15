"""
A class for the Server module which will handle the chat application
"""
import socket
import time

localIP     = "127.0.0.1"

localPort   = 20001

bufferSize  = 1024

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

    #when the server enters or the leader fails start election is called
    def start_election(self):
        leader= "" #Election_Module.start_election()
        if leader == self.server_id:
            is_leader = True
            me_leader = True
        else:
            is_leader = True

    #after every interval a fixed sized chunk of (N) bytes is replicated to secondaries
    def replicate(self):
        while(True):
            chunk_size = 10
            interval = 1
            #replicate current chunk (size KB) of data after regular interval ( time sec)

    #after replication chunk is received the secondary sends ack to the primary to commit
    def acknowledge_replication(self,chunk_number):
        pass
        #get_prev_chunk_number()
        #if prev_chunk_number > chunk_number:
        #return False
        #primary_write(chunk_number)

    #after receiving the heartbeat from the leader the server sends an ack
    def acknowledge_heartbeat(self):
        while(True):
            message = "alive"
            #listen_leader()


            #leader_write(message)

    #the leader sends an heartbeat to every server to detect fault in the system
    def send_heartbeat(self):
        while (True):
            address = "some broadcast address"
            interval = 30
            time.sleep(interval)
            msgFromServer = "heartbeat"

            bytesToSend = str.encode(msgFromServer)
            self.UDPServerSocket.sendto(bytesToSend, address)
            # send alive message to every server after regular interval ( time sec)
            # broadcast("alive")

    #when a client registers to the system the leader will assign it to a random server
    def assign_client_to_server(self):
        #check client request for joining
        #find free server by either round-robin or answer first selection
        #assign client to server
        pass

    #listen to clients request and connect to the server and chatroom ( keep listening to client requests)
    def connect_client(self):
        #after assignment connect client to requested chatroom or create a new one
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

        bytesToSend = str.encode(msgFromServer)
        self.UDPServerSocket.sendto(bytesToSend, address)
        pass

    #put the message in responsible chatroom (send the message to given chatroom)
    def write_to_chatroom(self,client_name,message,chatroom_id):
        #write(chatroom_id,message,client_name)
        pass

    #get the list of clients assigned to the server
    def get_client_list(self):
        return self.clients_handled


    #get the list of chat rooms handled by the server
    def get_chatroom_list(self):
        return self.chatrooms_handled

    #get the group view list
    def get_group_view(self):
        return self.group_view

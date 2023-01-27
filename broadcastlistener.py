import socket


def broadcast_listener():
    # Listening port
    BROADCAST_PORT = 5042

    # Local host information
    MY_HOST = socket.gethostname()
    MY_IP = "192.168.0.150"

    # Create a UDP socket
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Set the socket to broadcast and enable reusing addresses
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind socket to address and port
    listen_socket.bind((MY_IP, BROADCAST_PORT))

    print("Listening to broadcast messages")
    print(MY_IP)
    while True:
        data, addr = listen_socket.recvfrom(1024)
        if data:
            ipadress = data.decode()
            print(ipadress)
            listen_socket.sendto(str.encode("Whats up?"), (ipadress, 5043))
            #userInformation = data.decode().split(',')
            #newUser = {'IP' : userInformation[0], 'userName' : userInformation[1]}
            # print(newUser['userName'], " with IP ", newUser['IP'], " wants to join Chat ", newUser['chatID'])
            #return newUser
            break

if __name__ == "__main__":
    broadcast_listener()
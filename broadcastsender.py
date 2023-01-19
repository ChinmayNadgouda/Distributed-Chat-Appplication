import socket


def broadcast(ip, port, broadcast_message):
    # Create a UDP socket
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Send message on broadcast address
    broadcast_socket.sendto(str.encode(broadcast_message), (ip, port))
    broadcast_socket.close()


if __name__ == '__main__':
    # Broadcast address and port
    BROADCAST_IP = "192.168.0.255" #needs to be reconfigured depending on network
    BROADCAST_PORT = 10001

    # Local host information
    MY_HOST = socket.gethostname()
    MY_IP = socket.gethostbyname(MY_HOST)

    #Input User Information
    userName = input('Enter UserName ')
    chatID = input('Enter ChatID ')

    # Send broadcast message
    message = MY_IP + ',' + userName + ',' + chatID
    broadcast(BROADCAST_IP, BROADCAST_PORT, message)

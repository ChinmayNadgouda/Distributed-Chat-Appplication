import socket
import netifaces

def get_broadcast_ip(interface):

    addrs = netifaces.ifaddresses(interface)
    return addrs[netifaces.AF_INET][0]['broadcast']

    #return net.broadcast_address


def broadcast(ip, port, broadcast_message):
    # Create a UDP socket
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Send message on broadcast address
    broadcast_socket.sendto(str.encode(broadcast_message), (ip, port))
    broadcast_socket.close()


if __name__ == '__main__':
    # Broadcast address and port
    BROADCAST_IP = get_broadcast_ip("en0")
    BROADCAST_PORT = 5973

    # Local host information
    MY_HOST = socket.gethostname()
    MY_IP = socket.gethostbyname(MY_HOST)

    #Input User Information
    userName = input('Enter UserName ')
    chatID = input('Enter ChatID ')

    # Send broadcast message
    message = MY_IP + ',' + userName + ',' + chatID
    broadcast(BROADCAST_IP, BROADCAST_PORT, message)

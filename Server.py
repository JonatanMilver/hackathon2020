import socket
import threading
import random
import struct
from time import sleep

class Server:
    # IP = socket.gethostbyname(socket.gethostname())
    IP = '172.18.0.61'
    UDP_PORT = 13117
    TCP_PORT = 50000

    # magic_cookie = b'11111110111011011011111011101111'
    magic_cookie = 0xfeedbeef
    # m_type = b'00000010'
    m_type = 0x2
    # server_port = b'1100001101010000'
    server_port = 50000
    udp_offer = magic_cookie + m_type + server_port

    def __init__(self):
        self.sending_udp_messages = False

        self.udp_sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP

        # setting up udp socket for broadcasting to all clients
        self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        
        self.tcp_sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_STREAM) # TCP
        self.tcp_sock.settimeout(0.1)
        self.tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_sock.bind((self.IP, self.TCP_PORT))

        self.client_list = []

    
    def send_udp_message(self):
        self.sending_udp_messages = True
        print("Server started, listening on ip address {}".format(self.IP))

        for i in range(10):
            print(i)
            # self.udp_sock.sendto(self.udp_offer, ('<broadcast>', self.UDP_PORT))
            self.udp_sock.sendto(struct.pack('IbH', self.magic_cookie, self.m_type, self.server_port), ('<broadcast>', self.UDP_PORT))
            sleep(1)

        self.sending_udp_messages = False

    def accept_connections(self):

        while self.sending_udp_messages:
            try:
                client_socket, client_address = self.tcp_sock.accept()

                client_thread = threading.Thread(target=self.get_team_name, args=(client_socket,client_address))
                client_thread.start()

            except socket.timeout:
                # print("socket timed out")
                continue


    def get_team_name(self, client_socket, client_address):
        # TODO: put in try and catch!
        team_name = client_socket.recv(1024).decode('utf-8')
        print(team_name)

        self.client_list.append((client_socket, client_address, team_name))

    def assign_to_groups(self):
        group_a, group_b = [], []
        client_copy = list(self.client_list)
        l = len(self.client_list)

        for i in range(l//2):
            r = random.randint(0, len(client_copy))

            group_a.append(client_copy[r])
            client_copy.pop(r)
        
        for client in client_copy:
            group_b.append(client)

        return group_a, group_b

    def create_game_start_message(self, group_a, group_b):
        m = 'Welcome to Keyboard Spamming Battle Royale.\n'
        m += 'Group 1:\n==\n'
        for c in group_a:
            m += c[2]
        
        m += 'Group 2:\n==\n'
        for c in group_b:
            m += c[2]

        m += 'Start pressing keys on your keyboard as fast as you can!!'

        return m

    def send_tcp_message(self, message):
        l_thread = []
        for client in self.client_list:
            # client[0].send(bytes(message, 'utf-8'))
            x = threading.Thread(client[0].send, args=(bytes(message, 'utf-8'),))
            l_thread.append(x)
            x.start()
            
        





if __name__ == "__main__":
    server = Server()
    # server.main()
    server.tcp_sock.listen()
    while True:
        udp_message_thread = threading.Thread(target=server.send_udp_message)
        udp_message_thread.start()
        
        tcp_receive_thread = threading.Thread(target=server.accept_connections)
        tcp_receive_thread.start()

        udp_message_thread.join()
        tcp_receive_thread.join()

        if len(server.client_list) < 2:
            print("not enough players!")
            continue

        group_a, group_b = server.assign_to_groups()

        print("group_a: {}".format(group_a))
        print("group_b: {}".format(group_b))

        game_start_message = server.create_game_start_message(group_a, group_b)
        server.send_tcp_message(game_start_message)

    # server.tcp_sock.shutdown(socket.SHUT_RDWR)
    # server.tcp_sock.close()

    # server.start_game()

    # server.send_udp_message()
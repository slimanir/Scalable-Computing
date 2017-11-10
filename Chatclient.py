import socket
import threading

# class for simplifying the client
class Client(object):
    def __init__(self, host, port, name, ID):
        self.host = host
        self.port = port
        self.name = name #socket.gethostname()
        self.ID = ID 
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

        # send name of client
        self.socket.sendall(str.encode(self.name))

        # start thread for message queue
        clientThread = threading.Thread(target=self.listen)
        clientThread.daemon = True
        clientThread.start()

    # waits for incoming messages
    def listen(self):
        while True:
            try:
                data = bytes.decode(self.socket.recv(1024))
                print(data)
            except socket.error as e:
                print('\n[#] The server has disconnected. Press [Enter] to continue.')
                break

    # sends a message to the server
    def send(self, message):
        self.socket.send(str.encode(message))


print('[#] Welcome!')
name = input('[#] Please enter your Name: ')
ID = input('[#] Please enter your Student ID: ')

            #return [ name, ID ]
# loop for host input
while True:
    host = input('[#] Please enter the Host: ')
    port = 8000

    # we need a try-except here, if the server is not reachable
    try:
        client = Client(host, port, name, ID)
        print('[#] Connected ! ')
    except socket.error as e:
        print('[#] Sorry you can not connect to the host.')
        continue

    # loop for chat messages
    while True:
        try:
            # there might be an exception, when the server gets shut down
            client.send(input())
        except socket.error as e:
            break
    

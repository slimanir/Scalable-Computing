import socket
import threading

# Class for simplifying the server
class Server(object):

    # Initializes the class
    def __init__(self, port):
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.runServer = True
        self.room = [] # {room_name: Room}
        #self.room_client_map = {} # {clienName: roomName}

    # Starts the server
    def start(self):
        host = ''

        # we need to reopen ports, not setting this leads to left open ports
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind host and port
        try:
            self.server.bind((host, self.port))
        except socket.error as e:
            print(str(e))

        # Server is now running
        self.server.listen(15)

        # Some info
        self.consoleOutput('Server running.')
        self.consoleOutput('Host: ' + socket.gethostbyname(socket.gethostname()))
        self.consoleOutput('Port: ' + str(self.port))

        # start a new thread which accepts the connections
        serverThread = threading.Thread(target=self.__runServer)
        serverThread.daemon = True
        serverThread.start()

        # console input
        while self.runServer:
            userInput = input()
            commands = userInput.split(' ')

            if len(commands) == 0:
                continue

            # list all connected devices
            if commands[0] == 'list':
                i = 0
                while i < len(self.clients):
                    self.consoleOutput('(' + str(i) + ') ' + self.clients[i].name + ': ' + self.clients[i].connection.getsockname()[0])
                    i = i + 1

            # kick command [second argument is client number from list]
            elif commands[0] == 'kick':
                if len(commands) > 1 and commands[1].isdigit() and int(commands[1]) < len(self.clients):
                    self.clients[int(commands[1])].kick()

            # server shutdown
            elif commands[0] == 'quit':
                self.stop()

            # send message like everybody else
            else:
                self.serverMessage(userInput)
                
    def Room(self, client):
        
        if len(self.rooms) == 0:
            message = 'Oops, no active rooms currently.' #\
               # + 'Use [<join> room_name] to create a room.\n'
            #player.socket.sendall(msg.encode())
        else:
            message = 'Listing current rooms...\n'
            self.broadcast(message)

    # internal method to run the server multi-threaded
    def __runServer(self):
        while self.runServer:
            self.consoleOutput('Waiting for next client...')

            # accept a client
            (connection, address) = self.server.accept()

            # create new instance of our client class and add it to the list
            client = Client(connection, self)
            #room = Room(self, client)

            # some info
            self.consoleOutput(client.name + ' connected: ' + str(address[0]) + ':' + str(address[1]))
            self.serverMessage(client.name + ' connected.')

            # add client to list
            self.clients = self.clients + [client]
            #self.rooms = self.rooms + [room]

    #def HELO(self, client, message, server):
        
    
    

    # Sends a message to all clients, except the given one
    def broadcast(self, message, client=None, host=''):
        instructions = '[SERVER] : Welcome to chat rooms service \n'  + '[#Type list] to list all rooms\n'  + '[#Type join room_name] to Join/Switch to a room\n' + '[#Type quit] to quit\n'
        for c in self.clients:
            if client == None or c != client:
                c.send(message)
            if 'HELO' in str(message):
                c.send(' HELO text : ' )   
                c.send(' IP: ' + socket.gethostbyname(socket.gethostname()))
                c.send(' Port: ' + str(self.port))
            if 'chatroom' in str(message):
                
                self.broadcast(instructions)
                
                
                if 'join' in str(message):
                    
                    same_room = False
                    
                    if len(message.split()) >= 2: # error check
                        room_name = message.split()[1]
                    if client in self.room:
                        
                        # switching?
                            
                        self.broadcast('You are already in room: ' + room_name)
                        same_room = True  # switch
                            
                    else:
                        
                        self.broadcast(instructions)

                elif 'list' in str(message):
                    self.list_rooms(client)
        
                elif 'quit' in str(message):
                    
                    self.broadcast(QUIT_STRING)
                    self.remove_client(client)
    
                else:
                    
                        
                    message = 'You are currently not in any room! \n' \
                                + 'Use [<list>] to see available rooms! \n' \
                                + 'Use [<join> room_name] to join a room! \n'
                    
                    self.broadcast(message)
                    
         # Joining the chatroom            
    def joinRoom(self, chatname, join, leave, client, message):
        for c in client:
            chatroom = [1, 2, 3, 4, 5]
            if client == None or c != client:
                c.send(message)
            if 'JoinChatroom' in str(message):
                c.send('Please enter the chatroom name you want to join : ')
                c.send(num = input('[#] Chatroom name : ' "Please specifie one number from 1-5"))
                c.send(name = input('[#] Please enter your Name : '))
                return [chatname, name]
            for num in chatroom :
                c.send(self.broadcast('[SERVER] ' + 'You joined chatroom number:' + num))
                    

    
    def remove_client(self, client):
        if client.name in self.room_client_map:
            self.rooms[self.room_client_map[client.name]].remove_client(client)
            del self.room_client_map[client.name]
        print( client + " has left\n")
             

    # Stops the server
    def stop(self):
        self.serverMessage('Server shutting down.')

        # disconnect every client
        for client in self.clients:
            client.forceDisconnect()

        self.runServer = False

    # broadcast with prefix
    def serverMessage(self, message):
        self.broadcast('[SERVER] ' + message)
        

    # just simplifying the console output prefix
    def consoleOutput(self, message, isClient=False):
        if isClient:
            print('[CLIENT] ' + message)
        else:
            print('[SERVER] ' + message)


# Class holding methods to communicate with the client
class Client(object):

    # initializes a new client object
    def __init__(self, conn, server):
        self.connection = conn
        self.server = server
        ###
        self.socket = socket

        # receive name of client
        self.name = bytes.decode(self.connection.recv(1024))

        # every client has to get his own thread in order to run parallel
        clientThread = threading.Thread(target=self.listen)
        clientThread.daemon = True
        clientThread.start()

    # sends a message to the client
    def send(self, message):
        self.connection.sendall(str.encode(message))

    # waites for incoming data
    def listen(self):
        while True:
            try:
                data = bytes.decode(self.connection.recv(1024))
            except socket.error as e:
                self.forceDisconnect()
                break

            # send the message to all clients
            self.server.consoleOutput(self.name + ': ' + data, True)
            self.server.broadcast(self.name + ': ' + data, self)

    # kicks this client from the server
    def forceDisconnect(self):
        self.connection.close()

        # client can already be removed from list
        # with kick()
        if self in self.server.clients:
            self.server.clients.remove(self)

            # if client was not removed yet, info..
            self.server.consoleOutput(self.name + ' disconnected.')
            self.server.serverMessage(self.name + ' disconnected.')

    # kick this client
    def kick(self):
        self.send('[Server] You got kicked!')

        # actually kick the client
        self.forceDisconnect()

   # Class Room 
class Room:
    def __init__(self, name):
        self.clients = [] # a list of sockets
        self.name = name

    def welcome_new(self, from_client):
        message = self.name + " welcomes: " + from_client.name + '\n'
        for client in self.clients:
            self.broadcast(message)
    
    def broadcast(self, from_client, message):
        message = from_client + ":" + message
        for client in self.clients:
            self.broadcast(message)

    def remove_client(self, client):
        self.clients.remove(client)
        leave_message = client() + "has left the room\n"
        self.broadcast(client, leave_message)

QUIT_STRING = 'quit room'

server = Server(8000)
server.start()

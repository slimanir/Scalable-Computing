import socket 
from socket import *
import time
import threading
import sys

chatserver = True
studentID = 17313666 #Student ID 

roomMutex = threading.Lock()  ##  lock to control room lists
roomName = {}                 ## Identification of rooms by name
roomRef = {}                  ## Identification of connections by room references
roomRefCount = 0              ## room reference counter
connToJoinID = {}             ## Identification of clients by connection 
joinID = 0                    ## Join_ID counter

##         Running the server          ##

server = 'localhost'
Port = int(sys.argv[1])
print('Server Port {}'.format(sys.argv[1]))
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', Port))  
print('[SERVER]## SERVER STARTED....')
print('[SERVER]## Waiting for next client....')
serverSocket.listen(15) 


clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.connect(('localhost', 23))
addr = clientSocket.getsockname()[0]
print('Connected to {}\ '.format(addr))

##              Definition of HELO         ##

def helo(msg, conn):
    print("HELO : ")
    helo_msg = "HELO{}IP:{}\nPort:{}\nStudentID:{}\n".format(msg[4:],addr,Port,studentID)     
    conn.send(helo_msg.encode())
    print("[SERVER] ## HELO ? :\n {}".format(helo_msg)) ## "HELO text\nIP:[ip address]\nPort:[port number]\nStudentID:[your student ID]\n"
    
    ##         Joining chatroom           ##
    
def joinChatroom(msg, conn):
    text_split = msg.splitlines()     # spliting message lines
    room_name = text_split[0][15:]    # JOIN_CHATROOM: [chatroom name]
    client_ip = text_split[1][11:]    # CLIENT_IP: [IP Address of client if UDP | 0 if TCP]
    port = text_split[2][6:]          # PORT: [port number of client if UDP | 0 if TCP]
    client_name = text_split[3][13:]  # CLIENT_NAME: [string Handle to identifier client user]

    roomMutex.acquire()
    if room_name not in roomName:  
        roomRefCount += 1  
        roomName[room_name] = roomRefCount  
        roomRef[roomRefCount] =  list()  
    currentRoomRef = roomName[room_name]  
    roomRef[currentRoomRef].append(conn)  
                                        
    
    roomMutex.release()
    
    if conn not in connToJoinID:  
        joinID += 1
        connToJoinID[conn] = joinID  
    client_joinID = connToJoinID[conn]

    text_response = "JOINED_CHATROOM: {}\nSERVER_IP: {}\nPORT: {}\nROOM_REF: {}\nJOIN_ID: {}\n".format(room_name, addr, port, currentRoomRef, client_joinID)
    print("[SERVER]## You have just :\n {}".format(text_response))
    conn.send(text_response.encode())

    room_response = "CHAT: {}\nCLIENT_NAME: {}\nMESSAGE: {} has joined this chatroom\n\n".format(currentRoomRef, client_name, client_name)

    ##         Welcoming new client     ##
    
    for connect in roomRef[currentRoomRef]:
        connect.send(room_response.encode())
    print("[SERVER]## CHATROOM {}:\n {}".format(currentRoomRef, room_response))

   ###        Leaving the chatroom process         ##
    
def leaveChatroom(msg, conn):
    text_split = msg.splitlines()     # spliting message lines
    room_ref = text_split[0][16:]     # LEAVE_CHATROOM: [ROOM_REF]
		                    
    join_ID = text_split[1][9:]       # JOIN_ID: [integer previously provided by server on join]
    client_name = text_split[2][13:]  # CLIENT_NAME: [string Handle to identifier client user]


    if conn in roomRef[int(room_ref)]:  
        roomRef[int(room_ref)].remove(conn)
    leave_response = "LEFT_CHATROOM: {}\nJOIN_ID: {}\n".format(room_ref, join_ID)
    print("[SERVER]## You have just :\n {}".format(leave_response))
    conn.send(leave_response.encode())  

    room_response = "CHAT: {}\nCLIENT_NAME: {}\nMESSAGE: {} has left this chatroom\n\n".format(room_ref, client_name, client_name)  

    conn.send(room_response.encode())  
    
    
    for connect in roomRef[int(room_ref)]:
        connect.send(room_response.encode())
    print("[SERVER]##  {}:\n {}".format(room_ref, room_response))

    ##      Broadcast msg to chatroom      ##

def chatToChatroom(msg, conn):
    text_split = msg.splitlines()     ## spliting message lines
    room_ref = text_split[0][6:]      ## CHAT: [ROOM_REF]
    join_ID = text_split[1][9:]       ## JOIN_ID: [integer identifying client to server]
    client_name = text_split[2][13:]  ## CLIENT_NAME: [string identifying client user]
    chatMessage = text_split[3][9:]   ## MESSAGE: [string terminated with '\n\n']
    
    # Broadcast message to clients in room
    room_response = "CHAT: {}\nCLIENT_NAME: {}\nMESSAGE: {}\n\n".format(room_ref, client_name, chatMessage)
    for connect in roomRef[int(room_ref)]:
        connect.send(room_response.encode())
    print("[SERVER]## CHATROOM {}:\n {}".format(room_ref, room_response)) ##  CHAT: [ROOM_REF]  ## CLIENT_NAME: [string identifying client user] ## MESSAGE: [string terminated with '\n\n']
    

def disconnectClient(msg, conn): 
    text_split = msg.splitlines()     ## spliting message lines
    client_IP = text_split[0][12:]    ## DISCONNECT: [IP address of client if UDP | 0 if TCP]
    port = text_split[1][6:]          ## PORT: [port number of client it UDP | 0 id TCP]
    client_name = text_split[2][13:]  ## CLIENT_NAME: [string handle to identify client user]
    
    ##        Broadcast message to clients in room    ##
    
    for roomReference in roomRef:  
        if conn in roomRef[roomReference]:  
            room_response = "CHAT: {}\nCLIENT_NAME: {}\nMESSAGE: {} has left this chatroom\n\n".format(roomReference, client_name, client_name)
            for connect in roomRef[int(roomReference)]:
                connect.send(room_response.encode())
            print("[SERVER] ## Broadcast to clients in ROOM {}:\n {}".format(roomReference, room_response))
            roomRef[int(roomReference)].remove(conn)   
    conn.close()    


##     Dealing with clients requests       ##
def receive_clients(conn):
    
 
    while 1:
        request = conn.recv(1024)  
        request = request.decode()  
        if request != "":
            continue
        
	##        Responding to clients requests     ##
        if "HELO" in str(request):  
            heloFunction(request, conn)

        elif "JOIN_CHATROOM" in str(request):
            joinChatroom(request, conn)

        elif "LEAVE_CHATROOM" in str(request):
            leaveChatroom(request, conn)

        elif "CHAT" in str(request):
            chatToChatroom(request, conn)
        
        elif "DISCONNECT" in str(request):
            disconnectClient(request, conn)
            break

        elif "KILL_SERVICE\n" in str(request):                 
            print("[SERVER] ##  SERVICE STOPPED")
            chatserver = False
            conn.close()  
            break
        else:
            print("[SERVER]: Ooooops \nERROR_CODE : 666 \n ERROR_DESCRIPTION : {} COMMAND NOT FOUND OR INCORRECT # -__- # \n".format(request)) ##  ERROR_CODE: [integer]
                                                                                                                                               ## ERROR_DESCRIPTION: [string describing error] 
                                                                                                                                               


##              Running the server while condition 'chatserver is true ( no KILL SERVICE IS SENT )               ##
            
while chatserver:
    connectionSocket, addr = serverSocket.accept()  
    print('Received Connection from {}'.format(addr))
    threading.Thread(target=receive_clients, args=(connectionSocket,)).start()  


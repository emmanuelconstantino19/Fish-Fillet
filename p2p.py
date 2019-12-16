import socket
import threading
import sys
import string
import time
from random import randint
import traceback
from game import *
import globals

class Server:
    connections = []
    peers = []
    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', 10000))
        sock.listen(1)
        self.peers = globals.peers
        self.sendPeers()
        host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print(self.peers)
        if len(self.peers)==0:
            host_socket.connect(('0.0.0.0', 10000))
        else:
            host_socket.connect((self.peers[0], 10000))

        globals.sock = host_socket

        print("Server running ...")
        while True:
            serverChatThread = threading.Thread(target=self.serverChat)
            serverChatThread.daemon = True
            serverChatThread.start()

            c, a = sock.accept()
            cThread = threading.Thread(target=self.handler, args=(c,a))
            cThread.daemon = True
            cThread.start()
            self.connections.append(c)
            self.peers.append(a[0])
            print(str(a[0]) + ':' + str(a[1]), "connected")
            self.sendPeers()

    def serverChat(self):
        while True:
            data = input("")
            if data!="":
                updatedData = str("Server: " + data)
                for connection in self.connections:
                    connection.send(bytes(updatedData, "utf-8"))

    def handler(self, c, a):
        while True:
            try:
                data = c.recv(1024)
                convertedData = str(data, "utf-8")
                for connection in self.connections:

                    if 'CURRENT_COORDINATES' in convertedData:
                        coords = convertedData.split(':')
                        x,y = coords[-1].split(',')
                        p2p.peersCoordinates[a] = [x,y]
                        connection.send(bytes(str(p2p.peersCoordinates),'utf-8'))
                    else:    
                        connection.send(data)
                if not data:
                        print(str(a[0]) + ':' + str(a[1]), "disconnected")
                        self.connections.remove(c)
                        self.peers.remove(a[0])
                        del p2p.peersCoordinates[a]
                        c.close()
                        self.sendPeers()
                        break
            except:
                print(str(a[0]) + ':' + str(a[1]), "disconnected")
                self.connections.remove(c)
                self.peers.remove(a[0])
                del p2p.peersCoordinates[a]
                c.close()
                self.sendPeers()
                break

    def sendPeers(self):
        p = ""
        for peer in self.peers:
            p = p + peer + ","

        for connection in self.connections:
            connection.send(b'\x11' + bytes(p,"utf-8"))



class Client:
    def sendMsg(self):
            while True:
                globals.sock.send(bytes(input(""), 'utf-8'))

    def __init__(self,address):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((address,10000))
        globals.sock = sock

        print("START ITHREAD")
        iThread = threading.Thread(target=self.sendMsg)
        iThread.daemon = True
        iThread.start()
        print("END ITHREAD")


        while True:
            data = globals.sock.recv(1024)
            if not data:
                break
            if data[0:1] == b'\x11':
                self.updatePeers(data[1:])
                print(p2p.peers)
                print("got peers")
                globals.peers = p2p.peers
            # else:
            #     print(str(data, 'utf-8'))

    def updatePeers(self, peerData):
        p2p.peers = str(peerData, "utf-8").split(",")[:-1]

class p2p:
    peers = []
    peersCoordinates = {}



globals.initialize()
response = input("Do you want to host a game? Y/n")
if response.lower() == 'y':
    p2p.peers.append('127.0.0.1')
elif response.lower() == 'n':
    p2p.peers.append(input("Enter address of host peer: "))
else:
    print("Invalid input")

first_time = True
while True:
    try:
        print("Trying to connect ...")
        time.sleep(randint(1,5))
        for peer in p2p.peers:
            if first_time:
                gameThread = threading.Thread(target=Game)
                gameThread.daemon = True
                gameThread.start()
                first_time = False

            try:
                client = Client(peer)
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception:
                pass

            try:
                server = Server()
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception:
                pass

            

    except KeyboardInterrupt:
        sys.exit(0)

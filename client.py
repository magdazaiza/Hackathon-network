import socket
import struct
import sys
from msvcrt import getche
from threading import Thread
import time
import keyboard

UDPPort = 13117
buffSize = 1024


# thread func that sends packets to the server
def startingGameThread(sock):
    endtime = time.time() + 10
    while time.time() < endtime:
        try:
            # sock.settimeout(max(0, endtime - time.time()))
            keyPressed = getche()  # get char from user ( input user)
            sock.sendall(keyPressed)
            break
        except:
            pass
# Get the result msg from the server
def recievingResult(sock):
    while True:
        try:
            data = sock.recv(2048)
            print(data.decode('utf-8'))  # summary message
            break
        except:
            pass
# fun that starts the game by opining two threads:
# one thread for sending
# the other thread for lisining for the result at the end of the game
def SendDataByThread(sock):
    DataIsFound = False
    endtime = time.time() + 10
    while time.time() < endtime and not DataIsFound:  # the server 10 sec to give us the permition to start the game
        data = sock.recv(2048)  # recieve the Welcom message and Players Names
        if data is not None:  # starting the game
            print(data.decode('utf-8'))
            sendingThread = Thread(target=startingGameThread, args=(sock,))  # starting a thread to send packets (msg)
            recievingThread = Thread(target=recievingResult, args=(sock,))  # starting a thread to recieve packets (msg)
            sendingThread.start()
            recievingThread.start()
            sendingThread.join()
            recievingThread.join()
            DataIsFound = True
# init TCP connection with the server
def TCPConn(TCP_Port, host):
    # TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (host, TCP_Port)
    try:
        sock.connect(server_address)
    except:
        print("connection failed")
    return sock
# init udp connection that listen to UDP packets to get the broadcast
def UDPConn():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return client

def Main(TeamName):
    print("Client started,listening for offer requests...")
    client = UDPConn()  # init udp connection
    try:
        client.bind(("", UDPPort))
    except:
        print("error binding")
    while True:
        data, address = client.recvfrom(buffSize)
        host, UDP_Port = address
        try:
            Magic_cookie, Message_type, TCP_Port = struct.unpack('!IBH', data)
            if Magic_cookie == 0xabcddcba and Message_type == 0x2:  # checking recieved message from broadcast
                received_offer = "received offer from " + host + ",attempting to connect..."
                print(received_offer)
                sock = TCPConn(TCP_Port, host)  # init tcp connection
                try:
                    sock.sendall(TeamName.encode('utf-8'))  # sending the team name
                    SendDataByThread(sock)  # calling fun start the game (answer)
                    print("Server disconnected, listening for offer requests...")
                except:
                    print("server closed")
                finally:
                    sock.close()
        except:
            pass
        break
        # OR
        # Main(TeamName)


if __name__ == '__main__':
    args = sys.argv[1:]
    Main(args[0] + "\n")

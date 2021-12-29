from socket import *
from struct import *
import time
import threading
import random

clients = []  # threads
names = []  # clients_names
BroadcastIP = '255.255.255.255'
BroadcastPort = 13117
answers = []


def Main():
    ourPort = random.randint(2000, 40000)
    sock = TCPInitConnection(ourPort)  # calling fun to init the TCP connection
    cs, message = UDPInitConnection(ourPort)  # calling fun to init the UDP connection
    try:
        sock.listen()
        while True:
            clients = []
            random_expression = randomExpression()
            while len(clients) != 2:
                try:
                    cs.sendto(message, (BroadcastIP, BroadcastPort))  # broadcast
                except:
                    print("broadcasting failed")
                time.sleep(1)
                sock.settimeout(0)  # non blocking con
                try:
                    connection, addr = sock.accept()  # initializing threads
                    connection.settimeout(0)  # set the connection socket non blocking
                    new_client = threading.Thread(target=threaded, args=(connection, random_expression))
                    clients.append(new_client)
                except:
                    pass
            # starting the game by stating the thread of each player
            for x in clients:
                x.start()
            for x in clients:
                x.join()
            Main()  # continue listening to clients after the end of game
    except:
        pass


# Client Thread in Server
def threaded(connection, random_expression):  # run func for threading
    ClientName = ''
    ClientName = getTeamName(ClientName, connection)  # giving the client 10 sec to send his name
    while len(names) < 2:
        continue
    message = "Hi " + ClientName + "\n" \
                                   "Welcome to Quick Maths.\n" \
                                   "player 1 : " + names[0] + "\n" \
                                                              "player 2 : " + names[1] + " \n" \
                                                                                         "==\n" \
                                                                                         "Please answer the following question as fast as you can:\n" \
                                                                                         "How much is " + random_expression + "?"

    try:
        connection.sendall(message.encode('utf-8'))  # send welcome msg
    except:
        print("connection from client lost")
        try:
            connection.close()
            return
        except:
            return
    valid_result = eval(random_expression)
    answer = getKeyboardInput(connection)
    answers.append(answer)
    winner_msg = "\nCongratulations to the winner: " + ClientName
    looser_msg = "\nGame over!\n" + "The correct answer was " + str(valid_result) + "!"
    if len(answers) > 1:
        print(ClientName + ": someone answer before me !")
        if int(answers[0]) == int(valid_result):
            try:
                connection.sendall(winner_msg.encode('utf-8'))  # send summary message
                print("Game over, sending out offer requests...")
                connection.close()
            except:
                print("connection from client lost")
                try:
                    connection.close()
                    return
                except:
                    return
        else:
            try:
                connection.sendall(looser_msg.encode('utf-8'))  # send summary message
                print("Game over, sending out offer requests...")
                connection.close()
            except:
                print("connection from client lost")
                try:
                    connection.close()
                    return
                except:
                    return
    else:
        print(ClientName + ": answer firstly !", len(answers))
        if int(answer) == int(valid_result):
            try:
                connection.sendall(winner_msg.encode('utf-8'))  # send summary message
                print("Game over, sending out offer requests...")
                connection.close()
            except:
                print("connection from client lost")
                try:
                    connection.close()
                    return
                except:
                    return
        else:
            try:
                connection.sendall(looser_msg.encode('utf-8'))  # send summary message
                print("Game over, sending out offer requests...")
                connection.close()
            except:
                print("connection from client lost")
                try:
                    connection.close()
                    return
                except:
                    return


# Get the result from the client
def getKeyboardInput(connection):
    answer = ""
    endTime = time.time() + 10
    while time.time() < endTime:
        try:
            data = connection.recv(1)
            if data:
                answer = data.decode('utf-8')
                print(answer)
                break
        except:
            pass
    if answer == "":
        return -1
    return answer


# Get the name of the team by the connection
def getTeamName(ClientName, connection):
    while True:
        try:
            data = connection.recv(1)
            if data.decode('utf-8') == '\n':
                break
            else:
                ClientName = ClientName + data.decode('utf-8')
        except:
            pass
    names.append(ClientName)
    return ClientName


# Create a random arithmetic expression
def randomExpression():
    left = random.randint(0, 5)
    op = random.choice(["+", "-"])
    right = random.randint(0, left)
    return str(left) + str(op) + str(right)


# Init UDP connection
def UDPInitConnection(ourPort):
    cs = socket(AF_INET, SOCK_DGRAM)
    cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    message = pack('!IBH', 0xabcddcba, 0x2, ourPort)
    return cs, message


# Init TCP connection
def TCPInitConnection(ourPort):
    # TCP
    host = gethostname()
    print("server started, listening on IP address", gethostbyname(host))
    sock = socket(AF_INET, SOCK_STREAM)
    server_address = (host, ourPort)
    try:
        sock.bind(server_address)
    except:
        print("error binding{end}")
    return sock


if __name__ == '__main__':
    Main()

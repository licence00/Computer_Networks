#https://pythontic.com/modules/socket/udp-client-server-example
import socket
import math

localIP     = "127.0.0.1"
localPort   = 20001
bufferSize  = 1024

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

#print("UDP server up and listening")

# Listen for incoming datagrams
while (True):
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0].decode()
    address = bytesAddressPair[1]
    print("Received : " + message)
    #clientMsg = "Message from Client: {}".format(message)
    #clientIP  = "Client IP Address: {}".format(address)
    sent = message.split()
    if sent[0] == "add" :
        ans = (int(sent[1]))+(int(sent[2]))
    elif sent[0] == "mul" :
        ans = (int(sent[1]))*(int(sent[2]))
    elif sent[0] == "mod" :
        ans = (int(sent[1]))%(int(sent[2]))
    elif sent[0] == "hyp" : 
        a = int(sent[1])
        b = int(sent[2])
        ans = math.sqrt(a**2+b**2)
    msgFromServer = str(ans)

    # Sending a reply to client
    UDPServerSocket.sendto(msgFromServer.encode(), address)

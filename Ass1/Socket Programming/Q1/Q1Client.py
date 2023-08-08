#https://pythontic.com/modules/socket/udp-client-server-example
import socket

serverAddressPort   = ("127.0.0.1", 20001)
bufferSize          = 1024

msgFromClinet = input("Enter the Message : ")
bytesToSend = str.encode(msgFromClinet)
# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send to server using created UDP socket
UDPClientSocket.sendto(bytesToSend, serverAddressPort)

#Wait on recvfrom()
msgFromServer = UDPClientSocket.recvfrom(bufferSize)

#Wait completed
msg = msgFromServer[0].decode()

print("Message from Server : " + msg)

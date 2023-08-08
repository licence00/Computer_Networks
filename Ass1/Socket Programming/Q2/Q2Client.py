#https://pythontic.com/modules/socket/udp-client-server-example
import socket

serverAddressPort   = ("127.0.0.1", 20001)
bufferSize          = 1024

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

s=input("Enter Command : ")
bytesToSend = str.encode(s)

# Send to server using created UDP socket
UDPClientSocket.sendto(bytesToSend, serverAddressPort)

#Wait on recvfrom()
msgFromServer = UDPClientSocket.recvfrom(bufferSize)

#Wait completed

msg = "{}".format(msgFromServer[0].decode())
print("Answer from Server : " + msg)

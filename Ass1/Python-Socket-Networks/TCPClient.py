#https://pythontic.com/modules/socket/send
import socket
serverName = "127.0.0.1"
serverPort = 35001
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clientSocket.connect((serverName,serverPort))

sentence = input("Input lowercase sentence: ")

clientSocket.send(sentence.encode())

modifiedSentence = clientSocket.recv(1024)

print("From Server: ", modifiedSentence.decode())

clientSocket.close()

#https://pythontic.com/modules/socket/send
import socket 
import os

serverPort = 12000

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serverSocket.bind(('localhost',serverPort))

serverSocket.listen(1)

print("The Server is ready to Receive")

while (True):
    (connectionSocket, clientAddress) = serverSocket.accept()
    print("Accepted a connection request from %s:%s"%(clientAddress[0], clientAddress[1]))
    orgsentence = connectionSocket.recv(1024)
    orgsentence = orgsentence.decode()
    orglist = orgsentence.split("+")
    filename = orglist[0] 
    nbytes = int(orglist[1])
    currentpath = os.getcwd()
    checkfilepath = currentpath+'/'+filename
    bool_path = os.path.exists(checkfilepath)
    if bool_path == True :
        f = open(checkfilepath,"r")
        file_size = os.path.getsize(checkfilepath)
        wanted = file_size-int(nbytes)
        sentence = ""
        for i in range(0,file_size) :
            x = f.read(1)
            if i >= wanted :
                sentence = sentence + str(x)
        f.close()
        connectionSocket.send(sentence.encode())
    else :
        sendSentence = "SORRY!"    
        connectionSocket.send(sendSentence.encode())
    connectionSocket.close()

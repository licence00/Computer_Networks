#https://pythontic.com/modules/socket/send
import socket
serverName = 'localhost'
serverPort = 12000
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clientSocket.connect((serverName,serverPort))

sentence = input("Input the Filename : ")
nbytes = input("Enter the Value of N : ")

orgsentence = sentence + "+" + nbytes

clientSocket.send(orgsentence.encode())

modifiedSentence = clientSocket.recv(1024)

modifiedSentence = modifiedSentence.decode()

if modifiedSentence == "SORRY!" :
    print("Server says that the file does not exist.")
else :
    filenames = sentence.split(".")
    if len(filenames) == 1 :
        name = filenames[0] + str(1)        
    else :
        name = filenames[0] + str(1) + "."
        for i in range(1,len(filenames)-1) : 
            name = name + filenames[i] + "."
        name = name + filenames[len(filenames)-1]
    filename1 = name
    f = open(filename1,"w")
    f.write(modifiedSentence)
    f.close()
clientSocket.close()

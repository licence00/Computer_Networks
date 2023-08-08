'''
    NAME: Sai Siddarth Peta
    Roll Number: CS20B059
    Course: CS3205 Jan. 2023 semester
    Lab number: 2
    Date of submission: 04-03-2023
    I confirm that the source file is entirely written by me without resorting to any dishonest means.
    Website(s) that I used for basic socket programming code are:
    URL(s): None
'''

import os
import socket
import time

bufferSize = 1024 #Initilaize the buffer size to 1024 Bytes

#Taking the Input from the User (StartPortNum)
startportnum = int(input("Enter the Start Port Number : "))
#Taking the Input from the User (InputFileName)
filename = input("Enter the Input File Name : ")

#Extracting the Data from the Input File
DNSIPAddress,AUTHIPAddress,mini_server = {},{},{}
f = open(filename,"r")
f.readline()
#Extracting the DNS Servers IP Address and Mapping them to their Names
for i in range(0,10):
    lines = f.readline() #Reading the file line by line
    address = lines.split()
    #Adding the DNS Server's IP Address to the DNSIPAddress Dictionary
    if i>=4 :
        key = "ADS" + str(i-3)
        DNSIPAddress[key]=address[1] #Mapping the ADS Server's Name to their IP Address
    DNSIPAddress[address[0]]=address[1] #Mapping the DNS Server's Name to their IP Address

servers = []
auth_server = ""
i = 56
while True:
    #Reading the file line by line
    line = f.readline()
    #If file reaches end of the file ("END_DATA") break the loop
    if line == "END_DATA":
        break
    else:
        check = line[0:4]
        if check == "List" :
            #If the line starts with "List" then it is the start of a new server
            auth_server = line[8:12] #Extracting the Authorization Server Name
            mini_server = {}
            servers.append(mini_server)
            i = i+1
            continue
        else:
            values = line.split()
            mini_server[values[0]]=values[1] #Adding the Site Name and IP Address to the mini_server Dictionary
            site_name = values[0]
            auth_name = site_name.split('.')
            #Adding the all Authorization Server's IP Address and Port NUmbers to the AUTHIPAddress Dictionary
            AUTHIPAddress[auth_name[1]] = (DNSIPAddress[auth_server],startportnum+i) 
        
servers.append(mini_server)
f.close() #Closing the file

#Opening the Output Files for writing the data
f1 = open('NR.output',"w")
f2 = open('RDS.output',"w")
f3 = open('TDS.output',"w")
f4 = open('ADS.output',"w")

#Creating the Server Sockets based on the Value of 'i'
def create_Server(i):
    if i==0:
        #Creating the Server Socket for the Name Resolver Server
        #Storing the Information of Client
        clientportnumber = 0
        chance = [True,False,False,False]
        #Creating the Server Socket with family = IPv4 and type = UDP
        UDPServerSocket1 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #Binding the Server Socket to the IP Address and Port Number
        UDPServerSocket1.bind(('localhost', startportnum + 53))
        while True:
            bytesAddressPair = UDPServerSocket1.recvfrom(bufferSize)
            messageReceived = bytesAddressPair[0].decode()
            address = bytesAddressPair[1]
            #If Client sends "kill" then close the Server Socket and exit the program
            if messageReceived == "kill":
                UDPServerSocket1.close()
                exit()
            #If any Server sends "No" then send the message to the Client (Site found No Match)
            elif messageReceived == "No":
                #Writing the Information to the Output File (NR.output)
                sendinfo = "Response Sent : {} to Address {}\n\n".format(messageReceived,('localhost',clientportnumber))
                f1.write(sendinfo)
                #Sending the message to the Client
                UDPServerSocket1.sendto(messageReceived.encode(),('localhost',clientportnumber))
                #Resetting the chance list (Restart the process)
                chance = [True,False,False,False]
            else:
                if chance[0] == True:
                    #Sending to RDS server
                    clientportnumber = address[1]
                    #Writing the Information to the Output File (NR.output)
                    receivedinfo ="Query Received : {} from the Address {}\n\n".format(messageReceived,address)
                    f1.write(receivedinfo)
                    #Sending the message to the RDS Server
                    UDPServerSocket1.sendto(messageReceived.encode(),('localhost' , startportnum + 54))
                    sendinfo = "Response Sent : {} to Address {}\n\n".format(DNSIPAddress['RDS'],startportnum+54)
                    f1.write(sendinfo)
                    chance[0] = False
                    chance[1] = True
                elif chance[1] == True:
                    #Sending to TDS server
                    receivedinfo = "Query Received : {} from the Address {}\n\n".format(messageReceived,(DNSIPAddress['RDS'],startportnum+54))
                    f1.write(receivedinfo)
                    check_TDS = messageReceived.split()
                    port_number = int(check_TDS[2]) #Assigning the Port Number to TDS_com or TDS_edu
                    messagetosend = check_TDS[0] 
                    #Sending the message to the appropriate TDS Server (TDS_com or TDS_edu)
                    UDPServerSocket1.sendto(messagetosend.encode(),('localhost' , port_number))
                    #Writing the Information to the Output File (NR.output)
                    if port_number-55 == startportnum:
                        sendinfo = "Response Sent : {} to Address {}\n\n".format(messagetosend,(DNSIPAddress['TDS_com'],startportnum+55))
                        f1.write(sendinfo)
                    else:
                        sendinfo = "Response Sent : {} to Address {}\n\n".format(messagetosend,(DNSIPAddress['TDS_edu'],startportnum+56))
                        f1.write(sendinfo)
                    chance[1] = False 
                    chance[2] = True
                elif chance[2] == True:
                    #Sending to ADS server
                    check_ads = messageReceived.split()
                    site = check_ads[0].split('.')
                    #Assigning the Port Number to appropriate ADS Server
                    port_number = int(check_ads[2])
                    #Writing the Information to the Output File (NR.output)
                    if site[2] == "com":
                        receivedinfo = "Query Received : {} from the Address {}\n\n".format(messageReceived,(DNSIPAddress['TDS_com'],startportnum+54))
                        f1.write(receivedinfo)
                    else:
                        receivedinfo = "Query Received : {} from the Address {}\n\n".format(messageReceived,(DNSIPAddress['TDS_edu'],startportnum+54))
                        f1.write(receivedinfo)
                    sendinfo = "Response Sent : {} to Address {}\n\n".format(check_ads[0],(check_ads[1],check_ads[2]))
                    f1.write(sendinfo)
                    #Sending the message to the appropriate ADS Server (assigned by TDS Server)
                    UDPServerSocket1.sendto(check_ads[0].encode(),('localhost' , port_number))
                    chance[2] = False
                    chance[3] = True
                elif chance[3] == True:
                    #Sending to Client
                    #Sending the message to the Client received from the ADS Server
                    sendinfo = "Response Sent : {} to Address {}\n\n".format(messageReceived,('localhost',clientportnumber))
                    f1.write(sendinfo)
                    #Sending the message to the Client
                    UDPServerSocket1.sendto(messageReceived.encode(),('localhost',clientportnumber))
                    chance[3] = False
                    #Resetting the chance list (Restart the process)
                    chance = [True,False,False,False]
    elif i==1:
        #Creating the Server Socket for the Root DNS Server
        #Creating the Server Socket with family = IPv4 and type = UDP
        UDPServerSocket2 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #Binding the Server Socket to the IP Address and Port Number
        UDPServerSocket2.bind(('localhost',startportnum + 54))
        while True:
            bytesAddressPair = UDPServerSocket2.recvfrom(bufferSize)
            messageReceived = bytesAddressPair[0].decode()
            #If Client sends "kill" then close the Server Socket and exit the program
            if messageReceived == "kill":
                UDPServerSocket2.close()
                exit()
            else:
                Receivedinfo = "Query Received : {} from the Address {}\n\n".format(messageReceived,(DNSIPAddress['NR'],startportnum+53))
                f2.write(Receivedinfo)
                TDS_check = messageReceived.split('.')
                messagetosend = messageReceived
                #Checking whether the message belongs to TDS_com or TDS_edu Servers
                if TDS_check[2] == "com": #If the message end with ".com" then it belongs to TDS_com Server
                    messagetosend = messagetosend + " " + DNSIPAddress["TDS_com"] + " " + str(startportnum+55)
                elif TDS_check[2] == "edu": #If the message end with ".edu" then it belongs to TDS_edu Server
                    messagetosend = messagetosend + " " + DNSIPAddress["TDS_edu"] + " " + str(startportnum+56)
                else:   #If the message does not belong to any of the TDS Servers then send "No" to the NR Server
                    messagetosend = "No"
                #Writing the Information to the Output File (RDS.output)
                sendinfo = "Response Sent : {} to address {}\n\n".format(messagetosend,(DNSIPAddress['NR'],startportnum+53))
                f2.write(sendinfo)
                #Sending the message to the NR Server
                UDPServerSocket2.sendto(messagetosend.encode(),('localhost', startportnum + 53))
    elif i==2:
        #Creating the Server Socket for the TDS_com Server
        #Creating the Server Socket with family = IPv4 and type = UDP
        UDPServerSocket3 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #Binding the Server Socket to the IP Address and Port Number
        UDPServerSocket3.bind(('localhost',startportnum + 55))
        while True:
            bytesAddressPair = UDPServerSocket3.recvfrom(bufferSize)
            messageReceived = bytesAddressPair[0].decode()
            #If Client sends "kill" then close the Server Socket and exit the program
            if messageReceived == "kill":
                UDPServerSocket3.close()
                exit()
            else:
                Receivedinfo = "Query Received : {} from the Address {}\n\n".format(messageReceived,(DNSIPAddress['NR'],startportnum+53)) 
                f3.write(Receivedinfo)
                check_ads = messageReceived.split('.')
                #Checking whether the Site(Message Sent) belongs to ADS1 or ADS2 or ADS3
                if AUTHIPAddress.get(check_ads[1]) == None:
                    messagetosend = "No" #If the Site does not belong to any of the ADS Servers then send "No" to the NR Server
                else:
                    #If the Site belongs to any of the ADS Servers then send the IP Address and Port Number of the ADS Server to the NR Server
                    get_tuple = AUTHIPAddress.get(check_ads[1])
                    messagetosend = messageReceived + " " + get_tuple[0] + " " + str(get_tuple[1])
                #Writing the Information to the Output File (TDS.output)
                sendinfo = "Response Sent : {} to address {}\n\n".format(messagetosend,(DNSIPAddress['NR'],startportnum+53))
                f3.write(sendinfo)
                #Sending the message to the NR Server
                UDPServerSocket3.sendto(messagetosend.encode(),('localhost', startportnum + 53))
    elif i==3:
        #Creating the Server Socket for the TDS_edu Server
        #Creating the Server Socket with family = IPv4 and type = UDP
        UDPServerSocket4 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #Binding the Server Socket to the IP Address and Port Number
        UDPServerSocket4.bind(('localhost',startportnum + 56))
        while True:
            bytesAddressPair = UDPServerSocket4.recvfrom(bufferSize)
            messageReceived = bytesAddressPair[0].decode()
            #If Client sends "kill" then close the Server Socket and exit the program
            if messageReceived == "kill":
                UDPServerSocket4.close()
                exit()
            else:
                Receivedinfo = "Query Received : {} from the Address {}\n\n".format(messageReceived,(DNSIPAddress['NR'],startportnum+53)) 
                f3.write(Receivedinfo)
                check_ads = messageReceived.split('.')
                #Checking whether the Site(Message Sent) belongs to ADS4 or ADS5 or ADS6
                if AUTHIPAddress.get(check_ads[1]) == None:
                    messagetosend = "No" #If the Site does not belong to any of the ADS Servers then send "No" to the NR Server
                else:
                    #If the Site belongs to any of the ADS Servers then send the IP Address and Port Number of the ADS Server to the NR Server
                    get_tuple = AUTHIPAddress.get(check_ads[1])
                    messagetosend = messageReceived + " " + get_tuple[0] + " " + str(get_tuple[1])
                #Writing the Information to the Output File (TDS.output)
                sendinfo = "Response Sent : {} to address {}\n\n".format(messagetosend,(DNSIPAddress['NR'],startportnum+53))
                f3.write(sendinfo)
                #Sending the message to the NR Server
                UDPServerSocket4.sendto(messagetosend.encode(),('localhost', startportnum + 53))
    elif i==4:
        #Creating the Server Socket for the ADS1 Server
        #Creating the Server Socket with family = IPv4 and type = UDP
        UDPServerSocket5 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #Binding the Server Socket to the IP Address and Port Number
        UDPServerSocket5.bind(('localhost',startportnum + 57))
        while True:
            bytesAddressPair = UDPServerSocket5.recvfrom(bufferSize)
            messageReceived = bytesAddressPair[0].decode()
            #If Client sends "kill" then close the Server Socket and exit the program
            if messageReceived == "kill":
                UDPServerSocket5.close()
                exit()
            else:
                Receivedinfo = "Query Received : {} from the Address {}\n\n".format(messageReceived,(DNSIPAddress['NR'],startportnum+53)) 
                f4.write(Receivedinfo)
                messagetosend = str()
                #Checking whether the Site(Message Sent) belongs to ADS1 
                if servers[0].get(messageReceived) == None:
                    messagetosend = "No" #If the Site does not belong to ADS1 then send "No" to the NR Server
                else:
                    #If the Site belongs to ADS1 then send the IP Address of the Site to the NR Server
                    messagetosend = messagetosend + servers[0].get(messageReceived)
                #Writing the Response Sent to the "ADS.output"
                sendinfo = "Response Sent : {} to Address {}\n\n".format(messagetosend,(DNSIPAddress['NR'],startportnum+53))
                f4.write(sendinfo)
                #Sending the message to the NR Server
                UDPServerSocket5.sendto(messagetosend.encode(),('localhost', startportnum + 53))
    elif i==5:
        #Creating the Server Socket for the ADS2 Server
        #Creating the Server Socket with family = IPv4 and type = UDP
        UDPServerSocket6 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #Binding the Server Socket to the IP Address and Port Number
        UDPServerSocket6.bind(('localhost',startportnum + 58))
        while True:
            bytesAddressPair = UDPServerSocket6.recvfrom(bufferSize)
            messageReceived = bytesAddressPair[0].decode()
            #If Client sends "kill" then close the Server Socket and exit the program
            if messageReceived == "kill":
                UDPServerSocket6.close()
                exit()
            else:
                Receivedinfo = "Query Received : {} from the Address {}\n\n".format(messageReceived,(DNSIPAddress['NR'],startportnum+53)) 
                f4.write(Receivedinfo)
                messagetosend = str()
                #Checking whether the Site(Message Sent) belongs to ADS2
                if servers[1].get(messageReceived) == None:
                    messagetosend = "No" #If the Site does not belong to ADS2 then send "No" to the NR Server
                else:
                    #If the Site belongs to ADS2 then send the IP Address of the Site to the NR Server
                    messagetosend = messagetosend + servers[1].get(messageReceived)
                #Writing the Response Sent to the "ADS.output"
                sendinfo = "Response Sent : {} to Address {}\n\n".format(messagetosend,(DNSIPAddress['NR'],startportnum+53))
                f4.write(sendinfo)
                #Sending the message to the NR Server
                UDPServerSocket6.sendto(messagetosend.encode(),('localhost', startportnum + 53))
    elif i==6:
        #Creating the Server Socket for the ADS3 Server
        #Creating the Server Socket with family = IPv4 and type = UDP
        UDPServerSocket7 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #Binding the Server Socket to the IP Address and Port Number
        UDPServerSocket7.bind(('localhost',startportnum + 59))
        while True:
            bytesAddressPair = UDPServerSocket7.recvfrom(bufferSize)
            messageReceived = bytesAddressPair[0].decode()
            #If Client sends "kill" then close the Server Socket and exit the program
            if messageReceived == "kill" :
                UDPServerSocket7.close()
                exit()
            else:
                Receivedinfo = "Query Received : {} from the Address {}\n\n".format(messageReceived,(DNSIPAddress['NR'],startportnum+53)) 
                f4.write(Receivedinfo)
                messagetosend = str()
                #Checking whether the Site(Message Sent) belongs to ADS3
                if servers[2].get(messageReceived) == None:
                    messagetosend = "No" #If the Site does not belong to ADS3 then send "No" to the NR Server
                else:
                    #If the Site belongs to ADS3 then send the IP Address of the Site to the NR Server
                    messagetosend = messagetosend + servers[2].get(messageReceived)
                #Writing the Response Sent to the "ADS.output"
                sendinfo = "Response Sent : {} to Address {}\n\n".format(messagetosend,(DNSIPAddress['NR'],startportnum+53))
                f4.write(sendinfo)
                #Sending the message to the NR Server
                UDPServerSocket7.sendto(messagetosend.encode(),('localhost', startportnum + 53))
    elif i==7:
        #Creating the Server Socket for the ADS4 Server
        #Creating the Server Socket with family = IPv4 and type = UDP
        UDPServerSocket8 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #Binding the Server Socket to the IP Address and Port Number
        UDPServerSocket8.bind(('localhost',startportnum + 60))
        while True:
            bytesAddressPair = UDPServerSocket8.recvfrom(bufferSize)
            messageReceived = bytesAddressPair[0].decode()
            #If Client sends "kill" then close the Server Socket and exit the program
            if messageReceived == "kill":
                UDPServerSocket8.close()
                exit()
            else:
                Receivedinfo = "Query Received : {} from the Address {}\n\n".format(messageReceived,(DNSIPAddress['NR'],startportnum+53)) 
                f4.write(Receivedinfo)
                messagetosend = str()
                #Checking whether the Site(Message Sent) belongs to ADS4
                if servers[3].get(messageReceived) == None:
                    messagetosend = "No" #If the Site does not belong to ADS4 then send "No" to the NR Server
                else:
                    #If the Site belongs to ADS4 then send the IP Address of the Site to the NR Server
                    messagetosend = messagetosend + servers[3].get(messageReceived)
                #Writing the Response Sent to the "ADS.output"
                sendinfo = "Response Sent : {} to Address {}\n\n".format(messagetosend,(DNSIPAddress['NR'],startportnum+53))
                f4.write(sendinfo)
                #Sending the message to the NR Server
                UDPServerSocket8.sendto(messagetosend.encode(),('localhost', startportnum + 53))
    elif i==8:
        #Creating the Server Socket for the ADS5 Server
        #Creating the Server Socket with family = IPv4 and type = UDP
        UDPServerSocket9 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #Binding the Server Socket to the IP Address and Port Number
        UDPServerSocket9.bind(('localhost',startportnum + 61))
        while True:
            bytesAddressPair = UDPServerSocket9.recvfrom(bufferSize)
            messageReceived = bytesAddressPair[0].decode()
            #If Client sends "kill" then close the Server Socket and exit the program
            if messageReceived == "kill":
                UDPServerSocket9.close()
                exit()
            else:
                Receivedinfo = "Query Received : {} from the Address {}\n\n".format(messageReceived,(DNSIPAddress['NR'],startportnum+53)) 
                f4.write(Receivedinfo)
                messagetosend = str()
                #Checking whether the Site(Message Sent) belongs to ADS5
                if servers[4].get(messageReceived) == None:
                    messagetosend = "No"    #If the Site does not belong to ADS5 then send "No" to the NR Server
                else:
                    #If the Site belongs to ADS5 then send the IP Address of the Site to the NR Server
                    messagetosend = messagetosend + servers[4].get(messageReceived)
                #Writing the Response Sent to the "ADS.output"
                sendinfo = "Response Sent : {} to Address {}\n\n".format(messagetosend,(DNSIPAddress['NR'],startportnum+53))
                f4.write(sendinfo)
                #Sending the message to the NR Server
                UDPServerSocket9.sendto(messagetosend.encode(),('localhost', startportnum + 53))
    elif i==9:
        #Creating the Server Socket for the ADS6 Server
        #Creating the Server Socket with family = IPv4 and type = UDP
        UDPServerSocket10 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        #Binding the Server Socket to the IP Address and Port Number
        UDPServerSocket10.bind(('localhost',startportnum + 62))
        while True:
            bytesAddressPair = UDPServerSocket10.recvfrom(bufferSize)
            messageReceived = bytesAddressPair[0].decode()
            #If Client sends "kill" then close the Server Socket and exit the program
            if messageReceived == "kill":
                UDPServerSocket10.close()
                exit()
            else:
                Receivedinfo = "Query Received : {} from the Address {}\n\n".format(messageReceived,(DNSIPAddress['NR'],startportnum+53)) 
                f4.write(Receivedinfo)
                messagetosend = str()
                #Checking whether the Site(Message Sent) belongs to ADS6
                if servers[5].get(messageReceived) == None:
                    messagetosend = "No"   #If the Site does not belong to ADS6 then send "No" to the NR Server
                else:
                    #If the Site belongs to ADS6 then send the IP Address of the Site to the NR Server
                    messagetosend = messagetosend + servers[5].get(messageReceived)
                #Writing the Response Sent to the "ADS.output"
                sendinfo = "Response Sent : {} to Address {}\n\n".format(messagetosend,(DNSIPAddress['NR'],startportnum+53))
                f4.write(sendinfo)
                #Sending the message to the NR Server
                UDPServerSocket10.sendto(messagetosend.encode(),('localhost', startportnum + 53))

#Creating Child process each for a server using fork()
for i in range(0,10):
    pid = os.fork()
    #Child process 
    if pid == 0: 
        #calling the function to create the server based on the value of i
        create_Server(i) 
        exit()
    elif pid < 0:
        #If fork fails then exit the program
        print("Fork failed")
        exit()

#Creating the Client Socket
#Creating the Client Socket with family = IPv4 and type = UDP
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
#Assigning the IP Address and Port Number of the NR Server to the variable serverAddressPort
serverAddressPort = ('localhost', startportnum + 53)

while True:
    #Taking the input from the user (Site Name or Message)
    msgFromClient = input("Enter the Message : ")
    #If the user enters "bye" then stop taking input from the User
    if msgFromClient == "bye":
        #Sending "kill" to all the servers to close the Server Sockets using for loop
        for i in range(startportnum+53,startportnum+63):
            UDPClientSocket.sendto("kill".encode(),('localhost',i))
        UDPClientSocket.close() #Closing the Client Socket
        #Closing the files
        f1.close()
        f2.close()
        f3.close()
        f4.close()
        exit() #Exit the program
    else:
        bytesToSend = str.encode(msgFromClient)
        time.sleep(1)
        #Sending the message to the NR Server
        UDPClientSocket.sendto(bytesToSend, serverAddressPort)
        print("Response Sent : {} to Address {}".format(msgFromClient,(DNSIPAddress['NR'],startportnum+53)))
        #Receiving the response from the NR Server
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)
        msg = msgFromServer[0].decode()
        #Checking whether the IP address sent (Message Received) is Valid or not 
        if msg == "No":
            #If the IP Address is not Valid then print "No Mapping Found to the Site"
            print("No Mapping Found to the Site")
        else:
            #If the IP Address is Valid then print the IP Address
            print("The IP Address from DNS Server is : " + msg)
    #Continuing the loop until the user enters "bye"
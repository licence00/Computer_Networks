import socket
import random
import time
import sys
import numpy as np
import threading

if "-f" in sys.argv:
    inputfilename = sys.argv[sys.argv.index("-f")+1]
if "-h" in sys.argv:
    HELLO_INTERVAL = int(sys.argv[sys.argv.index("-h")+1])
if "-s" in sys.argv:
    SPF_INTERVAL = int(sys.argv[sys.argv.index("-s")+1])
if "-a" in sys.argv:
    LSA_INTERVAL = int(sys.argv[sys.argv.index("-a")+1])
if "-o" in sys.argv:
    outputfilename = sys.argv[sys.argv.index("-o")+1]
if "-i" in sys.argv:
    want = int(sys.argv[sys.argv.index("-i")+1])

#Change this accordingly
number_of_tables = 3
maximum_time = number_of_tables * SPF_INTERVAL + 1

#Sending the Hello packets to its neighbours
def send_HELLO(node):
    global UDPSocket
    global start_time
    while True:
        if time.time() - start_time > maximum_time:
            break
        for i in range(routers):
            if i != node and graph[i][node] != -1:
                #the message sent is "HELLO <node>"
                bytesTosend = "HELLO" + " " + str(node) 
                #send the message to the port of the neighbour
                UDPSocket[node].sendto(bytesTosend.encode(),('127.0.0.1',10000+i))
        time.sleep(HELLO_INTERVAL)
        
#Sending the LSA packets to its neighbours
def send_LSA(node):
    global LSA_INTERVAL
    global start_time
    while True:
        if time.time() - start_time > maximum_time:
            break
        time.sleep(LSA_INTERVAL)
        sequence_number = 0 #assign a sequence number to each LSA packet
        messageTosend = "LSA" + " " + str(node) + " " + str(sequence_number)	
        no_of_entries = 0
        add = str()
        for i in range(routers):
            if i != node and distance[node][node][i] != -1:
                no_of_entries = no_of_entries + 1
                add = add + " " + str(i) + " " + str(distance[node][node][i])
        #the message contains the sequence number, srcid ,number of entries and the entries(neighbour,cost)
        messageTosend = messageTosend + " " + str(no_of_entries) + add
        #send the message to the port of the neighbour
        for i in range(routers):
            if i != node and distance[node][node][i] != -1:
                UDPSocket[node].sendto(messageTosend.encode(),('127.0.0.1',10000+i))
        sequence_number = sequence_number + 1

#Receiving the packets sent from its neighbours
def receive_Router(node):
    global start_time
    while True:
        if time.time() - start_time > maximum_time:
            break
        message = UDPSocket[node].recvfrom(1024)
        message_Received = message[0].decode().split()
        from_node = int(message[1][1]-10000)
        #if the message is a Hello packet
        if message_Received[0] == "HELLO":
            messageTosend = str()
            #selecting a random distance between the range of the link
            random_distance = random.randint(graph[node][from_node][0]+1,graph[node][from_node][1]-1) 
            #sending the HelloReply message to the neighbour
            messageTosend = "HELLOREPLY" + " " + str(from_node) + " " + str(node) + " " + str(random_distance)
            UDPSocket[node].sendto(messageTosend.encode(),('127.0.0.1',10000+from_node))
        elif message_Received[0] == "HELLOREPLY": #if the message is a HelloReply packet
            #storing the distance in the local graph table
            distance[node][int(message_Received[1])][int(message_Received[2])] = int(message_Received[3])
        elif message_Received[0] == "LSA": #if the message is a LSA packet
            #check the seq_number is greater than the received_seq_number from that particular neighbour
            if int(message_Received[2]) >= seq_numbers[node][from_node]:
                seq_numbers[node][from_node] = int(message_Received[2])
                srcid = int(message_Received[1])
                start_index = 4
                for i in range(int(message_Received[3])):
                    #storing the distance in the local graph table
                    distance[node][srcid][int(message_Received[start_index])] = int(message_Received[start_index+1])
                    start_index = start_index + 2 #incrementing the start_index to read the next neighbour and cost
                for i in range(routers):
                    send_Message = message[0].decode()
                    #forwarding the LSA packet to all the neighbours except the one from which it received the packet
                    if i != node and distance[node][node][i] != -1 and i != from_node:
                        UDPSocket[node].sendto(send_Message.encode(),('127.0.0.1',10000+i))

#dijkstra's algorithm to find the shortest path from the source to all the other nodes
def find_min_path(node):
    min_distance = [float("inf")] * routers
    visited = [False] * routers
    min_distance[node] = 0
    dist_path = [str(node)+"-"] * routers

    for i in range(routers):

        min_dist = float("inf")
        min_node = -1

        for j in range(routers):
            if visited[j] == False and min_distance[j] < min_dist:
                min_dist = min_distance[j]
                min_node = j

        visited[min_node] = True

        for j in range(routers):
            if distance[node][min_node][j] != -1 and visited[j] == False and min_distance[j] > distance[node][min_node][j] + min_distance[min_node]:
                    min_distance[j] = distance[node][min_node][j] + min_distance[min_node]
                    dist_path[j] = dist_path[min_node] + str(j) + "-" #updating the path

    return min_distance,dist_path

#Printing the routing table for each node
def Routing_Table(node):
    global start_time
    global outputfileptr
    time_now = 0
    while True:
        if time.time() - start_time > maximum_time:
            break
        time.sleep(SPF_INTERVAL)
        time_now = time_now + SPF_INTERVAL
        outputfileptr[node].write("Routing Table for Node No. "+str(node)+" at time "+str(time_now)+"\n")
        outputfileptr[node].write("Destination\t\tPath\t\t\t\tCost\n")
        min_distance,dist_path = find_min_path(node)
        for j in range(len(min_distance)):
            if node != j :
                outputfileptr[node].write("\t" + str(j)+"\t\t" + dist_path[j][:-1] + "\t\t\t\t" + str(min_distance[j]) + "\n")

#Reading the input file
ptr = open(inputfilename,"r")
first_line = ptr.readline()
routers = int(first_line.split()[0])
links = int(first_line.split()[1])

graph = [[-1] * routers for i in range(routers)]
distance = np.full((routers,routers,routers), -1)
seq_numbers = np.full((routers,routers),-1)

for i in range(links):
    line = ptr.readline()
    info = line.split()
    graph[int(info[0])][int(info[1])]=(int(info[2]),int(info[3]))
    graph[int(info[1])][int(info[0])]=(int(info[2]),int(info[3]))

UDPSocket = np.zeros(routers,dtype=object)
for i in range(routers):
    UDPSocket[i] = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) 
    UDPSocket[i].bind(('127.0.0.1',10000+i))

#Opening the outputfiles for each router
outputfileptr = [0] * routers
for i in range(routers):
    outputfileptr[i] = open(outputfilename+"-"+str(i)+".txt","w")

#Creating the threads for each router
threads = np.zeros((routers,4),dtype=object)
start_time = time.time()
for i in range(routers):
    threads[i][0] = threading.Thread(target=send_HELLO,args=(i,))
    threads[i][0].start()
    threads[i][1] = threading.Thread(target=send_LSA,args=(i,))
    threads[i][1].start()
    threads[i][2] = threading.Thread(target=receive_Router,args=(i,))
    threads[i][2].start()
    threads[i][3] = threading.Thread(target=Routing_Table,args=(i,))
    threads[i][3].start()

#time.sleep(maximum_time)
while True:
    if time.time() - start_time > maximum_time + 2:
        print("Time Completed")
        break
    print("Processing |", end="\r")
    time.sleep(0.5)
    print("Processing -", end="\r")
    time.sleep(0.5)    

for i in range(routers):
    outputfileptr[i].close()
ptr.close()


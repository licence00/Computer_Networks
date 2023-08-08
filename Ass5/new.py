import socket
import random
import time
import sys
import numpy as np
import threading

HELLO_INTERVAL = 1
LSA_INTERVAL = 5
SPF_INTERVAL = 20

inputfilename = "input.txt"	
outputfilename = "outfile"

def send_HELLO(node):
    global UDPSocket
    while True:
        for i in range(routers):
            if i != node and graph[i][node] != -1:
                bytesTosend = "HELLO" + " " + str(node)
                UDPSocket[node].sendto(bytesTosend.encode(),('127.0.0.1',10000+i))
        time.sleep(HELLO_INTERVAL)
        

def send_LSA(node):
    global LSA_INTERVAL
    while True:
        time.sleep(LSA_INTERVAL)
        sequence_number = 0
        messageTosend = "LSA" + " " + str(node) + " " + str(sequence_number)	
        no_of_entries = 0
        add = str()
        for i in range(routers):
            if i != node and distance[node][node][i] != -1:
                no_of_entries = no_of_entries + 1
                add = add + " " + str(i) + " " + str(distance[node][node][i])
        messageTosend = messageTosend + " " + str(no_of_entries) + add
        for i in range(routers):
            if i != node and distance[node][node][i] != -1:
                UDPSocket[node].sendto(messageTosend.encode(),('127.0.0.1',10000+i))
        sequence_number = sequence_number + 1
        
def receive_Router(node):
    while True:
        message = UDPSocket[node].recvfrom(1024)
        message_Received = message[0].decode().split()
        from_node = int(message[1][1]-10000)
        
        if message_Received[0] == "HELLO":
            messageTosend = str()
            random_distance = random.randint(graph[node][from_node][0]+1,graph[node][from_node][1]-1) #check
            messageTosend = "HELLOREPLY" + " " + str(from_node) + " " + str(node) + " " + str(random_distance)
            UDPSocket[node].sendto(messageTosend.encode(),('127.0.0.1',10000+from_node))
        elif message_Received[0] == "HELLOREPLY":
            #if not change message[2] to node
            distance[node][int(message_Received[1])][int(message_Received[2])] = int(message_Received[3])
        elif message_Received[0] == "LSA":
            #check the seq_number is greater than the received_seq_number
            if int(message_Received[2]) >= seq_numbers[node][from_node]:
                seq_numbers[node][from_node] = int(message_Received[2])
                srcid = int(message_Received[1])
                start_index = 4
                for i in range(int(message_Received[3])):
                    distance[node][srcid][int(message_Received[start_index])] = int(message_Received[start_index+1])
                    start_index = start_index + 2
                for i in range(routers):
                    send_Message = message[0].decode()
                    if i != node and distance[node][node][i] != -1 and i != from_node:
                        UDPSocket[node].sendto(send_Message.encode(),('127.0.0.1',10000+i))

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
                    dist_path[j] = dist_path[min_node] + str(j) + "-"

    return min_distance,dist_path
    
def Routing_Table(node):
    global outputfileptr
    time_now = 0
    while True:
        time.sleep(SPF_INTERVAL)
        time_now = time_now + SPF_INTERVAL
        #for i in range(routers):
        #outputfileptr[i].write("Routing Table for Node No. "+str(i)+" at time "+str(time_now)+"\n")
        #outputfileptr[i].write("Destination\tPath\tCost\n")
        outputfileptr.write("Routing Table for Node No. "+str(node)+" at time "+str(time_now)+"\n")
        outputfileptr.write("Destination\t\tPath\t\t\t\tCost\n")
        #print(distance[node])
        min_distance,dist_path = find_min_path(node)
        #min_distance,dist_path = find_min_path(i)
        for j in range(len(min_distance)):
            if node != j :
                outputfileptr.write("\t\t\t\t" + str(j)+"\t\t\t\t" + dist_path[j][:-1] + "\t\t" + str(min_distance[j]) + "\n")

# if "-f" in sys.argv:
#     inputfilename = sys.argv[sys.argv.index("-f")+1]
# if "-h" in sys.argv:
#     HELLO_INTERVAL = int(sys.argv[sys.argv.index("-h")+1])
# if "-s" in sys.argv:
#     SPF_INTERVAL = int(sys.argv[sys.argv.index("-s")+1])
# if "-a" in sys.argv:
#     LSA_INTERVAL = int(sys.argv[sys.argv.index("-a")+1])
# if "-o" in sys.argv:
#     outputfilename = sys.argv[sys.argv.index("-o")+1]
# if "-i" in sys.argv:
#     want = int(sys.argv[sys.argv.index("-i")+1])
want = 2


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

#print(graph)

# outputfileptr = [0] * routers

# for i in range(routers):
#     outputfileptr[i] = open(outputfilename+"-"+str(i)+".txt","w")

# for i in range(routers):
#     outputfileptr[i].close()
# ptr.close()

threads = np.zeros((routers,3),dtype=object)

for i in range(routers):
    threads[i][0] = threading.Thread(target=send_HELLO,args=(i,))
    threads[i][0].start()
    threads[i][1] = threading.Thread(target=send_LSA,args=(i,))
    threads[i][1].start()
    threads[i][2] = threading.Thread(target=receive_Router,args=(i,))
    threads[i][2].start()
    print("vanakam")

threads_1 = threading.Thread(target=Routing_Table,args=(want,))
threads_1.start()


outputfileptr = open(outputfilename+"-"+str(want)+".txt","w")


time.sleep(42)
outputfileptr.close()
ptr.close()
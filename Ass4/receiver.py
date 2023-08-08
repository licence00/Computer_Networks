import socket
import random
import math
import time
import sys

debug = False

if "-d" in sys.argv:
    debug = True
if "-n" in sys.argv:
    MAX_PACKETS = int(sys.argv[sys.argv.index("-n") + 1])
if "-p" in sys.argv:
    PORT_NUMBER = int(sys.argv[sys.argv.index("-p") + 1])
if "-e" in sys.argv:
    RANDOM_DROP_PROB = float(sys.argv[sys.argv.index("-e") + 1])

buffersize = 1024
next_expected_packet = 0
error = False

def find_error_packet(random_index):
    random_value = MAX_PACKETS * RANDOM_DROP_PROB
    if random_value < 1:
        random_index.append(random.randint(1,MAX_PACKETS-1))
    else:
        random_value = math.ceil(random_value)
        for i in range(random_value):
            random_index.append(random.randint(1,MAX_PACKETS-1))

def get_seq_number(message):
    global PORT_NUMBER
    global error
    global debug
    global MAX_PACKETS
    global RANDOM_DROP_PROB
    seq_no = 0
    ten = 1
    check = message[0:8]
    for i in range(8):
        seq_no = seq_no + int(check[i])*ten
        ten = ten * 10
    return seq_no

program_start = time.time()

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind(('127.0.0.1', PORT_NUMBER))

random_index = list()
find_error_packet(random_index)

while True:
    message, address = UDPServerSocket.recvfrom(buffersize)
    time_diff = str((time.time() - program_start)*1000000).split(".")
    message = message.decode()
    if message == "kill":
        print("All packets received and acknowledgement send")
        break
    seq_number = get_seq_number(message)
    #print("Packet seq no :{} received and expected seq no : {}".format(seq_number,next_expected_packet))
    if seq_number in random_index:
        #remove that seq_number after using it once
        random_index.remove(seq_number)
        error = True

    if error == False:
        if seq_number == next_expected_packet:
            UDPServerSocket.sendto(str(seq_number).encode(),address)
            next_expected_packet = next_expected_packet + 1
            if debug == True:
                print("Seq {}: Time Received: {}:{} Packet dropped: {}".format(seq_number,time_diff[0][:-3],time_diff[0][-3:],error))
        else:
            UDPServerSocket.sendto(str(next_expected_packet-1).encode(),address)
    else:
        UDPServerSocket.sendto(str(next_expected_packet-1).encode(),address)
        error = False

UDPServerSocket.close()
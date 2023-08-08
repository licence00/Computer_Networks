import socket
import random
import math

PORT_NUMBER = 20001
MAX_PACKETS = 400
RANDOM_DROP_PROB = 0.0001

buffersize = 1024
next_expected_packet = 0
error = False

def find_error_packet(random_index):
    random_value = MAX_PACKETS * RANDOM_DROP_PROB
    if random_value < 1:
        random_index.append(random.randint(0,MAX_PACKETS))
    else:
        random_value = math.ceil(random_value)
        for i in range(random_value):
            random_index.append(random.randint(0,MAX_PACKETS))

def get_seq_number(message):
    seq_no = 0
    ten = 1
    check = message[0:8]
    for i in range(8):
        seq_no = seq_no + int(check[i])*ten
        ten = ten * 10
    return seq_no

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

UDPServerSocket.bind(('127.0.0.1', PORT_NUMBER))

random_index = list()

#find_error_packet(random_index)
random_index = [1]
print(random_index)

while True:
    if next_expected_packet == MAX_PACKETS:
        print("All packets received and acknowledgement send")
        break
    message, address = UDPServerSocket.recvfrom(buffersize)
    message = message.decode()
    seq_number = get_seq_number(message)
    print("Packet seq no :{} received".format(seq_number))
    if seq_number in random_index:
        error = True

    if error == False:
        print("expectd Packet seq no :{}".format(next_expected_packet))
        if seq_number == next_expected_packet:
            next_expected_packet += 1
            UDPServerSocket.sendto(str(seq_number).encode(),address)
            print("Packet seq no :{} received and acknowledgment sent".format(seq_number))
        else:
            UDPServerSocket.sendto(str(next_expected_packet-1).encode(),address)
            print("Acknowledgment sent is :{}".format(next_expected_packet-1))
    else:
        print("Packet with seq no: {} dropped as it contains error".format(seq_number))
        error = False
# NAME: Sai Siddarth
# Roll Number: CS20B059
# Course: CS3205 Jan. 2023 semester
# Lab number: 4
# Date of submission: 05-04-2023
# I confirm that the source file is entirely written by me without
# resorting to any dishonest means.
# Website(s) that I used for basic socket programming code are: <NILL>
# URL(s): <NILL>

import socket
import threading
import time
import sys

debug = False

if "-d" in sys.argv:
    debug = True
if "-l" in sys.argv:
    PACKET_LENGTH = int(sys.argv[sys.argv.index("-l") + 1])
if "-r" in sys.argv:
    PACKET_GEN_RATE = int(sys.argv[sys.argv.index("-r") + 1])
if "-b" in sys.argv:
    MAX_BUFFER_SIZE = int(sys.argv[sys.argv.index("-b") + 1])
if "-w" in sys.argv:
    WINDOW_SIZE = int(sys.argv[sys.argv.index("-w") + 1])
if "-n" in sys.argv:
    MAX_PACKETS = int(sys.argv[sys.argv.index("-n") + 1])
if "-s" in sys.argv:
    IP_ADDRESS = sys.argv[sys.argv.index("-s") + 1]
if "-p" in sys.argv:
    PORT_NUMBER = int(sys.argv[sys.argv.index("-p") + 1])

total_packets_transmitted = 0
acknowledged_packets = 0
round_trip_time = 0
expected_ack_number = 0
acks_list = []
counter = 0
check = False

packets = []
time_out = [0] * MAX_PACKETS #only contains seconds
lock = threading.Lock()
delaytime = 1 / PACKET_GEN_RATE

def modify_list():
    global packets 
    global total_packets_transmitted
    global delaytime
    global round_trip_time
    global acknowledged_packets
    global debug
    global program_start
    global acks_list
    global counter
    while total_packets_transmitted < MAX_PACKETS:
        lock.acquire()
        if len(packets) < MAX_BUFFER_SIZE:
            n = total_packets_transmitted
            data = str()
            for i in range(8):
                data = data + str(n % 10)
                n = n // 10
            for i in range(8, PACKET_LENGTH):
                data = data + 'a'
            packets.append(data)
            time_generated[total_packets_transmitted] = time.time()
            time_out[total_packets_transmitted] = 5*round_trip_time
            total_packets_transmitted = total_packets_transmitted + 1
            time.sleep(delaytime)
        lock.release()

def get_seq_number(message):
    global PACKET_GEN_RATE
    global MAX_PACKETS
    global MAX_BUFFER_SIZE
    global WINDOW_SIZE
    global PACKET_LENGTH
    global IP_ADDRESS
    global PORT_NUMBER
    seq_no = 0
    ten = 1
    check = message[0:8]
    for i in range(8):
        seq_no = seq_no + int(check[i])*ten
        ten = ten * 10
    return seq_no

def sendwindow():
    for i in range(min(WINDOW_SIZE, len(packets))):
        seq_number_to_send = get_seq_number(packets[i])
        if attempts[seq_number_to_send] > 6:
            print("Packet with seq: {} has been retransmitted more than 5 times".format(seq_number_to_send))
            sys.exit()
        time_stamps[seq_number_to_send] = time.time()
        attempts[seq_number_to_send] = attempts[seq_number_to_send] + 1
        UDPClientSocket.sendto(packets[i].encode(), serverAddressPort)

def sendnew(num):
    for i in range(num):
        lock.acquire()
        packets.pop(0)
        lock.release()
        if len(packets) < WINDOW_SIZE:
            packet_to_send = packets[len(packets)-1]
        else:
            packet_to_send = packets[WINDOW_SIZE-1]
        seq_number_to_send = get_seq_number(packet_to_send)
        if attempts[seq_number_to_send] > 6:
            print("Packet with seq: {} has been retransmitted more than 5 times".format(seq_number_to_send))
            sys.exit()
        attempts[seq_number_to_send] = attempts[seq_number_to_send] + 1
        time_stamps[seq_number_to_send] = time.time()
        UDPClientSocket.sendto(packet_to_send.encode(), serverAddressPort)

def receive_Ack():
    while True:
        message = UDPClientSocket.recvfrom(1024)
        if int(message[0].decode()) == MAX_PACKETS -1:
            break
        acks_list.append((int(message[0].decode()),time.time()))

program_start = time.time()
serverAddressPort   = (IP_ADDRESS, PORT_NUMBER)
bufferSize          = 4 #receving 4 bytes that is ACK

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.bind(('127.0.0.1',10002))
        
time_stamps = [0] * MAX_PACKETS #contains in time format
attempts = [0] * MAX_PACKETS
time_generated = [0] * MAX_PACKETS  

thread = threading.Thread(target=modify_list)
thread.start() #start the thread
time.sleep(1) #creating buffer

threadp = threading.Thread(target=receive_Ack)
threadp.start()

#first 10 packets has time_out as 100 ms
for i in range(10):
    time_out[i] = 0.1 #seconds

sendwindow()

while(True):
    if acknowledged_packets == MAX_PACKETS-1:
            UDPClientSocket.sendto("kill".encode(), serverAddressPort)
            print("All Packets Transmitted and Acknowledged")
            break
    if len(acks_list) > counter:
        message_tuple = acks_list[counter]
        ack_number_received = message_tuple[0]
        time_arrived = message_tuple[1]
        counter = counter + 1
        check = True
        
    if check == True:
        if time_arrived > time_out[expected_ack_number] + time_stamps[expected_ack_number]:
            sendwindow()
            continue
        if expected_ack_number == ack_number_received:
            time_taken = float(time_arrived - time_stamps[ack_number_received]) #seconds extracted
            if time_taken <= time_out[expected_ack_number]:
                expected_ack_number = expected_ack_number + 1
                round_trip_time =  ( round_trip_time*(acknowledged_packets) + time_taken ) / (acknowledged_packets + 1)
                acknowledged_packets = acknowledged_packets + 1
                sendnew(1)
                time_diff = str((time_generated[expected_ack_number] - program_start)*1000000).split('.')
                if debug == True:
                    print("Seq {}: Time Generated: {}:{} RTT: {} Number of Attempts: {}".format(expected_ack_number,time_diff[0][:-3],
                                                                time_diff[0][-3:],round_trip_time,attempts[expected_ack_number]))
        elif ack_number_received > expected_ack_number:
                time_taken_r = float(time_arrived - time_stamps[ack_number_received])
                diff = ack_number_received - expected_ack_number
                #check this once
                round_trip_time = ( round_trip_time*(acknowledged_packets) + (time_taken_r*diff) ) / (acknowledged_packets + diff)
                acknowledged_packets = acknowledged_packets + diff
                for i in range(diff):
                    expected_ack_number = expected_ack_number + 1
                    time_diff = str((time_generated[expected_ack_number] - program_start)*1000000).split('.')
                    if debug == True:
                        print("Seq {}: Time Generated: {}:{} RTT: {} Number of Attempts: {}".format(expected_ack_number,time_diff[0][:-3],
                                                        time_diff[0][-3:],round_trip_time,attempts[expected_ack_number]))
                sendnew(diff)
        check = False

thread.join() # Wait for the thread to finish
threadp.join()
UDPClientSocket.close()
print("Process Completed")
print("Packet Generation Rate : {} packets/sec".format(PACKET_GEN_RATE))
print("Packet Length : {} bytes".format(PACKET_LENGTH))
total_transmissions = sum(attempts) 
print("Retransmission Ratio : {}".format(total_transmissions/acknowledged_packets))
print("Round Trip Time: {} ms".format(round_trip_time*1000))
import socket
import threading
import time

PACKET_LENGTH = 512
PACKET_GEN_RATE = 10
MAX_BUFFER_SIZE = 10
WINDOW_SIZE = 3
MAX_PACKETS = 400
total_packets_transmitted = 0
acknowledged_packets = 0
round_trip_time = 0
expected_ack_number = 0
debug = True
check_flag = False

packets = []
lock = threading.Lock()
delaytime = 1 / PACKET_GEN_RATE

def modify_list():
    global packets 
    global total_packets_transmitted
    global delaytime
    while total_packets_transmitted < MAX_PACKETS:
        lock.acquire()
        if len(packets) < MAX_BUFFER_SIZE:
            #print(total_packets_transmitted)
            n = total_packets_transmitted
            data = str()
            for i in range(8):
                data = data + str(n % 10)
                n = n // 10
            for i in range(8, PACKET_LENGTH):
                data = data + 'a'
            packets.append(data)
            total_packets_transmitted = total_packets_transmitted + 1
            time.sleep(delaytime)
        lock.release()

# 123
# 3 12 32 1 321 0 32100000
# 10000000
# 1
# 1 0 10 0 10000000

#
# 00000001

def get_seq_number(message):
    seq_no = 0
    ten = 1
    check = message[0:8]
    for i in range(8):
        seq_no = seq_no + int(check[i])*ten
        ten = ten * 10
    return seq_no


serverAddressPort   = ("127.0.0.1", 20001)
bufferSize          = 4 #receving 4 bytes that is ACK

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

time_stamps = [0] * MAX_PACKETS #contains in time format
time_out = [0] * MAX_PACKETS #only contains microseconds
attempts = [0] * MAX_PACKETS

thread = threading.Thread(target=modify_list)
thread.start() #start the thread
time.sleep(1) #creating buffer

#first 10 packets has time_out as 100 ms
for i in range(10):
    time_out[i] = 100*(1000) #given in milliseconds

for i in range(WINDOW_SIZE):
    messageTosend = packets[i]
    seq_number = int(get_seq_number(messageTosend))
    #print(seq_number)
    bytesTosend = messageTosend.encode()
    time_stamps[seq_number] = time.time()
    #time_split = time_stamps[seq_number].split(".")
    attempts[seq_number] = attempts[seq_number] + 1
    UDPClientSocket.sendto(bytesTosend, serverAddressPort)
    print("Seq in for loop: {} sent".format(seq_number))
    # if debug == True:
    #     print("Seq: {} Time Generated: {}:{}  RTT: {}  Number of Attempts: {}"
    #                 .format(seq_number,time_split[1][:-3],time_split[1][3:],round_trip_time,attempts[seq_number]))

while(True):
    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    ack_number_received = int(msgFromServer[0].decode())
    print("ACK received : {}".format(ack_number_received))
    print("expected_ack_number : {}".format(expected_ack_number))
    time_taken = float(time.time() - time_stamps[ack_number_received])*1000000 #milliseconds extracted
    #print("time_taken : {}".format(time.time() - time_stamps[ack_number_received]))
    #print("time_out : {}".format(time_out[ack_number_received]))
    if expected_ack_number == ack_number_received:
        if time_taken < time_out[expected_ack_number]:
            expected_ack_number = expected_ack_number + 1
            lock.acquire()
            packets.pop(0)
            lock.release()
            #print(packets)
            acknowledged_packets = acknowledged_packets + 1
            round_trip_time =  ( round_trip_time*(acknowledged_packets-1) + time_taken ) / acknowledged_packets
            if acknowledged_packets == MAX_PACKETS:
                print("All packets transmitted and acknowledged")
                break
            seq_number_to_send = get_seq_number(packets[WINDOW_SIZE-1])
            if attempts[seq_number_to_send] > 5:
                print("Packet with seq: {} has transmitted more than 5 times".format(seq_number_to_send))
                print("Exiting")
                UDPClientSocket.close()
                break
            time_stamps[seq_number_to_send] = time.time()
            attempts[seq_number_to_send] = attempts[seq_number_to_send] + 1
            UDPClientSocket.sendto(packets[WINDOW_SIZE-1].encode(), serverAddressPort)
            print("Seq in equal condition: {} sent".format(seq_number_to_send))
        else:
            print("packet seq no: {} got dropped".fromat(ack_number_received))
    elif ack_number_received != expected_ack_number:
        if ack_number_received < expected_ack_number:
            print("gg")
            time_now = time.time()
            time_remaining = time_out[expected_ack_number] - float((time_now - time_stamps[expected_ack_number])*1000000)
            if time_remaining < 0:
                print("ACK Packet with seq: {} has been not received/dropped".format(expected_ack_number))
                for i in range(WINDOW_SIZE):
                    seq_number_to_send = get_seq_number(packets[i])
                    time_stamps[seq_number_to_send] = time.time()
                    attempts[seq_number_to_send] = attempts[seq_number_to_send] + 1
                    UDPClientSocket.sendto(packets[i].encode(), serverAddressPort)
                    print("Seq: {} sent".format(seq_number_to_send))
            elif time_remaining > 0:
                print("here")
                #do magic here
                while (time.time() - time_now)*1000000 < time_remaining:
                    msgFromServer2 = UDPClientSocket.recvfrom(bufferSize)
                    message_R = msgFromServer2[0].decode()
                    if message_R == expected_ack_number:
                        check_flag = True
                        break
                if check_flag == True:
                    continue #send new packet here

                else:
                    for i in range(WINDOW_SIZE):
                        seq_number_to_send = get_seq_number(packets[i])
                        time_stamps[seq_number_to_send] = time.time()
                        attempts[seq_number_to_send] = attempts[seq_number_to_send] + 1
                        UDPClientSocket.sendto(packets[i].encode(), serverAddressPort)
                        print("Seq: {} sent".format(seq_number_to_send))
                print("watiting for timeout for ACK:{}",expected_ack_number)
        elif ack_number_received > expected_ack_number:
            expected_ack_number = expected_ack_number + 1
            lock.acquire()
            packets.pop(0)
            lock.release()
            acknowledged_packets = acknowledged_packets + 1
            round_trip_time =  ( round_trip_time*(acknowledged_packets-1) + time_taken ) / acknowledged_packets
            if acknowledged_packets == MAX_PACKETS:
                print("All packets transmitted and acknowledged")
                break
            seq_number_to_send = get_seq_number(packets[WINDOW_SIZE-1])
            if attempts[seq_number_to_send] > 5:
                print("Packet with seq: {} has transmitted more than 5 times".format(seq_number_to_send))
                print("Exiting")
                UDPClientSocket.close()
                break
            time_stamps[seq_number_to_send] = time.time()
            attempts[seq_number_to_send] = attempts[seq_number_to_send] + 1
            UDPClientSocket.sendto(packets[WINDOW_SIZE-1].encode(), serverAddressPort)
            print("Seq in equal condition: {} sent".format(seq_number_to_send))

                    
thread.join() # Wait for the thread to finish
UDPClientSocket.close()
print("Process completed")
print("Round Trip Time: {} ms".format(round_trip_time))
#Wait completed
#msg = msgFromServer[0].decode()
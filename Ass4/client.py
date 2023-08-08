import socket
import threading
import time

serverAddressPort   = ("127.0.0.1", 20001)
bufferSize          = 4 #receving 4 bytes that is ACK

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

PACKET_LENGTH = 512
PACKET_GEN_RATE = 10
MAX_BUFFER_SIZE = 10
WINDOW_SIZE = 3
MAX_PACKETS = 100

total_packets_transmitted = 0
acknowledged_packets = 0
round_trip_time = 0
expected_ack_number = 0
debug = True

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
            time_out[total_packets_transmitted] = 5*round_trip_time
            total_packets_transmitted = total_packets_transmitted + 1
            time.sleep(delaytime)
        lock.release()

def get_seq_number(message):
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
        time_stamps[seq_number_to_send] = time.time()
        attempts[seq_number_to_send] = attempts[seq_number_to_send] + 1
        UDPClientSocket.sendto(packets[i].encode(), serverAddressPort)
        print("Seq: {} sent".format(seq_number_to_send))

def sendnew():
    
    lock.acquire()
    packets.pop(0)
    if len(packets) < WINDOW_SIZE:
        packet_to_send = packets[len(packets)-1]
    else:
        packet_to_send = packets[WINDOW_SIZE-1]
    seq_number_to_send = get_seq_number(packet_to_send)
    # if attempts[seq_number_to_send] > 5:
    #     print("Packet with seq: {} has transmitted more than 5 times".format(seq_number_to_send))
    #     return False
    attempts[seq_number_to_send] = attempts[seq_number_to_send] + 1
    time_stamps[seq_number_to_send] = time.time()
    UDPClientSocket.sendto(packet_to_send.encode(), serverAddressPort)
    print("Seq No success: {} sent".format(seq_number_to_send))
    lock.release()

time_stamps = [0] * MAX_PACKETS #contains in time format

attempts = [0] * MAX_PACKETS

#threadx,thready,threadz,threadw = 0,0,0,0
# global threadx
# global thready
# global threadz
# global threadw
thread = threading.Thread(target=modify_list)
thread.start() #start the thread
time.sleep(1) #creating buffer

#first 10 packets has time_out as 100 ms
for i in range(10):
    time_out[i] = 0.1 #seconds

for i in range(WINDOW_SIZE):
    messageTosend = packets[i]
    seq_number = int(get_seq_number(messageTosend))
    bytesTosend = messageTosend.encode()
    attempts[seq_number] = attempts[seq_number] + 1
    time_stamps[seq_number] = time.time()
    UDPClientSocket.sendto(bytesTosend, serverAddressPort)
    print("Seq in for loop: {} sent".format(seq_number))
    # if debug == True:
    #     print("Seq: {} Time Generated: {}:{}  RTT: {}  Number of Attempts: {}"
    #                 .format(seq_number,time_split[1][:-3],time_split[1][3:],round_trip_time,attempts[seq_number]))

#print("sai")

while(True):
    if acknowledged_packets == MAX_PACKETS-1:
            UDPClientSocket.sendto("kill".encode(), serverAddressPort)
            print("All packets transmitted and acknowledged")
            break
    message = UDPClientSocket.recvfrom(1024)
    ack_number_received = int(message[0].decode())
    print("ACK received : {} and expected ack number : {}".format(ack_number_received,expected_ack_number))
    if time.time() > time_out[expected_ack_number] + time_stamps[expected_ack_number]:
        print("packet seq no: {} got dropped due to time_out".format(expected_ack_number))
        # threadw = threading.Thread(target = sendwindow)
        # threadw.start()
        sendwindow()
        continue
    time_taken = float(time.time() - time_stamps[ack_number_received]) #seconds extracted
    print("time out: {} and time taken: {}".format(time_out[expected_ack_number],time_taken))
    if expected_ack_number == ack_number_received:
        if time_taken <= time_out[expected_ack_number]:
            expected_ack_number = expected_ack_number + 1
            acknowledged_packets = acknowledged_packets + 1
            round_trip_time =  ( round_trip_time*(acknowledged_packets-1) + time_taken ) / acknowledged_packets
            # threadx = threading.Thread(target = sendnew)
            # threadx.start()
            sendnew()
            print("round trip time" ,round_trip_time)
        else:
            print("packet seq no: {} got dropped due to time_out".format(ack_number_received))
            # thready = threading.Thread(target = sendwindow) 
            # thready.start()
            sendwindow()
    elif ack_number_received > expected_ack_number:
            time_taken_r = float(time.time() - time_stamps[ack_number_received])
            diff = ack_number_received - expected_ack_number
            #check this once
            round_trip_time = ( round_trip_time*(acknowledged_packets) + time_taken_r*diff ) / (acknowledged_packets + diff)
            acknowledged_packets = acknowledged_packets + diff
            expected_ack_number = expected_ack_number + diff
            for i in range(diff):
                print("error") 
                # threadz = threading.Thread(target = sendnew)
                # threadz.start()
                sendnew()
#print("sai")                    
thread.join() # Wait for the thread to finish
# threadx.join()

# threadz.join()
# threadw.join()
# thready.join()
UDPClientSocket.close()
print("Process completed")
print("Round Trip Time: {} ms".format(round_trip_time))
import random

def get_crc_error(gx,mx):
    index = 0
    for i in range(len(mx)):
        if mx[i] == 1:
            index = i
            break

    qx,rx = list(),str()
    operate = str(mx[index:index+len(gx)])
    index = index + len(gx)
    
    while index <= len(mx):
        rx = str()
        qx.append(1)
        for i in range(0,len(gx)) :
            bit = int(operate[i]) ^ int(gx[i])
            rx = rx + str(bit)
        rx = rx.lstrip('0')

        if rx == str():	
            count = 0
            while index + count < len(mx):
                if mx[index + count] == str(1):
                    break
                qx.append(0)
                count = count + 1
            if index + count == len(mx):
                rx = rx + str(mx[index:index+(len(mx)-index+1)])
                break
            index = index + count
        if index+len(gx)-len(rx) > len(mx):
            rx = rx + str(mx[index:index+(len(mx)-index+1)])
            qx = qx + [0 for i in range(len(mx)-index)]
            break
        else:
            operate = rx + str(mx[index:index+(len(gx)-len(rx))])
            index = index + (len(gx)-len(rx))
            qx.extend([0 for i in range(len(gx)-len(rx)-1)])
    return qx,rx

crc = str(100000111)
mx = '00110000101101101000000000110010011110110001111010111010000011111011111111001011101010000111101000011000011100100011000101100010'
quotient,remainder = get_crc_error(crc,mx)

    
if remainder == str():
    print("CRC Check: Error Not Detected\n\n")
else:
    print("CRC Check: Error Detected\n\n")

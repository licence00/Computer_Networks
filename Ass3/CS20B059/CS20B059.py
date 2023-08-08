import random

#Function to get the remainder when mx is divided by gx
def get_crc_error(gx,mx):
    index = 0
    for i in range(len(mx)):
        if mx[i] == 1:
            index = i
            break

    qx,rx = list(),str()
    operate = str(mx[index:index+len(gx)])
    index = index + len(gx)
    
    #Loop to get the remainder
    while index <= len(mx):
        rx = str()
        qx.append(1) #Append 1 to the quotient
        for i in range(0,len(gx)) :
            bit = int(operate[i]) ^ int(gx[i])
            rx = rx + str(bit)
        #Remove leading zeros by using lstrip
        rx = rx.lstrip('0')

        if rx == str():	#If the remainder is empty, append 0 to the quotient
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
        #If the index is greater than the length of mx, append the remaining bits to the remainder
        if index+len(gx)-len(rx) > len(mx):
            rx = rx + str(mx[index:index+(len(mx)-index+1)])
            qx = qx + [0 for i in range(len(mx)-index)]
            break
        #Else, append the remaining bits to the remainder
        else:
            operate = rx + str(mx[index:index+(len(gx)-len(rx))])
            index = index + (len(gx)-len(rx))
            qx.extend([0 for i in range(len(gx)-len(rx)-1)])
    return qx,rx

#The value of gx for CRC-8
crc = str(100000111)

#Enter the input file Name
filename = input("Enter the file name : ")
outputfilename1 = "CRC_computation.txt"
outputfilename2 = "Error_Detection.txt"
#Open the files with respective modes
file = open(filename, "r")
ofile1 = open(outputfilename1,"w")
ofile2 = open(outputfilename2,"w")	
print("File opened successfully")
print("Generating CRC ............. in CRC_computation.txt")
print("Error Detection ............. in Error_Detection.txt")	
line_count = 0
while True:
    #Read the line from the file
    line = file.readline()
    #Incrementing the Counter
    line_count = line_count + 1
    if line == "":
        break

    #1.1
    ofile1.write("Input #"+str(line_count)+"\n\n")
    writeline = "Input: " + line
    ofile1.write(writeline)
    #Remove the newline character
    line = line[0:128] 
    
    mx = str(line) + '0'*(len(crc)-1)
    quotient,remainder = get_crc_error(crc,mx)
    answer = str()
    for i in range(len(mx)):
        #If the index is greater than the length of mx - length of remainder, then xor the bits
        if i >= len(mx)-len(remainder):
            answer = answer + str(int(remainder[i-len(mx)+len(remainder)]) ^ int(mx[i]))
        else:
            answer = answer + str(mx[i])
    
    ofile1.write("CRC: " + answer+"\n\n")

    #1.2a
    ofile2.write("Input #"+str(line_count)+"\n\n")
    #Select 10 random numbers greater than or equal to 3
    error_introduce_range = range(3,135,2)
    error_introduce = random.sample(error_introduce_range,10)
    error_options = range(0,len(answer)-1)
    for j in range(len(error_introduce)):
        corrupted = answer
        #Select the random indices to introduce errors
        error_indices = random.sample(error_options,error_introduce[j])
        for i in range(len(error_indices)):
            #Flip the bits at the selected indices
            index = error_indices[i]
            if answer[index] == '0': #If the bit is 0, change it to 1
                corrupted = corrupted[0:index] + '1' + corrupted[index+1:]
            elif answer[index] == '1': #If the bit is 1, change it to 0
                corrupted = corrupted[0:index] + '0' + corrupted[index+1:]
        #Write the output to the file
        ofile2.write("Original String: " + line + "\n")
        ofile2.write("Original String with CRC: " + answer + "\n")
        ofile2.write("Corrupted String: " + corrupted + "\n")
        ofile2.write("Number of Errors Introduced: " + str(error_introduce[j]) + "\n")
        
        quotient_check,remainder_check = get_crc_error(crc,corrupted)
        
        if remainder_check == str(): #If the remainder is empty, then no error is detected
            ofile2.write("CRC Check: Error Not Detected\n\n")
        else: #Else, error is detected
            ofile2.write("CRC Check: Error Detected\n\n")
        
    #1.2b
    select_random_index = range(100,110) 
    select_random_array = random.sample(select_random_index,5) #Select 5 random indices
    for j in range(len(select_random_array)):
        new_corrupted = answer
        select_index = select_random_array[j]
        change_bit = str()
        #Change the bits at the selected indices
        for i in range(0,6):
            if new_corrupted[select_index+i] == '0': #If the bit is 0, change it to 1
                change_bit = change_bit + '1'
            elif new_corrupted[select_index+i] == '1': #If the bit is 1, change it to 0
                change_bit = change_bit + '0'
        new_corrupted = new_corrupted[0:select_index] + change_bit + new_corrupted[select_index+6:]
        #Write the output to the file
        ofile2.write("Original String: " + line + "\n")
        ofile2.write("Original String with CRC: " + answer + "\n")
        ofile2.write("Corrupted String: " + new_corrupted + "\n")
        ofile2.write("Number of Errors Introduced: " + str(6) + "\n")
        
        quotient_check,remainder_check = get_crc_error(crc,new_corrupted)

        if remainder_check == str(): #If the remainder is empty, then no error is detected
            ofile2.write("CRC Check: Error Not Detected\n\n")
        else: #Else, error is detected
            ofile2.write("CRC Check: Error Detected\n\n")

file.close()
ofile1.close()
ofile2.close()
print("CRC and Error Detection execute successfully")
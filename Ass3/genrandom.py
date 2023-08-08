import random

list1 = list()

f = open("input.txt","w")

for i in range(50):
    bitstring = str()
    for j in range(128):
        randoms = random.randint(1,10000)
        if randoms % 2 == 0:
            bitstring = bitstring + str(0)
        else:
            bitstring = bitstring + str(1)
    bitstring = bitstring + "\n"
    f.write(bitstring)   
f.close()
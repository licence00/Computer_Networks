import subprocess

port = 54322

for i in range(53,63):
    command = "sudo lsof -i:" + str(port+i)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    out = output.decode("utf-8")
    if len(out)>0:
        delete1 = str(out[63])+str(out[64])+str(out[65])
        print("process " + delete1)
        command = "kill " + str(delete1)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output1, error = process.communicate()
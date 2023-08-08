checkfilepath = currentpath+'/'+filename
    currentpath = os.getcwd()
    checkfilepath = currentpath+'/'+"sai.txt"
    bool_path = os.path.exists(checkfilepath)
    if bool_path == True :
        f = open(checkfilepath,"r")
        file_size = os.path.getsize(checkfilepath)
        wanted = file_size-int(nbytes)
        #print(wanted)
        for i in range(1,file_size+1):
            x = f.read(1)
            print(x) 
            print(i)
            #if i > wanted :
            #    print(x,end="")
        print("")
        f.close()  
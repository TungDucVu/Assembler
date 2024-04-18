import sys
 ##A = sys.stdin.readlines()
file_path = input("Enter the file path: ")  # Input the file path
A = []
B = []
with open(file_path, 'r') as file:
    a = file.readlines()
    #B.append(a.rstrip() for line in a)
    B.extend(line.rstrip() for line in a)
##B = [i.rstrip() for i in A]
dictreg={"R0":0,"R1":0,"R2":0,"R3":0,"R4":0,"R5":0,"R6":0,"V":0,"L":0,"G":0,"E":0}
opreg={"R0":"000","R1":"001","R2":"010","R3":"011","R4":"100","R5":"101","R6":"110","FLAGS":"111"}
variables=dict()
def regval(t):
    s=len(t)
    while(s<16):
        t="0"+t
        s=len(t)
    return t
def printfunc(i,over):
    pstr=""
    i=str(bin(i))[2:]
    s=len(i)
    while(s<8):
        i="0"+i
        s=len(i)
    pstr+=i+" " 
    k=0  
    f=0
    for i in dictreg.values():
        t=str(bin(i))[2:]
        if(k<7):
            t=regval(t)
            pstr+=t+" "
        else:
            if(over==1):
                pstr+="0000000000001000"
            elif(i==1):
                if(dictreg["E"]==1):
                    pstr+="0000000000000001"
                elif(dictreg["L"]==1):
                    pstr+="0000000000000100"
                elif(dictreg["G"]==1):
                    pstr+="0000000000000010"  
                f=1
        k+=1
    if(f==0):
        pstr+="0000000000000000"
    #pstr=pstr[:-1]
    print(pstr)
def convert(imm):
    imm=imm[::-1]
    val=0
    k=0
    for i in imm:
        if(i=='0'):
            pass
        else:
            val+=2**k
        k+=1
    return val
    #k=int(imm)
def typeA(str1):
    s1=str1[:5]
    x=str1[7:10]
    y=str1[10:13]
    z=str1[13:]
    for key, value in opreg.items():
        if x == value:
            x=key
        if y==value:
            y=key
        if z==value:
            z=key
    a=dictreg[x]
    b=dictreg[y]
    c=dictreg[z]
    check=2**16-1
    if(s1=='10000'):
        solve=b+c
        over=0
        if(solve>check):
            over=1
            dictreg["E"]=0
            dictreg["G"]=0
            dictreg["L"]=0
            dictreg["V"]=1
            b=str(bin(solve))[2:]
            b=b[::-1]
            b=b[:16]
            b=b[::-1]
            solve=convert(b)
        dictreg[x]=solve
        return over
    elif(s1=='10001'):
        solve=b-c
        if(solve<0):
            solve=0
        dictreg[x]=solve
    elif(s1=='10110'):
        solve=b*c
        over=0
        if(solve>check):
            over=1
            dictreg["E"]=0
            dictreg["G"]=0
            dictreg["L"]=0
            dictreg["V"]=1
            b=str(bin(solve))[2:]
            b=b[::-1]
            b=b[:16]
            b=b[::-1]
            solve=convert(b)
        dictreg[x]=solve
        return over
    elif(s1=='11010'):
        solve=b^c
        dictreg[x]=solve
    elif(s1=='11011'):
        solve=b|c
        dictreg[x]=solve
    elif(s1=='11100'):
        solve=b&c
        dictreg[x]=solve
def typeB(str1):
    s1=str1[:5]
    reg=str1[5:8]
    imm=str1[8:]
    val=convert(imm)
    for key, value in opreg.items():
        if reg==value:
            reg=key
    if(s1=='10010'):
        dictreg[reg]=val
    if(s1=='11001'):
        k=dictreg[reg]
        k=k<<val
        dictreg[reg]=k
    if(s1=='11000'):
        k=dictreg[reg]
        k=k>>val
        dictreg[reg]=k
def typeC(str1):
    s1=str1[:5]
    x=str1[10:13]
    y=str1[13:]
    for key, value in opreg.items():
        if x == value:
            x=key
        if y==value:
            y=key
    if(s1=='10011'):
        if(y=='111'):
            if(dictreg["V"]==1):
                dictreg[x]=1
            elif(dictreg["L"]==1):
                dictreg[x]=1
            if(dictreg["G"]==1):
                dictreg[x]=1
            if(dictreg["E"]==1):
                dictreg[x]=1
            else:
               dictreg[x]=0
        else: 
            val=dictreg[y]
            dictreg[x]=val
    if(s1=='10111'):
        x1=dictreg[x]
        y1=dictreg[y]
        x2=x1//y1
        y2=x1%y1
        dictreg[x]=x2
        dictreg[y]=y2
    if(s1=='11101'):
        k=dictreg[x]
        k=str(bin(k))[2:]
        str2=""
        for i in k:
            if(i=='1'):
                str2+="0"
            else:
                str2+="1"
        val=convert(str2)
        dictreg[y]=val
    if(s1=='11110'):
        a=dictreg[x]
        b=dictreg[y]
        if(a==b):
            dictreg["E"]=1
            dictreg["G"]=0
            dictreg["L"]=0
            dictreg["V"]=0
        elif(a<b):
            dictreg["L"]=1
            dictreg["G"]=0
            dictreg["E"]=0
            dictreg["V"]=0
        elif(a>b):
            dictreg["G"]=1
            dictreg["E"]=0
            dictreg["L"]=0
            dictreg["V"]=0
def typeD(str1):
    s1=str1[:5]
    reg=str1[5:8]
    for key, value in opreg.items():
        if reg == value:
            reg=key
    addr=str1[8:]
    val=dictreg[reg]
    if(s1=='10101'):
        

        variables[addr]=val
        
    if(s1=='10100'):
        if addr not in variables.keys():
            variables[addr] = 0
        
        memval=variables[addr]
        dictreg[reg]=memval
def typeE(str1,i):
    s1=str1[:5]
    addr=str1[8:]
    addr=convert(addr)
    #print(addr)
    if(s1=='11111'):
        return addr+1
    if(s1=='01100'):
        l=dictreg["L"]
        if(l==1):
            return addr+1
    if(s1=='01101'):
        g=dictreg["G"]
        if(g==1):
            #print(addr)
            return addr+1
    if(s1=='01111'):
        e=dictreg["E"]
        if(e==1):
            return addr+1
    return i+2
i=0
E = ['01100','01101','01111']
while(i<len(B)-1):
    over=0
    t=i
    #print(i)
    #print(dictreg)
    str1=B[i]
    s1=str1[:5]
    if s1 not in E:
        dictreg["E"]=0
        dictreg["G"]=0
        dictreg["L"]=0
        dictreg["V"]=0
    if(s1=='10000' or s1=='10001' or s1=='10110' or s1=='11010' or s1=='11011' or s1=='11100'):
        over=typeA(str1)
    if(s1=='10010' or s1=='11001' or s1=='11000'):
        typeB(str1)
    if(s1=='10011' or s1=='10111' or s1=='11101' or s1=='11110'):
        typeC(str1)
    if(s1=='10101' or s1=='10100'):
        typeD(str1)    
    if(s1=='11111' or s1=='01100' or s1=="01101" or s1=='01111'):
        t=typeE(str1,i)-2
        #print(t)
    if s1 in E:
        dictreg["E"]=0
        dictreg["G"]=0
        dictreg["L"]=0
        dictreg["V"]=0
    printfunc(i,over)
    i=t
    #print(dictreg)
    #print(variables)
    i+=1
over=0
printfunc(i,over)
#print(variables)
final=dict()
for key,value in variables.items():
    val=bin(value)[2:]
    s=len(val)
    while(s<16):
        val="0"+val
        s=len(val)
    k=int(key)
    final[k]=val
#print(final)
list=final.keys()
list=sorted(list)
#print(list)
j=256-len(B)-len(list)
for i in B:
    print(i)
for i in list:
    print(final[i])
str2="0000000000000000"
for i in range(j):
    print(str2)


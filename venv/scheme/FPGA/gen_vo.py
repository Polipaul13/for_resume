import re

def unique(lst):
    seen = set()
    result = []
    for x in lst:
        if x in seen:
            continue
        if x == 'gnd':
            continue
        if re.match(r'\S+combout', x):
            continue
        seen.add(x)
        result.append(x)
    return result


def get_mems(hx, x):
    hx = int(hx,16)
    bind = bin(hx)[2:]
    while len(bind) < 16:
        bind = '0'+bind
    i = 0
    result = ''
    while i < len(bind):
        if (bind[i] == '1'):
            result = result + 'VCC ' + 'lutmem' + str(x) + '_'+str(i)+'\n'
        else:
            result = result + 'GND ' + 'lutmem' + str(x) + '_'+str(i)+'\n'
        i+=1
    return result


def get_lut(A, B, C, D, out, x):
    result = ''
    i = 0
    j = 0
    while i < 8:
        result = result+'AND '+str(A)+' lutmem'+str(x)+'_'+str(j)+' andD'+str(x)+str(i)+'\n'
        result = result+'INV '+str(A)+' no'+str(x)+str(i)+'\n'
        j += 1
        result = result+'AND no'+str(x)+str(i)+' lutmem'+str(x)+'_'+str(j)+' andC'+str(x)+str(i)+'\n'
        result = result+'OR andC'+str(x)+str(i)+' andD'+str(x)+str(i)+' L1'+str(x)+'_'+str(i)+'\n'
        i += 1
        j += 1
    i = 0
    j = 0
    while i < 4:
        result = result+'AND '+str(B)+' L1'+str(x)+'_'+str(j)+' andD'+str(x)+'A'+str(i)+'\n'
        result = result+'INV '+str(B)+' no'+str(x)+'A'+str(i)+'\n'
        j += 1
        result = result+'AND no'+str(x)+'A'+str(i)+' L1'+str(x)+'_'+str(j)+' andC'+str(x)+'A'+str(i)+'\n'
        result = result+'OR andC'+str(x)+'A'+str(i)+' andD'+str(x)+'A'+str(i)+' L2'+str(x)+'_'+str(i)+'\n'
        i += 1
        j += 1
    i = 0
    j = 0
    while i < 2:
        result = result+'AND '+str(C)+' L2'+str(x)+'_'+str(j)+' andD'+str(x)+'B'+str(i)+'\n'
        result = result+'INV '+str(C)+' no'+str(x)+'B'+str(i)+'\n'
        j += 1
        result = result+'AND no'+str(x)+'B'+str(i)+' L2'+str(x)+'_'+str(j)+' andC'+str(x)+'B'+str(i)+'\n'
        result = result+'OR andC'+str(x)+'B'+str(i)+' andD'+str(x)+'B'+str(i)+' L3'+str(x)+'_'+str(i)+'\n'
        i += 1
        j += 1
    i = 0
    j = 0
    result = result+'AND '+str(D)+' L3'+str(x)+'_'+str(j)+' andD'+str(x)+'C'+str(i)+'\n'
    result = result+'INV '+str(D)+' no'+str(x)+'C'+str(i)+'\n'
    j += 1
    result = result+'AND no'+str(x)+'C'+str(i)+' L3'+str(x)+'_'+str(j)+' andC'+str(x)+'C'+str(i)+'\n'
    result = result+'OR andC'+str(x)+'C'+str(i)+' andD'+str(x)+'C'+str(i)+' '+str(out)+'\n'
    return result

text = open("file1.vo")
result = ''
inputs = ''
cnt = 0

A = []
B = []
C = []
D = []
outfpga = []
infpga = []
CIN = []
COUT = []
COUT_EN = []
out = []
inv = []
HX = []
cnt = 0
cnt_in = 0
cnt_out = 0
for line in text.readlines():

    if(re.match(r'\W+.dataa\(\\\S+_combout+\W\)', line)):
        data = re.findall(r'\W+.dataa\(\\(\S+_combout+\W)\)', line) #comboutA
        A.append(data[0])
    elif (re.match(r'\W+.dataa\(\\(\S+combout+\W)\)', line)):  #comboutA
        data = re.findall(r'.dataa\(\\\S+combout+\W\)', line)
        A.append(data[0])
    elif (re.match(r'\W+.dataa\((gnd)\)', line)): #GND
                data = re.findall(r'\W+.dataa\((gnd)\)', line)
                A.append(data[0])
                GND_EN = 1
    elif (re.match(r'\W+.dataa\(\\+(\S+)~input_o+\s\)', line)):  # A
                    data = re.findall(r'\W+.dataa\(\\+(\S+)~input_o+\s\)', line)
                    A.append(data[0])
    elif (re.match(r'\W+.datab\(\\(\S+_combout+\W)\)', line)):
                        data = re.findall(r'\W+.datab\(\\+(\S+_combout+\W)\)', line)  # comboutB
                        B.append(data[0])
    elif (re.match(r'\W+.datab\(\\+(\S+combout+\W)\)', line)):  # comboutB
                            data = re.findall(r'\W+.datab\(\\+(\S+combout+\W)\)', line)
                            B.append(data[0])
    elif (re.match(r'\W+.datab\((gnd)\)', line)):  # GND
                                data = re.findall(r'\W+.datab\((gnd)\)', line)
                                B.append(data[0])
                                GND_EN = 1
    elif (re.match(r'\W+.datab\(\\+(\S+)~input_o+\s\)', line)):  # B
                                    data = re.findall(r'\W+.datab\(\\+(\S+)~input_o+\s\)', line)
                                    B.append(data[0])
    elif (re.match(r'\W+.datac\(\\\S+_combout+\W\)', line)):
                                        data = re.findall(r'\W+.datac\(\\+(\S+_combout+\W)\)', line)  # comboutC
                                        C.append(data[0])
    elif re.match(r'\W+.datac\(\\\S+combout+\W\)', line):  # comboutC
                                            data = re.findall(r'\W+.datac\(\\+(\S+combout+\W)\)', line)
                                            C.append(data[0])
    elif re.match(r'\W+.datac\((gnd)\)', line):  # GND
                                                data = re.findall(r'\W+.datac\((gnd)\)', line)
                                                C.append(data[0])
                                                GND_EN = 1
    elif re.match(r'\W+.datac\(\\+(\S+)~input_o+\s\)', line):  # C
                                                    data = re.findall(r'\W+.datac\(\\+(\S+)~input_o+\s\)', line)
                                                    C.append(data[0])
    elif re.match(r'\W+.datad\(\\\S+_combout+\W\)', line):
        data = re.findall(r'\W+.datad\(\\+(\S+_combout+\W)\)',line)  # comboutD
        D.append(data[0])
    elif re.match(r'\W+.datad\(\\\S+combout+\W\)', line):  # comboutD
        data = re.findall(r'\W+.datad\(\\+(\S+combout+\W)\)', line)
        D.append(data[0])
    elif re.match(r'\W+.datad\((gnd)\)', line):  # GND
                           data = re.findall(r'\W+.datad\((gnd)\)', line)
                           D.append(data[0])
                           GND_EN = 1
    elif re.match(r'\W+.datad\((vcc)\)', line):  # VCC
                               data = re.findall(r'\W+.datad\((vcc)\)', line)
                               D.append(data[0])
                               VCC_EN = 1
    elif re.match(r'\W+.datad\(\\+(\S+)~input_o+\s\)',line):  # D
                                    data = re.findall(r'\W+.datad\(\\+(\S+)~input_o+\s\)', line)
                                    D.append(data[0])
    elif re.match(r'\W+.i\(\!+\\+\S+_combout+\s\)',line): #out_fpga
                      data = re.findall(r'\W+.i\(\!+\\+\S+_combout+\s\)',line)
                      outfpga.append(data[0])
                      inv.append('!')
                      cnt_out += 1
    elif re.match (r'\W+.i\(\\\S+combout+\s\)',line):  # out_fpga
                          data = re.findall(r'\W+.i\(\\+(\S+combout+\s)\)',line)
                          outfpga.append(data[0])
                          inv.append('!')
                          cnt_out += 1
    elif re.match(r'\W+.i\(\\\S+_combout+\s\)',line):  # out_fpga
                              data = re.findall(r'\W+.i\(\\+(\S+_combout+\s)\)',line)
                              outfpga.append(data[0])
                              cnt_out += 1
    elif re.match(r'\W+.i\(\S+\),',line):  #in_fpga
                             data = re.findall(r'\((\S+)\),',line)
                             infpga.append(data[0])
                             cnt_in += 1
    ###############################CIN
    elif re.match(r'\W+.cin\(\\+(\S+\S)+\W\),', line): #cout
        data = re.findall(r'\W+.cin\(\\\\+(\S+\S)+\W\),', line)
        CIN.append(data[0])
        CIN_EN = 1
    #############################
    elif re.match(r'\W+.combout\(\S+_combout+\s\)', line): #out
        data = re.findall(r'\W+.combout\(\\+(\S+_combout+\s)\)', line)
        out.append(data[0])
    elif re.match(r'\W+.combout\(\\+\S+combout+\s\)', line): #out
        data = re.findall(r'\W+.combout\(\\+(\S+combout+\s)\)', line)
        out.append(data[0])
    ###############################COUT
    elif re.match(r'\W+.combout\(\\+\S+combout+\s\)', line): #cout
        data = re.findall(r'\W+.combout\(\\+\S+combout+\s\)', line)
        COUT.append(data[0])
        COUT_EN.append(1)
        COUT_EN_all = 1
    elif re.match(r'\S+\W+\S+\W+.lut_mask+\W+=+\W+16\'h(\S+\S+\S+\S)+;',line): #16h
        data = re.findall(r'\S+\W+\S+\W+.lut_mask+\W+=+\W+16\'h(\S+\S+\S+\S)+;',line)
        HX.append(data[0])
        cnt += 1
    elif re.match(r'\S+\W+\S+.lut_mask+\W+=+\W+16\'h(\S+\S+\S+\S)+;', line):  # 16h
        data = re.findall(r'\S+\W+\S+.lut_mask+\W+=+\W+16\'h(\S+\S+\S+\S)+;', line)
        HX.append(data[0])
        cnt += 1




#print(A)
#print(B)
#print(C)
#print(D)
#print(outfpga)
#print(infpga)
#print(CIN)
#print(COUT)
#print(COUT_EN)
#print(out)
#print(inv)
#print(HX)
#print(cnt)

result = str(len(infpga))
for x in infpga:
    result += ' ' + str(x)
result += '\n'+str(len(outfpga))
for x in outfpga:
    result += ' ' + str(x)
result += '\n'
cnt_mem = 0
for x in HX:
    result += get_mems(x, cnt_mem)
    cnt_mem += 1
i = 0
while i<cnt:
    result += get_lut(A[i],B[i],C[i],D[i],out[i], i)
    i+=1


print('\n'+result)
f = open('sch1.seu','w')
f.write(result)
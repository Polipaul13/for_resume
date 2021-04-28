__author__ = 'Vladimir Rukhlov, Alexandr Stashevskiy'


#////////////////////////////////////////////////////////////////
#/ Read yosys file 4-IN LUT FPGA, and write to Scheme_alt class /
#////////////////////////////////////////////////////////////////
import scheme
import re
#//////////////////////////////////////////////////
#//Генератор значений входов и выходов всей схемы//
#//////////////////////////////////////////////////
def IO(inps, outps):
    i = 0
    j = 0
    ins = list(set(inps))
    outs = list(set(outps))
    while i < len(ins):
        j = 0
        while j < len(outs):
            if ins[i] == 'GND' or ins[i] == 'VCC':
                    del ins[i]
                    i -= 1
            if ins[i] == outs[j]:
                del ins[i]
                i = i-1
                del outs[j]
                j = j - 1
                if i > len(ins) or j > len(outs):
                    break
            else:
                j += 1
        else:
            i += 1
    ins_str = ''
    outs_str = ''
    cnt = 0
    i = 0
    while i < len(ins):
        ins_str = ins_str + str(ins[i])+" "
        cnt += 1
        i += 1
    ins_str = str(cnt) +" "+ins_str+"\n"

    cnt = 0
    i = 0
    while i < len(outs):
        outs_str = outs_str + str(outs[i])+" "
        cnt += 1
        i +=1
    outs_str = str(cnt)+" "+outs_str+" \n"
    result = ins_str + outs_str
    return result # N INS; N OUTS
#//////////////////////////////////////////////////
#//      Разбираем данные из строки в массив     //
#//////////////////////////////////////////////////
def Read_STR(stringtoread):
    #regex = r"(\w+)"
    regex = r"[a-zA-Z0-9_\[\]]+"
    result = re.findall(regex, stringtoread)
    return result # STR -> OBJ
#//////////////////////////////////////////////////
#//         Получим .seu структуру памяти        //
#//////////////////////////////////////////////////
def Get_mems_MUX_method(data, x):
    data = int(data,16)
    bind = bin(data)[2:]
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
    return result #ALL VCC/GND lutmemx_x
#//////////////////////////////////////////////////

#//////////////////////////////////////////////////
#//          Получим .seu структуру LUT          //
#//////////////////////////////////////////////////
def Get_lut_MUX_method(A, B, C, D, out, x):
    result = ''
    i = 0
    j = 0
    while i < 8:
        result = result + 'MUX lutmem' + str(x) + '_' + str(j) + ' lutmem' + str(x) + '_' + str(j + 1) + ' ' + str(A) + ' L1' + str(x) + '_' + str(i) + '\n'
        i += 1
        j += 2
    i = 0
    j = 0
    while i < 4:
        result = result + 'MUX L1' + str(x) + '_' + str(j) + ' L1' + str(x) + '_' + str(j + 1) + ' ' + str(B) + ' L2' + str(x) + '_' + str(i) + '\n'
        i += 1
        j += 2
    i = 0
    j = 0
    while i < 2:
        result = result + 'MUX  L2' + str(x) + '_' + str(j) + ' L2' + str(x) + '_' + str(j + 1) + ' ' + str(C) + ' L3' + str(x) + '_' + str(i) + '\n'
        i += 1
        j += 2
    i = 0
    j = 0
    result = result + 'MUX L3' + str(x) + '_' + str(j) + ' L3' + str(x) + '_' + str(j + 1) + ' ' + str(D) + ' ' + str(out) + '\n'
    j += 1
    return result #ALL Elements
### DEL - Old version of Get-lut
'''
def Get_lut_2ins_elements(A, B, C, D, out, x):
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
    return result #ALL Elements
'''
#//////////////////////////////////////////////////
#/////формируем структуру ячейки LUT3 из MUXs//////
#//////////////////////////////////////////////////
def Get_mems_MUX_method_LUT3(data, x):
    data = int(data,16)
    bind = bin(data)[2:]
    while len(bind) < 8:
        bind = '0'+bind
    i = 0
    result = ''
    while i < len(bind):
        if (bind[i] == '1'):
            result = result + 'VCC ' + 'lutmem' + str(x) + '_'+str(i)+'\n'
        else:
            result = result + 'GND ' + 'lutmem' + str(x) + '_'+str(i)+'\n'
        i+=1
    return result #ALL VCC/GND lutmemx_x

def Get_lut_MUX_method_LUT3(A, B, C, out, x):
    result = ''
    i = 0
    j = 0
    while i < 4:
        result = result + 'MUX lutmem' + str(x) + '_' + str(j) + ' lutmem' + str(x) + '_' + str(j + 1) + ' ' + str(A) + ' L2' + str(x) + '_' + str(i) + '\n'
        i += 1
        j += 2
    i = 0
    j = 0
    while i < 2:
        result = result + 'MUX  L2' + str(x) + '_' + str(j) + ' L2' + str(x) + '_' + str(j + 1) + ' ' + str(B) + ' L3' + str(x) + '_' + str(i) + '\n'
        i += 1
        j += 2
    i = 0
    j = 0
    result = result + 'MUX L3' + str(x) + '_' + str(j) + ' L3' + str(x) + '_' + str(j + 1) + ' ' + str(C) + ' ' + str(out) + '\n'
    j += 1
    return result #ALL Elements
#//////////////////////////////////////////////////
#/формируем структуру scheme_alt LUT3 из строк/////
#//////////////////////////////////////////////////
def lut2schemealt_MUX_method_LUT3(strngs, IOs_ex=0):
    result = ''
    luts = ''
    cnt = 0
    num_elem_lut = 15
    inputs = []
    outputs = []
    MEMs_data = []
    for strng in strngs:
        datas = Read_STR(strng)
        if (len(datas)==5):
             i = 0
             while i < 3:
                 inputs.append(datas[i])
                 i += 1
             outputs.append(datas[4])
             MEMs_data.append(datas[3])
             lut = Get_lut_MUX_method_LUT3(datas[0],datas[1],datas[2],datas[4],cnt)
             luts = luts+lut
             cnt += 1
        if (len(datas)==4):
             i = 0
             while i < 2:
                 inputs.append(datas[i])
                 i += 1
             inputs.append('VCC')
             outputs.append(datas[3])
             MEMs_data.append(datas[2])
             lut = Get_lut_MUX_method_LUT3(datas[0],datas[1],'VCC',datas[3],cnt)
             luts = luts+lut
             cnt += 1
        if (len(datas)==3):
             inputs.append(datas[0])
             inputs.append('VCC')
             inputs.append('VCC')
             outputs.append(datas[2])
             MEMs_data.append(datas[1])
             lut = Get_lut_MUX_method_LUT3(datas[0],'VCC','VCC',datas[1],cnt)
             luts = luts+lut
             cnt += 1
    cnt_el = cnt*num_elem_lut + 2
    IOs = IO(inputs, outputs)
    if (IOs_ex == 0):
        result = result + IOs
        result = result + str(cnt_el) + '\nGND GND\nVCC VCC\n'
    else:
        test = str(IOs_ex[2]).split("\n")
        result = result + str(IOs_ex[0]) + "\n" + str(IOs_ex[1]) +"\n"
        result = result + str(cnt_el + (len(test)-1))+'\nGND GND\nVCC VCC\n' + IOs_ex[2]
    cnt_mem = 0
    MEM = ''
    for MEM_data in MEMs_data:
        MEM = MEM + Get_mems_MUX_method_LUT3(MEM_data, cnt_mem)
        cnt_mem += 1
    result = result + MEM
    result = result + luts
    #print(result)
    schm = scheme.scheme_alt()
    scheme_alt = result.split('\n')
    lines = scheme_alt
    schm.__inputs__ = lines[0].split()[1:]
    schm.__outputs__ = lines[1].split()[1:]
    elements = lines[3:-1]
    for element in elements:
        operation, *operands, result = element.split()
        schm.__elements__[result] = (operation, list(operands))
    return schm
#//////////////////////////////////////////////////
#/////формируем структуру scheme_alt из строк//////
#//////////////////////////////////////////////////
def lut2schemealt_MUX_method(strngs, IOs_ex=0):
    result = ''
    luts = ''
    cnt = 0
    num_elem_lut = 31
    inputs = []
    outputs = []
    MEMs_data = []
    for strng in strngs:
        datas = Read_STR(strng)
        if (len(datas)==6):
             i = 0
             while i < 4:
                 inputs.append(datas[i])
                 i += 1
             outputs.append(datas[5])
             MEMs_data.append(datas[4])
             lut = Get_lut_MUX_method(datas[0],datas[1],datas[2],datas[3],datas[5],cnt)
             luts = luts+lut
             cnt += 1
        if (len(datas)==5):
             i = 0
             while i < 3:
                 inputs.append(datas[i])
                 i += 1
             inputs.append('VCC')
             outputs.append(datas[4])
             MEMs_data.append(datas[3])
             lut = Get_lut_MUX_method(datas[0],datas[1],datas[2],'VCC',datas[4],cnt)
             luts = luts+lut
             cnt += 1
        if (len(datas)==4):
             i = 0
             while i < 2:
                 inputs.append(datas[i])
                 i += 1
             inputs.append('VCC')
             inputs.append('VCC')
             outputs.append(datas[3])
             MEMs_data.append(datas[2])
             lut = Get_lut_MUX_method(datas[0],datas[1],'VCC','VCC',datas[3],cnt)
             luts = luts+lut
             cnt += 1
        if (len(datas)==3):
             inputs.append(datas[0])
             inputs.append('VCC')
             inputs.append('VCC')
             inputs.append('VCC')
             outputs.append(datas[2])
             MEMs_data.append(datas[1])
             lut = Get_lut_MUX_method(datas[0],'VCC','VCC','VCC',datas[2],cnt)
             luts = luts+lut
             cnt += 1
    cnt_el = cnt*num_elem_lut
    IOs = IO(inputs, outputs)
    if (IOs_ex == 0):
        result = result + IOs
        result = result + str(cnt_el) + '\nGND GND\nVCC VCC\n'
    else:
        test = str(IOs_ex[2]).split("\n")
        result = result + str(IOs_ex[0]) + "\n" + str(IOs_ex[1]) +"\n"
        result = result + str(cnt_el + (len(test)-1))+'\nGND GND\nVCC VCC\n' + IOs_ex[2]
    cnt_mem = 0
    MEM = ''
    for MEM_data in MEMs_data:
        MEM = MEM + Get_mems_MUX_method(MEM_data, cnt_mem)
        cnt_mem += 1
    result = result + MEM
    result = result + luts
    #print(result)
    schm = scheme.scheme_alt()
    scheme_alt = result.split('\n')
    lines = scheme_alt
    schm.__inputs__ = lines[0].split()[1:]
    schm.__outputs__ = lines[1].split()[1:]
    elements = lines[3:-1]
    for element in elements:
        operation, *operands, result = element.split()
        schm.__elements__[result] = (operation, list(operands))
    return schm

#//////////////////////////////////////////////////
#//  Получим конфигурационные данные для LUT4    //
#//////////////////////////////////////////////////
def Get_mems_LUT_method(data):
    data = int(data,16)
    bind = bin(data)[2:]
    while len(bind) < 16:
        bind = '0'+bind
    result = ' '.join(str(bind))
    return result #ALL VCC/GND lutmemx_x
#//////////////////////////////////////////////////

#//////////////////////////////////////////////////
#//          Получим .seu структуру LUT          //
#//////////////////////////////////////////////////
def Get_lut_LUT_method(A, B, C, D, mem, out):
    result = ''
    memx = Get_mems_LUT_method(mem)
    result = result + 'LUT ' + A + ' ' + B + ' ' + C + ' ' + D + ' ' + memx + ' ' +out + '\n'
    return result #ALL Elements
#//////////////////////////////////////////////////
#/////формируем структуру scheme_alt из строк//////
#//////////////////////////////////////////////////
def lut2schemealt_LUT_method(strngs, IOs_ex=0):
    result = ''
    luts = ''
    cnt = 0
    num_elem_lut = 60
    inputs = []
    outputs = []
    MEMs_data = []
    for strng in strngs:
        datas = Read_STR(strng)
        if (len(datas)==6):
             i = 0
             while i < 4:
                 inputs.append(datas[i])
                 i += 1
             outputs.append(datas[5])
             MEMs_data.append(datas[4])
             lut = Get_lut_LUT_method(datas[0],datas[1],datas[2],datas[3],datas[4],datas[5])
             luts = luts+lut
             cnt += 1
        if (len(datas)==5):
             i = 0
             while i < 3:
                 inputs.append(datas[i])
                 i += 1
             inputs.append('VCC')
             outputs.append(datas[4])
             MEMs_data.append(datas[3])
             lut = Get_lut_LUT_method(datas[0],datas[1],datas[2],'VCC',datas[3],datas[4])
             luts = luts+lut
             cnt += 1
        if (len(datas)==4):
             i = 0
             while i < 2:
                 inputs.append(datas[i])
                 i += 1
             inputs.append('VCC')
             inputs.append('VCC')
             outputs.append(datas[3])
             MEMs_data.append(datas[2])
             lut = Get_lut_LUT_method(datas[0],datas[1],'VCC','VCC',datas[2],datas[3])
             luts = luts+lut
             cnt += 1
        if (len(datas)==3):
             inputs.append(datas[0])
             inputs.append('VCC')
             inputs.append('VCC')
             inputs.append('VCC')
             outputs.append(datas[2])
             MEMs_data.append(datas[1])
             lut = Get_lut_LUT_method(datas[0],'VCC','VCC','VCC',datas[1],datas[2])
             luts = luts+lut
             cnt += 1
    IOs = IO(inputs, outputs)
    if (IOs_ex == 0):
        result = result + IOs
        result = result + str(cnt + 4) + '\nGND GND\nVCC VCC\nGND 0\nVCC 1\n'
    else:
        test = str(IOs_ex[2]).split("\n")
        result = result + str(IOs_ex[0]) + "\n" + str(IOs_ex[1]) + "\n"
        result = result + str(cnt + 4 + (len(test)-1))+'\nGND GND\nVCC VCC\nGND 0\nVCC 1\n' + IOs_ex[2]
    result = result + luts
    #print(result)
    schm = scheme.scheme_alt()
    scheme_alt = result.split('\n')
    lines = scheme_alt
    schm.__inputs__ = lines[0].split()[1:]
    schm.__outputs__ = lines[1].split()[1:]
    elements = lines[3:-1]
    for element in elements:
        operation, *operands, result = element.split()
        schm.__elements__[result] = (operation, list(operands))
    return schm

#//////////////////////////////////////////////////
#//  Получим конфигурационные данные для LUT3    //
#//////////////////////////////////////////////////
def Get_mems_LUT3_method(data):
    data = int(data,16)
    bind = bin(data)[2:]
    while len(bind) < 8:
        bind = '0' + bind
    result = ' '.join(str(bind))
    return result #ALL VCC/GND lutmemx_x
#//////////////////////////////////////////////////

#//////////////////////////////////////////////////
#//          Получим .seu структуру LUT3         //
#//////////////////////////////////////////////////
def Get_lut_LUT3_method(A, B, C, mem, out):
    result = ''
    memx = Get_mems_LUT3_method(mem)
    result = result + 'LUT3 ' + A + ' ' + B + ' ' + C + ' ' + memx + ' ' +out + '\n'
    return result #ALL Elements
#//////////////////////////////////////////////////
#/////формируем структуру scheme_alt из строк//////
#//////////////////////////////////////////////////
def lut2schemealt_LUT3_method(strngs, IOs_ex=0):
    result = ''
    luts = ''
    cnt = 0
    num_elem_lut = 28
    inputs = []
    outputs = []
    MEMs_data = []
    for strng in strngs:
        datas = Read_STR(strng)
        if (len(datas)==5):
             i = 0
             while i < 3:
                 inputs.append(datas[i])
                 i += 1
             outputs.append(datas[4])
             MEMs_data.append(datas[3])
             lut = Get_lut_LUT3_method(datas[0],datas[1],datas[2],datas[3],datas[4])
             luts = luts+lut
             cnt += 1
        if (len(datas)==4):
             i = 0
             while i < 2:
                 inputs.append(datas[i])
                 i += 1
             inputs.append('VCC')
             outputs.append(datas[3])
             MEMs_data.append(datas[2])
             lut = Get_lut_LUT3_method(datas[0],datas[1],'VCC',datas[2],datas[3])
             luts = luts+lut
             cnt += 1
        if (len(datas)==3):
             inputs.append(datas[0])
             inputs.append('VCC')
             inputs.append('VCC')
             outputs.append(datas[2])
             MEMs_data.append(datas[1])
             lut = Get_lut_LUT3_method(datas[0],'VCC','VCC',datas[1],datas[2])
             luts = luts+lut
             cnt += 1
    IOs = IO(inputs, outputs)
    if (IOs_ex == 0):
        result = result + IOs
        result = result + str(cnt + 4) + '\nGND GND\nVCC VCC\nGND 0\nVCC 1\n'
    else:
        test = str(IOs_ex[2]).split("\n")
        result = result + str(IOs_ex[0]) + "\n" + str(IOs_ex[1]) + "\n"
        result = result + str(cnt + 4 + (len(test)-1))+'\nGND GND\nVCC VCC\nGND 0\nVCC 1\n' + IOs_ex[2]
    result = result + luts
    #print(result)
    schm = scheme.scheme_alt()
    scheme_alt = result.split('\n')
    lines = scheme_alt
    schm.__inputs__ = lines[0].split()[1:]
    schm.__outputs__ = lines[1].split()[1:]
    elements = lines[3:-1]
    for element in elements:
        operation, *operands, result = element.split()
        schm.__elements__[result] = (operation, list(operands))
    return schm
#/////////////////////////////////////////////////////
#/////формируем строки ячеек LUT из файла yosys fpga//
#/////////////////////////////////////////////////////
def Read_file_yosys(filetoread):
    f = open(filetoread)
    regex = r"(\(.\S+\))"
    lutsreg = r"(\d+'.\d+)"
    insreg = r"(\.I[0-3]\S+)"
    outsreg = r"(\.O\(\S+)"
    inp_scheme = r"input\W\S+;"
    out_scheme = r"output\W\S+;"
    assigns_scheme = r"assign (\S+) = (\S+);"
    inp_scheme_list = []
    out_scheme_list = []
    IOs = [[],[],[]]
    lutslist = []
    inslist = []
    outslist = []
    result = []
    globalassigne = ''
    localassigne = ''
    a = []
    for line in f.readlines():
        a = re.findall(assigns_scheme, line)
        if (a != []):
            val = a.pop(0)
            if (str(val[1]) == "1\'b0"):
                localassigne = 'GND ' + val[0]
            elif (str(val[1]) == '1\'b1'):
                localassigne = 'VCC ' + val[0]
            else:
                localassigne = 'BUF ' + val[1] + ' ' + val[0]
            globalassigne = globalassigne + localassigne + "\n"
        inf = re.findall(inp_scheme, line)
        i = 0
        while i < len(inf):
            inp_scheme_list.append("".join(inf))
            i +=1
        inf = re.findall(out_scheme, line)
        i = 0
        while i < len(inf):
            out_scheme_list.append("".join(inf))
            i +=1
        inf = re.findall(insreg, line)
        i = 0
        while i < len(inf):
            inslist.append("".join(inf))
            i +=1
        inf = re.findall(outsreg, line)
        i = 0
        while i < len(inf):
            outslist.append("".join(inf))
            i +=1
        inf = re.findall(lutsreg, line)
        i = 0
        while i < len(inf):
            lutslist.append("".join(inf))
            i +=1
    num_outs_schm = len(out_scheme_list)
    out_scheme_res = ''
    while i< len(out_scheme_list):
        out_scheme_res = out_scheme_res + out_scheme_list.pop()[7:-1] + ' '
    out_scheme_res = str(num_outs_schm) + ' ' + out_scheme_res
    num_inp_schm = len(inp_scheme_list)
    inp_scheme_res = ''
    while i< len(inp_scheme_list):
        inp_scheme_res = inp_scheme_res + inp_scheme_list.pop()[6:-1] + ' '
    inp_scheme_res = str(num_inp_schm) + ' ' + inp_scheme_res
    num = len(lutslist)
    while i< num:
        localres = ""
        lastlut = lutslist.pop()
        if(lastlut[:2]=="16"):
            lluthex = hex(int(lastlut[4:], 2))
            localres = localres + inslist.pop()[4:-2] + ";"
            localres = localres + inslist.pop()[4:-2] + ";"
            localres = localres + inslist.pop()[4:-2] + ";"
            localres = localres + inslist.pop()[4:-2] + ";"
            localres = localres + lluthex + ";"
            localres = localres + outslist.pop()[3:-1] + ";"
        if (lastlut[:1] == "8"):
            lluthex = hex(int(lastlut[3:] + '00000000', 2))
            localres = localres + inslist.pop()[4:-2] + ";"
            localres = localres + inslist.pop()[4:-2] + ";"
            localres = localres + inslist.pop()[4:-2] + ";"
            localres = localres + lluthex + ";"
            localres = localres + outslist.pop()[3:-1] + ";"
        if(lastlut[:1]=="4"):
            lluthex = hex(int(lastlut[3:] + '000000000000', 2))
            localres = localres + inslist.pop()[4:-2] + ";"
            localres = localres + inslist.pop()[4:-2] + ";"
            localres = localres + lluthex + ";"
            localres = localres + outslist.pop()[3:-1] + ";"
        if(lastlut[:1]=="2"):
            lluthex = hex(int(lastlut[3:] + '00000000000000', 2))
            localres = localres + inslist.pop()[4:-2] + ";"
            localres = localres + lluthex + ";"
            localres = localres + outslist.pop()[3:-1] + ";"
        result.append(localres)
        i+=1
    IOs[0] = inp_scheme_res
    IOs[1] = out_scheme_res
    IOs[2] = globalassigne
    return result, IOs

#////////////////////////////////////////////////////////////
#ПЛИС СОЮЗ - формируем строки ячеек LUT из файла yosys fpga//
#////////////////////////////////////////////////////////////
def Read_verilog_soyus_yosys(Self):
    f = open(Self)
    Lines = f.readlines()
    Inputs = ''
    Inp_cnt = 0
    Outputs = ''
    Out_cnt = 0
    IO = []
    LUTs = []
    BUF_str = ''
    for Line in Lines:
        data = Line[:-1].replace(' ','')
        strk = data[:6]
        if (strk == 'assign'):
            Buf = Line[8:-2].replace(' ', '').split('=')
            BUF_str += 'BUF ' + Buf[1]+ ' ' + Buf[0] + "\n"
            #print()
        if (strk[:5] == 'input'):
            #print()
            Inputs += str(Line[:-1].split(' ')[3][:-1]) + ' '
            Inp_cnt += 1
        if (strk[:5] == 'outpu'):
            Outputs += Line[:-1].split(' ')[3][:-1] + ' '
            Out_cnt += 1
        if (strk == '.LUT(8'):
            #mem = ' '.join(data[8:-2])
            mem = str(hex(int(data[8:-2], 2)))
        elif(strk == '.LUT(4'):
            #mem = ' '.join(data[8:-2]+'0000')
            mem = str(hex(int(data[8:-2]+'0000', 2)))
        elif (strk[:-3] == '.A('):
            INs = data.split('(')[1][:-1][1:-2].split(',')
            INs_strk = ''
            for IN in INs:
                INs_strk += IN + ' '
        elif(strk[:-3] == '.Y('):
            LUT = str(INs_strk) +  ' ' + str(mem) +  ' ' + str(data.split('(')[1][:-1])
            LUTs.append(LUT.replace(' ', ';'))

    IO.append(str(Inp_cnt) + ' ' + Inputs)
    IO.append(str(Out_cnt) + ' ' + Outputs)
    IO.append(BUF_str)
    return LUTs, IO
#/////////////////////////////////////////////////////
#/////формируем строки ячеек LUT из файла yosys fpga//
#/////////////////////////////////////////////////////
import os
import subprocess
def print_run_file_opt_fpga(run_file, verilog_file, synth_file, graph):
    f = open(run_file, 'w')
    f.write('read_verilog ' + verilog_file + '\n')
    f.write('hierarchy -check -top circ\n')
    f.write('proc; opt; fsm; opt; techmap; opt\n')
    f.write('abc -lut 4; opt\n')
    f.write('techmap -map fpga_cells.v; opt\n')
    f.write('clean\n')
    f.write('write_verilog ' + synth_file + '\n')
    f.close()
def read_verilog2fpga_yosys (circuit):
    dfile = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    run_path = os.path.join(dfile, "utils", "bin", "win32", "yosys")
    yosys_exe = os.path.join(run_path, "yosys.exe")
    circuit_file = os.path.join(dfile, "temp", "tmp_sheme_yosys_fpga.v")
    run_file = os.path.join(dfile, "temp", "tmp_runfile_yosys_fpga.txt")
    synth_file = os.path.join(dfile, "temp", "tmp_synth_yosys_fpga.v")
    converted_circuit_file = os.path.join(dfile, "temp", "tmp_synth_conv.txt")
    graph_file = os.path.join(dfile, "temp", "synth.svg")
    debug_file = os.path.join(dfile, "temp", "yosys_fail.txt")
    if os.path.isfile(circuit_file):
        os.remove(circuit_file)
    if os.path.isfile(run_file):
        os.remove(run_file)
    if os.path.isfile(synth_file):
        os.remove(synth_file)
    if os.path.isfile(converted_circuit_file):
        os.remove(converted_circuit_file)
    print_run_file_opt_fpga(run_file, circuit, synth_file, graph_file)
    exe = yosys_exe + " < " + run_file
    try:
        ret = subprocess.check_output(exe, shell=True, cwd=run_path).decode('UTF-8')
    except:
        ret = 'Error'
    if not os.path.isfile(synth_file):
        circuit.print_circuit_in_file(debug_file)
        print('Yosys error')
        return None
    new_ckt = Read_file_yosys(synth_file)
    return new_ckt

# Scheme_alt to Scheme_alt_FPGA_yosys
import scheme.resynthesis.resynthesis_create_subckts as res

def scheme_alt2luts_yosys(schm_alt):
    testfile = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    adr_file = testfile.replace("\\","\\\\")+"\\\\temp\\\\verilog.v"
    res.print_circuit_in_verilog_file(schm_alt,'circ',adr_file)
    verilog = adr_file
    LUTs = read_verilog2fpga_yosys(verilog)
    #schm_alt_yos_fpga_file = lut2schemealt(LUTs)
    #return schm_alt_yos_fpga_file
    return LUTs
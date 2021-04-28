import os
import subprocess
import re
import scheme as sc
import string
import random

def get_project_directory():
    project_directory = os.path.abspath(os.path.dirname(__file__))
    return project_directory


def gen_name(scheme):
    """
    simple name generator
    :param scheme: scheme in scheme_alt format
    :return: unique name for this scheme
    """
    labels = scheme.input_labels()+scheme.output_labels()+scheme.element_labels()
    attempt = 'ngen'
    while (attempt in labels):
        a = string.ascii_letters + string.digits
        attempt = ''.join([random.choice(a) for i in range(4)])
    return attempt


def clean_abc_output(firstline, synth_file, converted_circuit_file):
    # get module line from initial circuit file


    f = open(converted_circuit_file, 'w')
    f.write(firstline)
    f1 = open(synth_file, 'r')
    content = f1.read()

    # input
    matches_wires = re.findall(r"\s*?((input)\s+(.*?);)", content, re.DOTALL)
    if len(matches_wires) > 0:
        f.write("\tinput ")
        wires = matches_wires[0][2].strip().split(',')
        f.write(wires[0].strip())
        for w in wires[1:]:
            f.write(', ' + w.strip())
        f.write(';\n')
    if len(matches_wires) > 1:
        print('Unexpected behaviour! Many inputs for ABC.')
        exit()

    # output
    matches_wires = re.findall(r"\s*?((output)\s+(.*?);)", content, re.DOTALL)
    if len(matches_wires) > 0:
        f.write("\toutput ")
        wires = matches_wires[0][2].strip().split(',')
        f.write(wires[0].strip())
        for w in wires[1:]:
            f.write(', ' + w.strip())
        f.write(';\n')
    if len(matches_wires) > 1:
        print('Unexpected behaviour! Many outputs for ABC.')
        exit()

    # wires
    wire_map = dict()
    matches_wires = re.findall(r"\s*?((wire) (.*?);)", content, re.DOTALL)
    if len(matches_wires) == 1:
        wires = matches_wires[0][2].strip().split(',')
        for w in wires:
            ws = w.strip()
            wire_map[ws] = 'mod_' + ws
        f.write("\twire ")
        lst = sorted(wire_map.keys())
        f.write(wire_map[lst[0]])
        for w in lst[1:]:
            f.write(', ' + wire_map[w])
        f.write(';\n')
    if len(matches_wires) > 1:
        print('Unexpected behaviour! Many wires for ABC.')
        exit()

    # Все элементы
    matches = re.findall(r"\s*?(buf|not|nand|and|nor|or|xor|xnor)\d+\s+(.*?)\((.*?);", content, re.DOTALL)
    for m in matches:
        # print(m[2])
        cell_type = m[0]
        nodes = re.search("\.O\((.*?)\)", m[2], re.M)
        if nodes is None:
            print('Error converting verilog file (3)')
        out = nodes.group(1)
        if out in wire_map:
            out = wire_map[out]

        nodes = re.findall("\.[a-z]\((.*?)\)", m[2], re.DOTALL)
        if nodes is None:
            print('Error converting verilog file (1)')

        f.write('\t' + cell_type + ' (' + out)
        for n in nodes:
            if n in wire_map:
                f.write(', ' + wire_map[n])
            else:
                f.write(', ' + n)
        f.write(');\n')
    # Bufs
    matches = re.findall(r"\s*?(vcc|gnd)\s+[^\(]+\(.O\(([^\)]+)\)\);", content)
    for m in matches:
        if m[0] == 'gnd':
            f.write('\t' + 'buf' + ' (' + m[1] + ', 1\'b0);\n')
        if m[0] == 'vcc':
            f.write('\t' + 'buf' + ' (' + m[1] + ', 1\'b1);\n')

    f.write('endmodule\n')
    f.close()
    f1.close()


def mapping_abc(out_file, path=None):
    dfile = os.path.dirname(get_project_directory())
    if path == None:
        truth_table_min = os.path.join(dfile, "utils", "bin", "win32", "espresso", "tt_min.dat")
    else:
        truth_table_min = os.path.join(path, "tt_min.dat")
    f = open(truth_table_min, "r")
    f.readline()
    f.readline()
    inwir = f.readline()[5:-1]
    outwir = f.readline()[4:-1]
    inwir = inwir.replace(" ", ", ")
    outwir = outwir.replace(" ", ", ")
    first_line = "module top (" + inwir + ", " + outwir + ");\n"
    run_path = os.path.join(dfile, "utils", "bin", "win32", "abc")
    abc_exe = os.path.join(run_path, "abc.exe")
    lib_file = os.path.join(run_path, "lib.genlib")
    if path == None:
        out_sch_file = os.path.join(run_path, out_file)
    else:
        out_sch_file = os.path.join(path, out_file)
    tmp_file = os.path.join(run_path, "tmp.v")
    if os.path.isfile(out_file):
        os.remove(out_file)
    if os.path.isfile(os.path.join(run_path, 'map.txt')):
        os.remove(os.path.join(run_path, 'map.txt'))
    f = open(os.path.join(run_path, 'map.txt'), 'w')
    f.write('read_library ' + "lib.genlib" + '\n')
    f.write('read_pla ' + truth_table_min + '\n')
    f.write("balance -l\nrewrite -l\nrefactor -l\nbalance -l\nrewrite -l\nrewrite -z -l\nbalance -l\nrefactor -z -l\nrewrite -z -l\nbalance -l\n")
    f.write('map -a -s\n')
    f.write('write tmp.v \n')
    f.close()
    exe = abc_exe + " -f map.txt"
    try:
        ret = subprocess.check_output(exe, shell=True, cwd=run_path).decode('UTF-8')
    except:
        ret = 'Error: ' + exe
    clean_abc_output(first_line, tmp_file, out_sch_file)
    os.remove(tmp_file)

    return ret


def read_verilog(filename):
    """
    verilog parser
    :param filename: filename
    :return: scheme in scheme_alt format
    """
    scheme = sc.scheme_alt()
    f = open(filename)
    file = f.read()
    # парсинг модуля и портов
    m = re.match(r"\s*module\s+(\S+)\s*\(((\s*\S+\s*,)*\s*\S+\s*)\)\s*;\s*", file)
    if m:
        ports = m.group(2)
        ports = ports.replace(' ', '')
        ports = ports.split(',')
        module_name = m.group(1)
        rest = file[0:m.start()] + file[m.end():len(file)]

    # парсинг входов
    m = re.match(r"\s*input\s+((\s*\S+\s*,)*\s*\S+\s*)\s*;\s*", rest)
    if m:
        inputs = m.group(1)
        inputs = inputs.replace(' ', '')
        inputs = inputs.split(',')
        rest = rest[0:m.start()] + rest[m.end():len(rest)]
    else:
        print('ERROR IN READING VERILOG: no inputs')
        return 0

    # парсинг выходов
    m = re.match(r"\s*output\s+((\s*\S+\s*,)*\s*\S+\s*)\s*;\s*", rest)
    if m:
        outputs = m.group(1)
        outputs = outputs.replace(' ', '')
        outputs = outputs.split(',')
        rest = rest[0:m.start()] + rest[m.end():len(rest)]
    else:
        print('ERROR IN READING VERILOG: no outputs')
        return 0

    # парсинг проводов
    m = re.match(r"\s*wire\s+((\s*\S+\s*,)*\s*\S+\s*)\s*;\s*", rest)
    if m:
        wires = m.group(1)
        wires = wires.replace(' ', '')
        wires = wires.split(',')
        rest = rest[0:m.start()] + rest[m.end():len(rest)]
    else:
        wires = []

    # парсинг тестовых проводов
    m = re.match(r"\s*wire\s+((\s*\S+\s*,)*\s*\S+\s*)\s*;\s*", rest)
    if m:
        targets = m.group(1)
        targets = targets.replace(' ', '')
        targets = targets.split(',')
        rest = rest[0:m.start()] + rest[m.end():len(rest)]
    else:
        targets = []

    # генерируем имя для VCC
    while 1:
        VCC_name = gen_name(scheme)
        if VCC_name not in wires+inputs+outputs+targets:
            break

    # генерируем имя для GND
    while 1:
        GND_name = gen_name(scheme)
        if GND_name not in wires + inputs + outputs + targets:
            break
    VCC_name += '_VCC'
    GND_name += '_GND'
    # парсинг элементов
    lines = rest.splitlines()

    for line in lines:
        m = re.match(r"\s*(\S+)\s*\(((\s*\S+\s*,)*\s*\S+\s*)\)\s*;\s*", line)
        if m:
            elt = m.group(1)
            elt = elt.upper()
            if elt == 'NOT':
                elt = 'INV'
            pts = m.group(2)
            pts = pts.replace(' ', '')
            pts = pts.split(',')
            # проверка не являются ли сигналы - нулями/единицами
            scheme.__elements__[VCC_name] = ('VCC', [])
            scheme.__elements__[GND_name] = ('GND', [])
            k=0
            for inp in pts[1:]:
                k+=1
                if (inp == '1\'b1' or inp =='1'):
                    #name = gen_name(scheme)
                    #scheme.__elements__[name] = ('VCC', [])
                    #pts[k] = name
                    pts[k] = VCC_name
                if (inp == '1\'b0' or inp == '0'):
                    #name = gen_name(scheme)
                    #scheme.__elements__[name] = ('GND', [])
                    #pts[k] = name
                    pts[k] = GND_name
            scheme.__elements__[pts[0]] = (elt, pts[1:])

    scheme.__inputs__ = inputs
    scheme.__outputs__ = outputs

    return scheme


def read_minimized_table(outputs, in_file):
    f = open(in_file, "r")
    lines = f.readlines()
    if lines[0][0] == 'e':
        rows = lines[6: 6 + int(lines[5][2:])]
    else:
        rows = lines[5: 5 + int(lines[4][2:])]
    ins = []
    outs = []
    for row in rows:
        [i, o] = row.split(' ')
        ins.append(i.replace('-', 'X'))
        outs.append(o)
    data = {i: [] for i in range(outputs)}
    for i in range(len(outs)):
        for j in range(outputs):
            if outs[i][j] == '1':
                data[j].append(ins[i])

    f.close()
    return data


def pla_gen(inputs, outputs, stimulus, reactions):
    dfile = os.path.dirname(get_project_directory())
    run_path = os.path.join(dfile, "utils", "bin", "win32",  "espresso")
    truth_table = os.path.join(run_path, "tt.dat")
    f = open(truth_table, 'w')
    f.write('.type fr\n')
    f.write('.i ' + str(len(inputs)) + '\n')
    f.write('.o ' + str(len(outputs)) + '\n')
    f.write('.ilb')
    for inp in inputs:
        f.write(' ' + inp)
    f.write('\n.ob ')
    for out in outputs:
        f.write(' ' + out)
    f.write('\n')
    for i in range(len(stimulus)):
        f.write(stimulus[i] + ' ' + reactions[i] + '\n')
    f.write('.e \n')
    f.close()


def run_espresso(path=None):
    #print('Run Espresso...')
    dfile = os.path.dirname(get_project_directory())
    run_path = os.path.join(dfile, "utils", "bin", "win32", "espresso")
    espresso_exe = os.path.join(run_path, "espresso.exe")
    if path == None:
        truth_table = os.path.join(run_path, "tt.dat")
        truth_table_min = os.path.join(run_path, "tt_min.dat")
    else:
        truth_table = os.path.join(path, "tt.dat")
        truth_table_min = os.path.join(path, "tt_min.dat")

    if os.path.isfile(truth_table_min):
        os.remove(truth_table_min)

    exe = espresso_exe + " -Dexact " + truth_table
    #exe = espresso_exe + " -o fr " + truth_table
    #exe = espresso_exe + " -o fr -efast -eonset " + truth_table
    #exe = espresso_exe + " " + truth_table
    try:
        ret = subprocess.check_output(exe, shell=True, cwd=run_path).decode('UTF-8')
    except:
        ret = 'Error'
    #if os.path.isfile(truth_table):
    #    os.remove(truth_table)
    f = open(truth_table_min, 'w')
    f.write(ret.replace("\r\n", "\n"))
    f.close()

    #data = read_minimized_table(1, truth_table_min)
    #return data


def tt2sch(inputs, outputs, stimulus, reactions):
    dfile = os.path.dirname(get_project_directory())
    run_path = os.path.join(dfile, "utils", "bin", "win32", "abc")
    tmp_file = os.path.join(run_path, "temp.v")
    #  генерируем таблицу истинности
    pla_gen(inputs, outputs, stimulus, reactions)
    # минимизируем с помощью Espresso
    run_espresso()
    # маппинг с помощью ABC
    mapping_abc("temp.v")
    sch = read_verilog(tmp_file)
    os.remove(tmp_file)
    return sch



def perebor():
    p=[]
    ipolus=[]
    b = []
    for q in itertools.product(('00', '01', '10', '11'), repeat=2):
        p.append(q)
    p.remove(('00', '00'))
    p.remove(('01', '01'))
    p.remove(('10', '10'))
    p.remove(('11', '11'))
    for q in itertools.product(('00', '01', '10', '11'), repeat=2):
        b.append(q)
    AND=[]
    OR=[]
    NAND=[]
    NOR=[]
    XOR=[]

    q=0
    for m in range (12):
        nAND=[]
        nNAND = []
        nOR = []
        nNOR = []
        nXOR = []

        for q in range(16):
                if ( b[q][0]==p[m][0] and b[q][1]==p[m][0]):
                    nAND.append(p[m][0])
                    nNAND.append(p[m][1])
                    nOR.append(p[m][0])
                    nNOR.append(p[m][1])
                    nXOR.append(p[m][0])
                elif ( b[q][0]==p[m][0] and b[q][1]==p[m][1]):
                    nAND.append(p[m][0])
                    nNAND.append(p[m][1])
                    nOR.append(p[m][1])
                    nNOR.append(p[m][0])
                    nXOR.append(p[m][1])
                elif ( b[q][0]==p[m][1] and b[q][1]==p[m][0]):
                    nAND.append(p[m][0])
                    nNAND.append(p[m][1])
                    nOR.append(p[m][1])
                    nNOR.append(p[m][0])
                    nXOR.append(p[m][1])
                elif ( b[q][0]==p[m][1] and b[q][1]==p[m][1]):
                    nAND.append(p[m][1])
                    nNAND.append(p[m][0])
                    nOR.append(p[m][1])
                    nNOR.append(p[m][0])
                    nXOR.append(p[m][0])
                else:
                    nAND.append('00')
                    nNAND.append('00')
                    nOR.append('00')
                    nNOR.append('00')
                    nXOR.append('00')

        AND.append(nAND)
        NAND.append(nNAND)
        OR.append(nOR)
        NOR.append(nNOR)
        XOR.append(nXOR)









    a=['0000',
        '0001',
        '0010',
        '0011',
        '0100',
        '0101',
        '0110',
        '0111',
        '1000',
        '1001',
        '1010',
        '1011',
        '1100',
        '1101',
        '1110',
        '1111']
    i=0
    j=1
    l=0
    nMIN=['','','','','']
    s = []
    for v in itertools.product((0, 1), repeat=12):
        s.append(v)
    nMINand=[]
    nMINor = []
    nMINnand = []
    nMINnor = []
    nMINxor = []
    ANDmin=[]
    NANDmin = []
    ORmin = []
    NORmin = []
    XORmin=[]
    for w in range(len(p)):
        ni=0
        classX = ['00','01','10','11']
        n=[]
        polus = p[w]
        classX.remove(polus[0])
        classX.remove(polus[1])
        minAND = 100
        minOR = 100
        minNAND = 100
        minNOR = 100
        minXOR = 100

        for l in range(len(s)):
            print(w,'.  ',l)
            i=0
            ni=0
            for ni in range(16):
                if AND[w][ni] != polus[0] and AND[w][ni] != polus[1]:
                    if s[l][i] == 0:
                        AND[w][ni] = classX[0]
                        OR[w][ni] = classX[0]
                        NAND[w][ni] = classX[0]
                        NOR[w][ni] = classX[0]
                        XOR[w][ni] = classX[0]
                    elif s[l][i] == 1:
                        AND[w][ni] = classX[1]
                        OR[w][ni] = classX[1]
                        NAND[w][ni] = classX[1]
                        NOR[w][ni] = classX[1]
                        XOR[w][ni] = classX[1]
                    i += 1


            sch = tt2sch(['a0', 'a1', 'b0', 'b1'], ['F0', 'F1'], a, AND[w])
            kAND = sch.elements() - 2
            sch = tt2sch(['a0', 'a1', 'b0', 'b1'], ['F0', 'F1'], a, NAND[w])
            kNAND = sch.elements() - 2
            sch = tt2sch(['a0', 'a1', 'b0', 'b1'], ['F0', 'F1'], a, OR[w])
            kOR = sch.elements() - 2
            sch = tt2sch(['a0', 'a1', 'b0', 'b1'], ['F0', 'F1'], a, NOR[w])
            kNOR = sch.elements() - 2
            sch = tt2sch(['a0', 'a1', 'b0', 'b1'], ['F0', 'F1'], a, XOR[w])
            kXOR = sch.elements() - 2

            if kAND < minAND:
                nMIN[0] = AND[w]
                minAND = kAND
            if kNAND < minNAND:
                nMIN[1] = NAND[w]
                minNAND = kNAND
            if kOR < minOR:
                nMIN[2] = OR[w]
                minOR = kOR
            if kNOR < minNOR:
                nMIN[3] = NOR[w]
                minNOR = kNOR
            if kXOR < minXOR:
                nMIN[4] = XOR[w]
                minXOR = kXOR
        nMINand.append(list.copy(nMIN[0]))
        nMINnand.append(list.copy(nMIN[1]))
        nMINor.append(list.copy(nMIN[2]))
        nMINnor.append(list.copy(nMIN[3]))
        nMINxor.append(list.copy(nMIN[4]))
        ANDmin.append(minAND)
        NANDmin.append(minNAND)
        ORmin.append(minOR)
        NORmin.append(minNOR)
        XORmin.append(minXOR)



    print ('AND')
    for w in range(12):
        print (p[w],'     ',ANDmin[w],'     ',nMINand[w])
    print ('NAND')
    for w in range(12):
        print (p[w],'     ',NANDmin[w],'     ',nMINnand[w])
    print ('OR')
    for w in range(12):
        print (p[w],'     ',ORmin[w],'     ',nMINor[w])
    print ('NOR')
    for w in range(12):
        print (p[w],'     ',NORmin[w],'     ',nMINnor[w])
    print ('XOR')
    for w in range(12):
        print (p[w],'     ',XORmin[w],'     ',nMINxor[w])
from itertools import product
import re
import os
import subprocess


def get_project_directory():
    project_directory = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return project_directory


def ispwr2(num):
    if num == 0:
        return False
    if num == 1:
        return True
    if num & 1:
        return False
    return ispwr2(num >> 1)


def func_conv(liberty_fs, inp, out):  # converts list of functions from Liberty to truth table format
    f = {}
    for i in range(len(out)):
        strg = liberty_fs[i]           # simple substitutions
        strg = strg.replace('+', '|')
        strg = strg.replace('*', '&')
        strg = strg.replace('!', '~')
        strg = strg.replace('not', '~')
        comb = list(product(inp, repeat=2))  # whitespace substitution
                                             # still PROBLEM with (A' B) case
        comb = [" ".join(elm) for elm in comb]
        comb = comb + [") " + i for i in inp]
        comb = comb + [i + " (" for i in inp]
        comb = comb + [') (']
        for c in comb:
            strg = strg.replace(c, c.replace(' ', ' & '))
        for _ in range(strg.count('\'')):   # ' ! substitution
            k = strg.find('\'')
            if strg[k-1] != ')':
                m = re.search("\w+$", strg[:k])
                inv_inp = m.group(0)
                strg = strg[:k-len(inv_inp)] + '~' + inv_inp + strg[k+1:]
            else:
                opn_brckt = 1
                inv_pos = k-1
                for letter in reversed(strg[:k-1]):
                    if letter == '(':
                        opn_brckt -= 1
                    elif letter == ')':
                        opn_brckt += 1
                    inv_pos -= 1
                    if opn_brckt == 0:
                        break
                strg = strg[:inv_pos] + '~' + strg[inv_pos:k] + strg[k+1:]
        f[out[i]] = eval('lambda ' + ', '.join(inp) + ': ' + strg)
    table = []
    for output in out:
        fun = []
        for vector in product((0, 1), repeat=len(inp)):
            fun.append(int(f[output](*vector) % 2))
        table.append(fun)
    return table


def create_basic_lib():
    lib = Library()
    lib.add_cell('AND', ['a', 'b'], ['c'], ['a&b'])
    lib.add_cell('NAND', ['a', 'b'], ['c'], ['!(a&b)'])
    lib.add_cell('OR', ['a', 'b'], ['c'], ['a|b'])
    lib.add_cell('NOR', ['a', 'b'], ['c'], ['!(a|b)'])
    lib.add_cell('XOR', ['a', 'b'], ['c'], ['a^b'])
    lib.add_cell('BUF', ['a'], ['c'], ['a'])
    lib.add_cell('INV', ['a'], ['c'], ['!a'])
    lib.add_cell('HA', ['a', 'b'], ['S', 'C'], ['a^b', 'a&b'])
    return lib


def create_fa():
    fa = Scheme()
    fa.__inputs__ = ['A', 'B', 'P']
    fa.__outputs__ 
    return 1


def evaluate(library, cell, inputs, error=0):         # calculates the value of a separate gate
    return 1


def read_verilog(filename):        # reads scheme from verilog netlist file
    return 1


def read_library(filename):        # reads library from liberty file
    lib = Library()
    out_file = os.path.join("temp", "library.txt")
    exe = os.path.join("utils", "bin", "win32", "liberty_converter.exe") + " " + filename + " " + out_file
    print(exe)
    subprocess.check_output(exe, shell=True).decode('UTF-8')
    f = open(out_file, 'r')
    for line in f:
        m = re.search("(\w+)\(([01]), ([\.|\d]+), \[([^\]]+)\], \[([^\]]+)\], \[([^\]]*)\], \[([^\]]*)\]\)", line)
        if m is None:
            print("WARNING: ", line, " is not recognized!")
            continue
        label = m.group(1)
        comb = int(m.group(2))
        area = float(m.group(3))
        inputs = m.group(4)
        inp = inputs.split(", ")
        inp = [inpt[1:-1] for inpt in inp]
        outputs = m.group(5)
        outputs = outputs.split(", ")
        outs = [outputs[i*2][1:-1] for i in range(int(len(outputs)/2))]
        funcs = [outputs[i*2+1][1:-1] for i in range(int(len(outputs)/2))]
        if 'UNKNOWN' in funcs:
            print("WARNING: ", line, " unknown output function")
            continue
        fun = []
        order = m.group(7)
        if order != "":
            order = order.split(", ")
            for el in order:
                fun.append(funcs[outs.index(el)])
            out = order
        else:
            fun = funcs
            out = outs
        probs = m.group(6)
        if probs != "":
            p = probs.split(", ")
            p = [float(prob) for prob in p]
            if len(p) == 1:
                p.insert(0, 0)
        else:
            p = []
        lib.add_cell(label, inp, out, fun, p, area, comb)
    f.close()
    return lib


class Library(object):       # basic library class
    def __init__(self):
        self.__cells__ = {}

    def cells(self):        # returns number of cells in library
        return len(self.__cells__)

    def add_cell(self, label, inp, out, f, p=[], area=0.0, seq=0, debug=0):    # adds cell to library
                                                                     # inp, out - lists of input and output pins
                                                                     # f must be a list of strings in Liberty format
                                                                     # p must be a list with length equal to number of outputs
        if type(p) != list:  # check 4 p correctness
            p = []
            for i in range(2**(len(out))):
                if ispwr2(i):
                    p.append(1)
                else:
                    p.append(0)
            if debug == 1:
                print('p is set to 1 to all outputs. p must be list')
        elif len(p) != 2**len(out):
            p = []
            for i in range(2**(len(out))):
                if ispwr2(i):
                    p.append(1)
                else:
                    p.append(0)
            if debug == 1:
                print('p is set to 1 to all outputs. p dimension must be equal to number of outputs ')

        cell = {}  # build up a cell
        cell['inputs'] = inp
        cell['outputs'] = out
        cell['seq'] = seq
        cell['area'] = area
        if seq == 0:
            cell['function'] = func_conv(f, inp, out)
            cell['p'] = p
        elif seq == 1:
            cell['function'] = []
            cell['p'] = []
        self.__cells__[label] = cell


class Scheme(object):
    def __init__(self):
        self.__inputs__ = []
        self.__outputs__ = []
        self.__cells__ = {}
        self.__nets__ = {}
        self.library = Library()

    def __str__(self):
        return '\n'.join(
            ['inputs', str(self.__inputs__), 'outputs', str(self.__outputs__), 'elements', str(self.__cells__)])

    def inputs(self):
        return len(self.__inputs__)

    def outputs(self):
        return len(self.__outputs__)

    def elements(self):
        return 1

    def input_labels(self):
        return list(self.__inputs__)

    def output_labels(self):
        return list(self.__outputs__)

    def element_labels(self):
        return 1

    def all_labels(self):
        return 1

    def process(self, input_values, error_values=None):
        return 1

    def display_truth_table(self):
        for vector in product((0, 1), repeat=self.inputs()):
            print(vector, '|', self.process(vector))

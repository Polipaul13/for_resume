# coding: utf-8
__author__ = 'IDM.IPPM (Roman Solovyev)'

import random
import scheme as sa
from scheme.resynthesis.resynthesis_create_subckts import create_circuit_external_yosys


def generate_random_ckt(num_inputs, num_outputs, max_width, circ_type='comb'):
    """
    :param num_inputs: Required number of inputs for ckt.
    :param num_outputs: Required number of outputs for ckt.
    :param max_width: maximum width of ckt.
    :return: generated ckt
    """

    overall_index = 0

    if num_inputs < 3:
        print('Too small number of inputs')

    if num_outputs < 3:
        print('Too small number of outputs')

    height = num_outputs
    width = max_width
    if width < 2:
        width = 2

    numInLevel = dict()
    for i in range(width-1):
        numInLevel[i] = random.randint(round(height/2), height)
    numInLevel[width-1] = num_outputs

    current_nodes = []
    ckt = sa.scheme_alt()
    for i in range(num_inputs):
        ckt.__inputs__.append('N_' + str(overall_index))
        current_nodes.append('N_' + str(overall_index))
        overall_index += 1

    elements = ["BUFF", "NOT", "AND", "OR", "NAND", "NOR", "XOR", "NXOR"]
    if circ_type == 'seq':
        elements.append("DFF")
    for i in range(width):
        h = numInLevel[i]
        level_nodes = []
        for j in range(h):
            o_node_name = 'N_' + str(overall_index)
            overall_index += 1
            type = random.choice(elements)
            if type == 'NOT' or type == 'BUFF':
                node = random.choice(current_nodes)
                ckt.__elements__[o_node_name] = (type, [node])
            else:
                node1 = random.choice(current_nodes)
                tmpnodes = current_nodes[:]  # fastest way to copy
                tmpnodes.remove(node1)
                node2 = random.choice(tmpnodes)
                ckt.__elements__[o_node_name] = (type, [node1, node2])
            level_nodes.append(o_node_name)
        if i == width-1:
            ckt.__outputs__ = level_nodes
        current_nodes = current_nodes + level_nodes

    return ckt


def print_circuit(ckt, file_name):
    out = open(file_name, "w")
    for i in ckt.__inputs__:
        out.write("INPUT(" + i + ")\n")
    out.write("\n")
    for i in ckt.__outputs__:
        out.write("OUTPUT(" + i + ")\n")
    out.write("\n")
    for el in ckt.__elements__:
        out.write(el + ' = ' + ckt.__elements__[el][0] + "(")
        out.write(ckt.__elements__[el][1][0])
        for i in range(1, len(ckt.__elements__[el][1])):
            out.write(", " + ckt.__elements__[el][1][i])
        out.write(")\n")
    out.close()


def print_failures(ckt, file_name):
    out = open(file_name, "w")
    total = 1
    for i in ckt.__inputs__:
        for l in ['SA0', 'SA1', 'NEG']:
            out.write(str(total) + " " + i + " " + l + "\n")
            total += 1
    for o in ckt.__outputs__:
        for l in ['SA0', 'SA1', 'NEG']:
            out.write(str(total) + " " + o + " " + l + "\n")
            total += 1

    for el in ckt.__elements__:
        if el in ckt.__outputs__ or el in ckt.__inputs__:
            continue
        for l in ['SA0', 'SA1', 'NEG']:
            out.write(str(total) + " " + el + " " + l + "\n")
            total += 1
        type = ckt.__elements__[el][0]
        if type == 'BUFF':
            out.write(str(total) + " " + el + " " + "RDOB_NOT\n")
            total += 1
        elif type == 'NOT':
            out.write(str(total) + " " + el + " " + "RDOB_BUFF\n")
            total += 1
        else:
            for l in ["AND", "OR", "NAND", "NOR", "XOR", "NXOR"]:
                if l == type:
                    continue
                out.write(str(total) + " " + el + " " + "RDOB_" + l + "\n")
                total += 1

    out.close()


def remap_node_names(ckt):

    # Fill dictionary of all available nodes
    nodes = dict()
    total = 0
    for i in ckt.__inputs__:
        if i not in nodes:
            nodes[i] = str(total)
            total += 1
    for i in ckt.__outputs__:
        if i not in nodes:
            nodes[i] = str(total)
            total += 1
    for el in ckt.__elements__:
        if el not in nodes:
            nodes[el] = str(total)
            total += 1
            for l in ckt.__elements__[el][1]:
                if l not in nodes:
                    nodes[l] = str(total)
                    total += 1

    new = sa.scheme_alt()
    for i in ckt.__inputs__:
        new.__inputs__.append(nodes[i])
    for i in ckt.__outputs__:
        new.__outputs__.append(nodes[i])
    for el in ckt.__elements__:
        lst = []
        for l in ckt.__elements__[el][1]:
            lst.append(nodes[l])
        elem = ckt.__elements__[el][0]
        if elem == 'INV':
            elem = 'NOT'
        if elem == 'BUF':
            elem = 'BUFF'
        if elem == 'XNOR':
            elem = 'NXOR'
        new.__elements__[nodes[el]] = (elem, lst)
    return new


if __name__ == '__main__':
    ckt = generate_random_ckt(10, 10, 100)
    minim = create_circuit_external_yosys(ckt)
    remaped = remap_node_names(minim)
    print_circuit(remaped, '../temp/iccad/design_05.isc')
    print_failures(remaped, '../temp/iccad/fault_description.txt')
    print(remaped)
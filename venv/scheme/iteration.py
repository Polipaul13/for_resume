from itertools import *
from operator import mul
from functools import reduce
import random
import copy

import numpy as np

from scheme.tmp.old import scheme as sc
from scheme import scheme_alt as sa


def elements_types_configurations(elements_number, used_types=None):
    if used_types is None:
        used_types = ["AND", "NAND", "OR", "NOR", "XOR", "XNOR", "INV"]
    return product(used_types, repeat=elements_number)
    
def random_elements_types_configuration(elements_number, used_types=None):
    if used_types is None:
        used_types = ["AND", "NAND", "OR", "NOR", "XOR", "XNOR", "INV"]
    return [random.choice(used_types) for _ in range(elements_number)]

def level_partitions(inputs, elements, outputs):
    if inputs != 0:
        return [[inputs] + partition for partition in level_partitions(0, elements, outputs)]
    elif outputs != 0:
        return [partition + [outputs] for partition in level_partitions(inputs, elements, 0)]
    elif elements == 0:
        return [[]]
    else:
        smaller_partitions = []
        for i in range(1, elements + 1):
            smaller_partitions += [[i] + partition for partition in level_partitions(inputs, elements - i, outputs)]

        return smaller_partitions

def random_level_partition(inputs, elements, outputs):
    if inputs != 0:
        return [inputs] + random_level_partition(0, elements, outputs)
    elif outputs != 0:
        return random_level_partition(inputs, elements, 0) + [outputs]
    elif elements == 0:
        return []
    else:
        current_level = random.randint(1, elements)
        return [current_level] + random_level_partition(inputs, elements-current_level, outputs)
        
def connections(level_partition, inputs_to_outputs=True):
    pairs = [[]] * len(level_partition)
    comb = [[]] * len(level_partition)
    for i in range(1, len(level_partition)):
        levels = level_partition[:i]
        if i == len(level_partition) - 1 and not inputs_to_outputs:
            pairs[i] = [(level_number + 1, element_number) for level_number, elements in enumerate(levels[1:]) for element_number in
                    range(elements)]
        else:
            pairs[i] = [(level_number, element_number) for level_number, elements in enumerate(levels) for element_number in
                    range(elements)]
            
        pairs[i] = product(pairs[i], repeat=2)
        comb[i] = product(pairs[i], repeat=level_partition[i])
    return product(*comb[1:])

def random_connection(level_partition, inputs_to_outputs=False):
    pairs = [[]] * len(level_partition)
    comb = [[]] * len(level_partition)
    for i in range(1, len(level_partition)):
        condition = i == len(level_partition) - 1 and not inputs_to_outputs
        comb[i] = [0] * level_partition[i]

        if not condition:
            r_level1, r_level2 = np.random.randint(0, i, size=(2, level_partition[i]))
        else:
            r_level1, r_level2 = np.random.randint(1, i, size=(2, level_partition[i]))

        for j in range(level_partition[i]):

            r_element1 = np.random.randint(0, level_partition[r_level1[j]])
            r_element2 = np.random.randint(0, level_partition[r_level2[j]])

            comb[i][j] = ((r_level1[j], r_element1), (r_level2[j], r_element2))

    return comb[1:]

def new_scheme(level_partition, connection, element_types):
    inputs = level_partition[0]
    elements = sum(level_partition[1:-1])
    outputs = level_partition[-1]
    element_types += ('o', ) * outputs
    levels = len(level_partition)
    sch = sc.scheme()
    sch.scheme = [[sc.element() for i in range(elements_on_level)] for elements_on_level in level_partition]

    for i, element in enumerate(sch.scheme[0]):
        element.type = 'i'
        element_label = 'in' + str(i)

    element_number = 0
    for i, level in enumerate(sch.scheme[1:]):
        for j, element in enumerate(level):
            element.type = element_types[element_number]
            inp1_i, inp1_j = connection[i][j][0]
            inp2_i, inp2_j = connection[i][j][1]
            element.inp1 = sch.scheme[inp1_i][inp1_j]
            element.inp2 = sch.scheme[inp2_i][inp2_j]
            if element.type == 'o':
                element.label = 'out' + str(j)
            else:
                element.label = 'el' + str(i) + '_' + str(j)

            element_number += 1

    return sch

def random_scheme(inputs, elements, outputs, used_types=None, inputs_to_outputs=False):
    
    level_partition = random_level_partition(inputs, elements, outputs)
    connection = random_connection(level_partition, inputs_to_outputs)
    element_types = random_elements_types_configuration(elements, used_types)
    
    return new_scheme(level_partition, connection, element_types)

# def circuits(inputs, outputs, elements):
#     input_labels = list(range(inputs))
#     element_labels = list(range(inputs, inputs+elements))
#
#     return None

def schemes_number(inputs, elements, types=None):
    if types is None:
        types = 6
    tmp = list(map(range, range(inputs, inputs + elements)))
    return types ** elements * reduce(mul, [len(i) * (len(i) - 1) // 2 for i in tmp])

def schemes(inputs, outputs, elements, types=None):
    if types is None:
        types = ("AND", "NAND", "OR", "NOR", "XOR", "XNOR")
    types_configurations = product(*[sorted(t, key=lambda k: random.random()) for t in [types] * elements])
    tmp = list(map(range, range(inputs, inputs + elements)))
    connections = product(*[combinations(i, r=2) for i in tmp])
    # print('confs ', len(types_configurations))
    # print('connections', len(connections))
    sch = sa.scheme_alt()
    sch.__elements__ = {'e' + str(i): ('EMPTY', []) for i in range(inputs, inputs + elements)}

    for conf, connection in product(types_configurations, connections):
        sch.__inputs__ = ['e' + str(i) for i in range(inputs)]
        sch.__outputs__ = ['e' + str(i) for i in range(inputs + elements - outputs, inputs + elements)]
        for el in range(inputs, inputs + elements):
            sch.__elements__['e' + str(el)] = (conf[el - inputs], ['e' + str(i) for i in connection[el-inputs]])
        sch = sch.subscheme_by_outputs(sch.output_labels())
        yield copy.deepcopy(sch)

# main loop
inputs = 2
outputs = 1
elements = 2

used_types = ["AND", "NAND"]

if __name__ == '__main__':
    # counter = 0
    # s = []
    # level_partition = (2, 1, 1, 1)
    # print(len(list(elements_types_configurations(elements, used_types))))
    # print(len(list(connections(level_partition))))
    #
    #
    # for connection in connections(level_partition):
    #     for elements_types_configuration in elements_types_configurations(elements, used_types):
    #         s.append(new_scheme(level_partition, connection, elements_types_configuration))
    #         counter += 1
    # print(counter)
    x = list(schemes(3, 1, 2))
    print('x')

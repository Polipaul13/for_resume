import random
from itertools import *
from math import ceil
from functools import reduce
from operator import and_

import scheme as sa
import scheme.stats as stat
import utils.python.dynamic as d
import utils.python.binary_op as b

# internal subschemes

def sch2chromo(sch):
    tmp = [(v, k) for k, v in sch.label_levels().items()]
    tmp.sort()
    order = [i for (_, i) in tmp]
    chromosome = []
    for elm in order[sch.inputs():]:
        gene = sch.__elements__[elm]
        if len(gene[1]) == 1:
            chromosome.append((gene[0], order.index(gene[1][0]), order.index(gene[1][0])))
        else:
            chromosome.append((gene[0], order.index(gene[1][0]), order.index(gene[1][1])))
    outputs = [order.index(sch.__outputs__[i]) for i in range(sch.outputs())]
    return (sch.inputs(), chromosome, outputs)

def chromo2sch(chromo):
    (inputs, chromosome, outputs) = chromo
    scheme = sa.scheme_alt()
    name = names(inputs+len(chromosome))
    scheme.__inputs__ = [name.__next__() for _ in range(inputs)]
    order = scheme.__inputs__.copy()
    for gene in chromosome:
        label = name.__next__()
        order.append(label)
        scheme.__elements__[label] = (gene[0], [order[gene[1]], order[gene[2]]])
    scheme.__outputs__ = [order[out] for out in outputs]
    return scheme

def names(max):
    for n in range(max):
        n += 1
        yield 'N' + str(n)

def scheme_cmp(sch1, sch2):  # compares equality of functions of two circuits
    if sch1.inputs() != sch2.inputs():
        return False
    n = sch1.inputs()
    for i in product((0, 1), repeat=n):
        if sch1.process(i) != sch2.process(i):
            return False
    return True

def correlation(sch1, sch2):  # compares correlation between two circuits (0% - 100%)
    if sch1.inputs() != sch2.inputs():
        return False
    correl = 0
    capacity = min(32, 2 ** sch1.inputs())
    mask = 2 ** capacity - 1
    sch1_func = d.make_process_func(sch1, capacity=capacity)
    sch2_func = d.make_process_func(sch2, capacity=capacity)
    n = sch1.inputs()
    for i in b.inputs_combinations(sch1.inputs(), capacity=capacity):
        output = (mask ^ out1 ^ out2 for out1, out2 in zip(sch1_func(i), sch2_func(i)))
        output = reduce(and_, output)
        correl += b.ones(output)
    correl /= (2 ** n)
    return correl

def random_scheme(inputs, outputs, elements, types=None):
    if types is None:
        types = ("AND", "NAND", "OR", "NOR", "XOR", "XNOR", "INV")
    name = names(inputs+elements)
    scheme = sa.scheme_alt()
    scheme.__inputs__ = [name.__next__() for _ in range(inputs)]
    for _ in range(elements):
        a = random.choice(scheme.all_labels())
        b = random.choice(scheme.all_labels())
        while b == a:
            b = random.choice(scheme.all_labels())
        scheme.__elements__[name.__next__()] = (random.choice(types), [a, b])
    roulette = []
    levels = scheme.label_levels()
    #for label in levels:                                       # More level - more likely to be an output
    #    roulette += [label for _ in range(levels[label])]
    #scheme.__outputs__ = [random.choice(roulette) for _ in range(outputs)]
    scheme.__outputs__ = random.sample(scheme.element_labels(), outputs)
    return scheme

def sch_mutation(scheme, prob = 0.001, types=None):
    if types is None:
        types = ("AND", "NAND", "OR", "NOR", "XOR", "XNOR", "INV")
    chromo = sch2chromo(scheme)
    chromo_extend = chromo[1]+[chromo[2]]
    mutant = []
    for element in chromo_extend:
        group = []
        for node in element:
            if (random.random() < prob):
                if type(node) == str:
                    gene = random.choice(types)
                elif type(node) == int:
                    gene = random.randint(0, chromo_extend.index(element)+chromo[0]-1)
            else:
                gene = node
            group.append(gene)
        mutant.append(tuple(group))
    return chromo2sch((chromo[0], mutant[0:-1], mutant[-1]))

# initial population

def initial_population_rnd(etalon, len, sigma=0.5):
    inputs = etalon.inputs()
    outputs = etalon.outputs()
    population = [random_scheme(inputs, outputs, ceil(abs(random.gauss(etalon.elements(), sigma)))) for _ in range(len)]
    return population

def initial_population_focus(etalon, len, sigma=0.5, focus=0.2, force=1):
    inputs = etalon.inputs()
    outputs = etalon.outputs()
    elements = etalon.elements()
    population = []
    for i in range(len):
        coin = random.random()
        if coin < focus:
            rate = force/(elements*3 + outputs)
            sch = sch_mutation(etalon, rate)
        else:
            sch = random_scheme(inputs, outputs, ceil(abs(random.gauss(etalon.elements(), sigma))))
        population.append(sch)
    return population

def initial_population_entropy(etalon, length, sigma=0.5):
    inputs = etalon.inputs()
    outputs = etalon.outputs()
    population = []
    while (len(population) < length):
        elm_num = ceil(abs(random.gauss(etalon.elements(), sigma)))
        if elm_num < outputs:
            elm_num = outputs
        sch = random_scheme(inputs, outputs, elm_num)
        entr = stat.entropy(sch)
        if entr < 1:
            population.append(sch)
    return population


# fitness function

def fitness(etalon, population):
   fit = [stat.correlation_multiout(etalon, scheme) for scheme in population]
   return fit

def fitness_entropy(etalon, population):
   fit = [stat.correlation_multiout(etalon, scheme) + stat.entropy(scheme) for scheme in population]
   return fit

# crossingover modules

def one_point_crossingover(sch1, sch2, prob = 0.5):
    if random.random() < prob:
        (_, chromo1, outputs1) = sch2chromo(sch1)
        (inputs, chromo2, outputs2) = sch2chromo(sch2)
        len1 = len(chromo1)
        len2 = len(chromo2)
        cutting_point = random.randint(1, (min(len1, len2)))
        newchromo1 = chromo1[0:cutting_point] + chromo2[cutting_point:len2]
        newchromo2 = chromo2[0:cutting_point] + chromo1[cutting_point:len1]
        kid1 = chromo2sch((inputs, newchromo1, outputs2))
        kid2 = chromo2sch((inputs, newchromo2, outputs1))
        return (kid1, kid2)
    else:
        return (sch1, sch2)

def two_point_crossingover(sch1, sch2, prob = 0.5):
    if random.random() < prob:
        (_, chromo1, outputs1) = sch2chromo(sch1)
        (inputs, chromo2, outputs2) = sch2chromo(sch2)
        len1 = len(chromo1)
        len2 = len(chromo2)
        cutting_point1 = random.randint(0, (min(len1, len2)))
        cutting_point2 = random.randint(0, (min(len1, len2)))
        frm = min(cutting_point1, cutting_point2)
        ntil = max(cutting_point1, cutting_point2)
        newchromo1 = chromo1[0:frm] + chromo2[frm:ntil] + chromo1[ntil:]
        newchromo2 = chromo2[0:frm] + chromo1[frm:ntil] + chromo2[ntil:]
        kid1 = chromo2sch((inputs, newchromo1, outputs1))
        kid2 = chromo2sch((inputs, newchromo2, outputs2))
        return (kid1, kid2)
    else:
        return (sch1, sch2)

# selection modules

def roulette_selection(population, fitness):
    power = len(population)
    max = sum(fitness)
    parents = []
    for _ in range(power):
        pick = random.uniform(0, max)
        current = 0
        for i in range(power):
            current += fitness[i]
            if current > pick:
                parents.append(population[i])
                break
    return parents

def tournament_selection(population, fitness):
    power = len(population)
    parents = []
    for _ in range(power):
        a = random.randint(0, power-1)
        b = random.randint(0, power-1)
        if (fitness[a] > fitness[b]):
            sch = population[a]
        else:
            sch = population[b]
        parents.append(sch)
    return parents

def best_selection(population, fitness):
    zip = zip(fitness, population)

# mutation modules

def mutation(offsprings, prob = 0.5, types=None):
    mutants = []
    for kid in offsprings:
        rate = prob/(kid.elements()*3 + kid.outputs())
        mutants.append(sch_mutation(kid, rate, types))
    return mutants

# reduction modules

def reduction(population, mutants, fitness):
    return mutants

def reduction_elite(population, mutants, fitness):
    elite = population[fitness.index(max(fitness))]
    sample = random.sample(mutants, (len(mutants)-1))
    sample.append(elite)
    return sample

def reduction_selective(population, mutants, fitness_pm):
    power = len(population)
    total = list(zip(fitness_pm, (population+mutants)))
    total.sort(key=lambda x: x[0], reverse=True)
    pop = list(list(zip(*total))[1][:power])
    fit = list(list(zip(*total))[0][:power])
    return (fit, pop)

# coupling modules

def coupling_rnd(parents, points = 1, prob = 0.5):
    offsprings = []
    for _ in range(ceil(len(parents)/2)):
        father = random.choice(parents)
        mother = random.choice(parents)
        if points == 1:
            offsprings += list(one_point_crossingover(father, mother, prob))
        elif points == 2:
            offsprings += list(two_point_crossingover(father, mother, prob))
    return offsprings[:len(parents)]

# test modules

def population_entropy(population):
    avr = 0
    for sc in population:
        avr += stat.entropy(sc)
        #print(stat.entropy(sc))
    return avr/len(population)

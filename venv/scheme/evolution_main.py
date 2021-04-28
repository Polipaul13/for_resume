__author__ = 'Telpuhov'
import time
import matplotlib.pyplot as plt
import scheme as sa
import scheme.evolution.evolution_module as em

def evolution(sch, pop_len, gens):
    if type(sch) == str:
        c17 = sa.read_scheme(sch)
        print('string')
    elif type(sch) == sa.scheme_alt:
        c17 = sch
        print('scheme')
    else:
        print('undefined scheme type')
    max_arr = []
    avr_arr = []
    entr_arr = []
    x_axis = []
    inp = c17.inputs()
    out = c17.outputs()
    el = c17.elements()
    population = em.initial_population_entropy(c17, pop_len, 1)  # generate random population
    time_fitness = 0
    time_selection = 0
    time_coupling = 0
    time_mutation = 0
    time_reduction = 0
    total = time.time()
    for gen in range(gens):

        tmp = time.time()
        fitness = em.fitness(c17, population)
        time_fitness += tmp - time.time()
        entropy = em.population_entropy(population)


        print("GENERATION # ", gen)
        print("AVERAGE = ", (sum(fitness)/len(fitness)))
        print("MAXIMUM = ", max(fitness))
        print("ENTROPY = ", entropy)
        print("=================")
        max_arr.append(max(fitness))
        avr_arr.append(sum(fitness)/len(fitness))
        entr_arr.append(entropy/out)
        x_axis.append(gen)
        if max(fitness) == 1:
            plt.plot(x_axis, avr_arr, 'b--', x_axis, max_arr, 'r', x_axis, entr_arr, 'y-')
            return population[fitness.index(max(fitness))]


        tmp = time.time()
        parents = em.tournament_selection(population, fitness)
        time_selection += tmp - time.time()

        tmp = time.time()
        offsprings = em.coupling_rnd(parents, 1, 0.9)
        time_coupling += tmp - time.time()

        tmp = time.time()
        mutants = em.mutation(offsprings, 0.5) # среднее число ошибок на 1 хромосому
        time_mutation += tmp - time.time()

        tmp = time.time()
        population = em.reduction_elite(population, mutants, fitness)
        time_reduction += tmp - time.time()

    print("time_fitness = ", time_fitness)
    print("time_selection = ", time_selection)
    print("time_coupling = ", time_coupling)
    print("time_mutation = ", time_mutation)
    print("time_reduction = ", time_reduction)
    print("TOTAL = ", total - time.time())
    plt.plot(x_axis, avr_arr, 'b--', x_axis, max_arr, 'r', x_axis, entr_arr, 'y-')
    return population[-1]


def evolution2(sch, pop_len, gens):
    if type(sch) == str:
        c17 = sa.read_scheme(sch)
        print('string')
    elif type(sch) == sa.scheme_alt:
        c17 = sch
        print('scheme')
    else:
        print('undefined scheme type')
    max_arr = []
    avr_arr = []
    x_axis = []
    inp = c17.inputs()
    out = c17.outputs()
    el = c17.elements()
    population = em.initial_population_rnd(c17, pop_len, 1)  # generate random population
    fitness = em.fitness(c17, population)

    for gen in range(gens):

        print("GENERATION # ", gen)
        print("AVERAGE = ", (sum(fitness)/len(fitness)))
        print("MAXIMUM = ", max(fitness))
        print("=================")
        max_arr.append(max(fitness))
        avr_arr.append(sum(fitness)/len(fitness))
        x_axis.append(gen)
        if max(fitness) == 1:
            plt.plot(x_axis, avr_arr, 'b--', x_axis, max_arr, 'r')
            return population[fitness.index(max(fitness))]


        parents = em.tournament_selection(population, fitness)

        offsprings = em.coupling_rnd(parents, 2, 0.5)

        mutants = em.mutation(offsprings, 8)

        fitness_mtn = em.fitness(c17, mutants)

        (fitness, population) = em.reduction_selective(population, mutants, fitness + fitness_mtn)




    plt.plot(x_axis, avr_arr, 'b--', x_axis, max_arr, 'r')
    return population[-1]


def randomution(sch, pop_len, gens):
    if type(sch) == str:
        c17 = sa.read_scheme(sch)
        print('string')
    elif type(sch) == sa.scheme_alt:
        c17 = sch
        print('scheme')
    else:
        print('undefined scheme type')
    population = em.initial_population_rnd(c17, pop_len, 1)  # generate random population
    max_arr = []
    avr_arr = []
    x_axis = []
    for gen in range(gens):
        fitness = em.fitness(c17, population)
        print("GENERATION # ", gen)
        print("AVERAGE = ", (sum(fitness)/len(fitness)))
        print("MAXIMUM = ", max(fitness+max_arr))
        print("=================")
        max_arr.append(max(fitness+max_arr))
        avr_arr.append(sum(fitness)/len(fitness))
        x_axis.append(gen)
        #if max(fitness) == 1:
        #    return population[fitness.index(max(fitness))]
        population = em.initial_population_rnd(c17, pop_len, 1)  # generate random population
    plt.plot(x_axis, avr_arr, 'b--', x_axis, max_arr, 'r')
    return population[fitness.index(max(fitness))]



#c17 = sa.read_scheme('circuits\\c18.txt')
#evolution(c17, 100, 100)


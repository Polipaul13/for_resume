from scheme.stats import error_test
from utils.python.binary_op import *
import random

def reliability_spread_lut(scheme, tests=0):
    reliability = 0.0
    spread = []
    if tests == 0 or tests > 2 ** scheme.inputs():
        tests = 2 ** scheme.inputs()
    luts = []
    names = scheme.__elements__.keys()
    for name in names:
        if (scheme.__elements__.get(name)[0] == 'LUT'):
            luts.append(str(name))
    for lut in range(len(luts)):
        error_number = 2 ** lut
        spread.append(0)
        error = num2vec(error_number, scheme.elements())
        error_count = 0.0
        for test in range(tests):
            if tests == 2 ** scheme.inputs():
                input_num = test
            else:
                input_num = random.randrange(2 ** scheme.inputs())
            input_values = num2vec(input_num, scheme.inputs())
            if error_test(scheme, input_values, error):
                error_count += 1
                spread[lut] += 1
        reliability += error_count / tests
    # return reliability, spread
    reliability = str(reliability).replace('.', ',')
    spread_str = str(spread)[1:-1]
    spread_str = spread_str.replace(',', ';')
    out = reliability + ';' + spread_str
    return out

def reliability_spread_lut3(scheme, tests=0):
    reliability = 0.0
    spread = []
    if tests == 0 or tests > 2 ** scheme.inputs():
        tests = 2 ** scheme.inputs()
    luts = []
    names = scheme.__elements__.keys()
    for name in names:
        if (scheme.__elements__.get(name)[0] == 'LUT3'):
            luts.append(str(name))
    for lut in range(len(luts)):
        error_number = 2 ** lut
        spread.append(0)
        error = num2vec(error_number, scheme.elements())
        error_count = 0.0
        for test in range(tests):
            if tests == 2 ** scheme.inputs():
                input_num = test
            else:
                input_num = random.randrange(2 ** scheme.inputs())
            input_values = num2vec(input_num, scheme.inputs())
            if error_test(scheme, input_values, error):
                error_count += 1
                spread[lut] += 1
        reliability += error_count / tests
    # return reliability, spread
    reliability = str(reliability).replace('.', ',')
    spread_str = str(spread)[1:-1]
    spread_str = spread_str.replace(',', ';')
    out = reliability + ';' + spread_str
    return out

def reliability_spread_mux(scheme, tests=0):
    reliability = 0.0
    spread = []
    if tests == 0 or tests > 2 ** scheme.inputs():
        tests = 2 ** scheme.inputs()
    luts = []
    names = scheme.__elements__.keys()
    for name in names:
        if (scheme.__elements__.get(name)[0] == 'MUX'):
            luts.append(str(name))
    for lut in range(len(luts)):
        error_number = 2 ** lut
        spread.append(0)
        error = num2vec(error_number, scheme.elements())
        error_count = 0.0
        for test in range(tests):
            if tests == 2 ** scheme.inputs():
                input_num = test
            else:
                input_num = random.randrange(2 ** scheme.inputs())
            input_values = num2vec(input_num, scheme.inputs())
            if error_test(scheme, input_values, error):
                error_count += 1
                spread[lut] += 1
        reliability += error_count / tests
    # return reliability, spread
    reliability = str(reliability).replace('.',',')
    spread_str = str(spread)[1:-1]
    spread_str = spread_str.replace(',',';')
    out = reliability + ';' + spread_str
    return out

def reliability_spread_mem(scheme, tests=0):
    random.seed()
    # находим все элементы LUT
    luts = []
    rel = 0.0
    err = 0
    Elem = [0, 0]
    spread = []
    if tests == 0 or tests > 2 ** scheme.inputs():
        tests = 2 ** scheme.inputs()
    names = scheme.__elements__.keys()
    for name in names:
        if (scheme.__elements__.get(name)[0] == 'LUT'):
            luts.append(str(name))
            spread.append(0)
    #print(luts)
    for lut in range(len(luts)):
        for i in range(16):
            Elem[0] = lut
            Elem[1] = i+4
            for i in range(tests):
                if tests == 2 ** scheme.inputs():
                    rnd_inputs = i
                else:
                    rnd_inputs = random.randrange(2 ** scheme.inputs())
                znch_schm = scheme.process(num2vec(rnd_inputs, scheme.inputs()))
                # инжектируем ошибку
                value = scheme.__elements__.pop(str(luts[Elem[0]]))  # выпиливаем LUT из схемы
                if value[1][Elem[1]] == '0':
                    value[1][Elem[1]] = '1'
                elif value[1][Elem[1]] == '1':
                    value[1][Elem[1]] = '0'
                scheme.__elements__[str(luts[Elem[0]])] = value  # возвращаем LUT обратно в схему
                znch_schm_err = scheme.process(num2vec(rnd_inputs, scheme.inputs()))
                # возвращаем исходную схему
                value = scheme.__elements__.pop(str(luts[Elem[0]]))  # выпиливаем LUT из схемы
                if value[1][Elem[1]] == '0':
                    value[1][Elem[1]] = '1'
                elif value[1][Elem[1]] == '1':
                    value[1][Elem[1]] = '0'
                scheme.__elements__[str(luts[Elem[0]])] = value
                if(znch_schm != znch_schm_err):
                    err += 1
                    spread[Elem[0]] += 1
        rel += err / tests
    # return rel, spread
    rel = str(rel).replace('.', ',')
    spread_str = str(spread)[1:-1]
    spread_str = spread_str.replace(',', ';')
    out = rel + ';' + spread_str
    return out
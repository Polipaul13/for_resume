import scheme as sch
import numpy as np
import itertools as it
import random
#from scheme.resynthesis.resynthesis_create_subckts import create_circuit_external_yosys

def create_ced(scheme, count):
    #ОСНОВНАЯ ФУНКЦИЯ ГЕНЕРАЦИИ СФК НА ОСНОВЕ МОДИФИЦИРОВАННОГО КОДА ХЭММИНГА

    SWC_ced = sch.scheme_alt()
    # ВЫЧИСЛЕНИЕ ОСНОВНЫХ ПАРАМЕТРОВ СХЕМЫ
    k = scheme.outputs()                                                # КОЛ-ВО ИНФОРМАЦИОННЫХ РАЗРЯДОВ/ВЫХОДОВ СХЕМЫ
    n = int(np.ceil(np.log2(k + 1)))                                    # КОЛ-ВО ПРОВЕРОЧНЫХ РАЗРЯДОВ
    gx = matrix_gx(n, k)                                                # ГЕНЕРАЦИЯ ПОРОЖДАЮЩЕЙ МАТРИЦЫ
    gx_elements = gx_with_elements(scheme, gx, k, n)                    # СПИСОК ЭЛ-ОВ, ДЛЯ ВЫЧИСЛЕНИЯ ПРОВЕРОЧНЫХ РАЗРЯДОВ
    gx_one_line = np.sum(gx, 1)                                         # КОЛ-ВО ЭЛ-ОВ, ДЛЯ ВЫЧИСЛЕНИЯ ПРОВЕРОЧНЫХ РАЗРЯДОВ
    scheme_1 = sch.replicate(scheme, 1)                                 # КОПИЯ О.С. ДЛЯ ФОРМИРОВАНИЯ КОДЕРА
    coder, count = create_coder(scheme_1, gx_elements, gx_one_line, n, count)       # ФОРМИРОВАНИЕ ПОДСХЕМЫ КОДЕРА
    #coder_min = create_circuit_external_yosys(coder)                                # МИНИМИЗАЦИЯ КОДЕРА С ПОМОЩЬЮ YOSYS
    decoder, count = create_decoder(scheme, gx_elements, gx_one_line, n, k, count)  # ФОРМИРОВАНИЕ ПОДСХЕМЫ ДЕКОДЕРА
    #decoder_min = create_circuit_external_yosys(decoder)                            # МИНИМИЗАЦИЯ ДЭКОДЕРА С ПОМОЩЬЮ YOSYS

    # ОБЪЕДИНЕНИЕ ОСНОВНОЙ СХЕМЫ И ПОДСХЕМЫ КОДЕРА
    conn = dict()                                                               # СОЕДИНЕНИЯ ОС И КОДЕРА
    conn_min = dict()                                                           # СОЕДИНЕНИЯ ОС И МИНИМИЗИРОВАННОГО КОДЕРА
    out = list()                                                                # ВЫХОДЫ ОС И КОДЕРА
    out_min = list()                                                            # ВЫХОДЫ ОС И МИН. КОДЕРА

    for i in range(scheme.inputs()):                                            # ЗАПОЛНЕНИЕ СЛОВОРЕЙ СОЕДИНЕНИЙ
        conn[(0, scheme.__inputs__[i])] = [(1, coder.__inputs__[i])]
        #conn_min[(0, scheme.__inputs__[i])] = [(1, coder_min.__inputs__[i])]

    for j in range(scheme.outputs()):                                           # ЗАПОЛНЕНИЕ СПИСКА ВЫХОДОВ
        out.append((0, scheme.__outputs__[j]))
        out_min.append((0, scheme.__outputs__[j]))

    for i in range(coder.outputs()):
        out.append((1, coder.__outputs__[i]))
    # for i in range(coder_min.outputs()):
    #     out_min.append((1, coder_min.__outputs__[i]))

    scheme_2 = sch.merge_schemes([scheme, coder], conn, out)                    # ОБЪЕДИНЕНИЕ ОС И КОДЕРА
    #scheme_3 = sch.merge_schemes([scheme, coder_min], conn_min, out_min)        # ОБЪЕДИНЕНИЕ ОС И МИН. КОДЕРА

    # ОБЪЕДИНЕНИЕ scheme_3/scheme_3 И ДЕКОДЕРА
    conn = dict()                                                               # СОЕДИНЕНИЯ scheme_3/scheme_3 И ДЕКОДЕРА
    conn_min = dict()                                                           # СОЕДИНЕНИЯ scheme_3/scheme_3 И МИН. ДЕКОДЕРА
    out = list()                                                                # ВЫХОДЫ scheme_3/scheme_3 И ДЕКОДЕРА
    out_min = list()                                                            # ВЫХОДЫ scheme_3/scheme_3 И МИН. ДЕКОДЕРА

    for i in range(decoder.inputs()):                                           # ЗАПОЛНЕНИЕ СЛОВОРЕЙ СОЕДИНЕНИЙ
        conn[(0, scheme_2.__outputs__[i])] = [(1, decoder.__inputs__[i])]
    # for i in range(decoder_min.inputs()):
    #     conn_min[(0, scheme_2.__outputs__[i])] = [(1, decoder_min.__inputs__[i])]

    for j in range(scheme.outputs()):                                           # ЗАПОЛНЕНИЕ СПИСКА ВЫХОДОВ
        out.append((0, scheme_2.__outputs__[j]))
        out_min.append((0, scheme_2.__outputs__[j]))

    for i in range(decoder.outputs()):
        out.append((1, decoder.__outputs__[i]))
    # for i in range(decoder_min.outputs()):
    #     out_min.append((1, decoder_min.__outputs__[i]))

    SWC_ced = sch.merge_schemes([scheme_2, decoder], conn, out)                # ФОРМИРОВАНИЕ СФК
    #SWC_ced = sch.merge_schemes([scheme_2, decoder_min], conn, out)             # ФОРМИРОВАНИЕ СФК С МИН. ДЕКОДЕРОМ
    #SWC_ced = sch.merge_schemes([scheme_3, decoder], conn, out)                # ФОРМИРОВАНИЕ СФК С МИН. КОДЕРОМ
    #SWC_ced = sch.merge_schemes([scheme_3, decoder_min], conn_min, out_min)    # ФОРМИР СФК С МИН. КОДЕРОМ И МИН. ДЕКОДЕРОМ

    return SWC_ced

def create_decoder(scheme, gx_el, one, n, k, count):
    # ФУНКЦИЯ ФОРМИРОВАНИЯ ПОДСХЕМЫ ДЕКОДЕРА

    outputs_shem = []
    for i in range(scheme.outputs()):
        outputs_shem.append(scheme.__outputs__[i])

    decoder = sch.scheme_alt()
    decoder.__inputs__ = outputs_shem

    for i in range(n):
        decoder.__inputs__.append('decoder_in_{}'.format(i))

    outputs_shem = []

    for num in range(n):
        if one[num] != 1:
            for i in range(one[num] - 1):
                if i == 0:
                    decoder.__elements__['decoder_{}'.format(count)] = ('XOR', [gx_el[num][0], gx_el[num][1]])
                    count += 1
                else:
                    decoder.__elements__['decoder_{}'.format(count)] = ('XOR', [gx_el[num][i + 1], 'decoder_{}'.format(count - 1)])
                    count += 1
            decoder.__outputs__.append('decoder_{}'.format(count - 1))
        else:
            decoder.__outputs__.append(gx_el[num][0])

    for i in range(n):  decoder.__outputs__.append(decoder.__inputs__[scheme.outputs() + i])

    if k != 1:

        for j in range(n):
            decoder.__elements__['_s{}'.format(j)] = ('XOR', [decoder.__outputs__[j], decoder.__outputs__[j + n]])
            outputs_shem.append('_s{}'.format(j))
            count += 1

        decoder.__outputs__ = []
        list_1 = outputs_shem

        if (n - 1) != 1:
            for i in range(n - 1):
                if i == 0:
                    decoder.__elements__['decoder_{}'.format(count)] = ('OR', [list_1[0], list_1[1]])
                    count += 1
                else:
                    if i == n-2:
                        decoder.__elements__['flag'] = ('OR', [list_1[i + 1], 'decoder_{}'.format(count - 1)])
                        decoder.__outputs__.append('flag')
                    else:
                        decoder.__elements__['decoder_{}'.format(count)] = ('OR', [list_1[i + 1], 'decoder_{}'.format(count - 1)])
                    count += 1
        elif (n - 1) == 1:
            for i in range(n - 1):
                if i == 0:
                    decoder.__elements__['flag'] = ('OR', [list_1[0], list_1[1]])
                    count += 1
                    decoder.__outputs__.append('flag')
    else:
        for j in range(n):
            decoder.__elements__['flag'] = ('XOR', [decoder.__outputs__[j], decoder.__outputs__[j + n]])
            count += 1
        decoder.__outputs__ = []
        for i in range(scheme.outputs() - 1):
            decoder.__outputs__.append(scheme.__outputs__[i])
        decoder.__outputs__ .append('flag')

    return decoder, count

def create_coder(coder, gx_el, one, n, count):
    # ФУНКЦИЯ ФОРМИРОВАНИЯ ПОДСХЕМЫ КОДЕРА

    for num in range(n):
        if one[num] != 1:
            for i in range(one[num] - 1):
                if i == 0:
                    coder.__elements__['coder_{}'.format(count)] = ('XOR', [gx_el[num][0], gx_el[num][1]])
                    count += 1
                else:
                    coder.__elements__['coder_{}'.format(count)] = ('XOR', [gx_el[num][i + 1], 'coder_{}'.format(count - 1)])
                    count += 1
            coder.__outputs__.append('coder_{}'.format(count - 1))
        else:
            coder.__outputs__.append(gx_el[num][0])

    outputs_coder = []
    for j in range(n):  outputs_coder.append(coder.__outputs__[coder.outputs() - n + j])
    coder.__outputs__ = outputs_coder

    return coder, count

def matrix_gx (n, k):
    # ФУНКЦИЯ ГЕНЕРАЦИИ ПОРАЖДАЮЩЕЙ МАТРИЦЫ НА ОСНОВЕ МОДИФИЦИРОВАННОГО КОДА ХЭММИНГА (SWC)
    # n - число проверочных разрядов
    # k - число информационных разрядов
    l1 = list()

    for m in it.product(range(2), repeat=n):            # ФОРМИРУЕМ МАТРИЦУ РАЗМЕРОМ NxK
        l1.append(list(m))
    gx = np.transpose(l1[1:k+1])

    return gx

def gx_with_elements(scheme, gx, k, n):
    # ФУНКЦИЯ, КОТОРАЯ ОПРЕДЕЛЯЕТ КАКИЕ ВЫХОДЫ НАДО СЛОЖИТЬ ПО МОДУЛЮ 2 ДЛЯ ПОЛУЧЕНИЯ
    # ПРОВЕРОЧНОГО РАЗРЯДА

    gx_elements = []
    for i in range(n):
        list_1 = []
        for j in range(k):
            if gx[i][j] == 1:
                list_1.append(scheme.__outputs__[:k][j-n])
        if list_1:
            gx_elements.append(list_1)

    return gx_elements

def exhaustive_stimulus(n_inputs):
    tmp = 1
    result = []

    for i in range(n_inputs - 1, -1, -1):
        result.append((2**(2**i)-1)*tmp)
        tmp *= (1+2**(2**i))

    return result

def error_simulations(ced, n):
    # моделирование СФК с помощью инжектирования ошибок

    # список кол-ва каждого типа ошибок
    t_errors = [0, 0, 0, 0]

    elements = sorted(ced.__elements__.keys())
    # максимальное число моделирований для данной СФК
    n_max = 2 ** ced.inputs() * ced.elements()

    if n_max <= n:                                  # полный перебор

        capacity = 2 ** ced.inputs()
        num = n_max

        for i in elements:
            # Список входных воздействий
            input_list = exhaustive_stimulus(ced.inputs())

            # Моделирование без инжектироания ошибок (ЭТАЛОН)
            error_list = [0] * ced.elements()
            check = ced.process(input_list, error_list, capacity)

            # Моделирование с инжектированием ошибок (СФК)
            k = elements.index(i)
            error_list[k] = 2 ** capacity - 1
            #error_list[random.randint(0, ced.elements() - 1)] = 2 ** capacity - 1
            result = ced.process(input_list, error_list, capacity)

            # Вычисление колличества ошибок каждого типа
            t_errors = type_of_err(result, check, ced.outputs(), t_errors, capacity)
    else:
        #случайное моделирование
        num = n * ced.elements()
        capacity = n

        for i in elements:
            input_list = list()
            for j in range(ced.inputs()):   input_list.append(random.randint(0, 2 ** capacity - 1))

            # Моделирование без инжектироания ошибок (ЭТАЛОН)
            error_list = [0] * ced.elements()
            check = ced.process(input_list, error_list, capacity)

            # Моделирование с инжектированием ошибок (СФК)
            # k = elements.index(i)
            # error_list[k] = 2 ** capacity - 1
            error_list[random.randint(0, ced.elements()-1)] = 2 ** capacity - 1
            result = ced.process(input_list, error_list, capacity)

            # Вычисление колличества ошибок каждого типа
            t_errors = type_of_err(result, check, ced.outputs(), t_errors, capacity)

    return t_errors, num

def type_of_err(result, check, n_outputs, t_errors, capacity):
    outputs_ced_check = list()                              #сравнение вых. СФК и ЭТАЛОНА
    flag_check = list()                                     #сравнение флагов СФК и ЭТАЛОНА

    result = list(result)
    check = list(check)

    result_flag = list()
    check_flag = list()

    for i in range(n_outputs):
        result[i] = list(bin(result[i])[2:].zfill(capacity))
        for j in range(capacity):       result[i][j] = int(result[i][j])

    for i in range(n_outputs):
        check[i] = list(bin(check[i])[2:].zfill(capacity))
        for j in range(capacity):       check[i][j] = int(check[i][j])

    result_flag.append(result[n_outputs - 1])
    check_flag.append(check[n_outputs - 1])

    if n_outputs != 2:
        result = result[:n_outputs - 1]
        check = check[:n_outputs - 1]
    else:
        result = result[n_outputs - 2]
        check = check[n_outputs - 2]

    result = np.transpose(result)
    check = np.transpose(check)

    result_flag = np.transpose(result_flag)
    check_flag = np.transpose(check_flag)

    for i in range(capacity):
        outputs_ced_check.append(np.array_equal(result[i], check[i]))
        flag_check.append(np.array_equal(result_flag[i], check_flag[i]))

    # Подсчет колличества ошибок каждого типа
    for i in range(capacity):
        if outputs_ced_check[i] and flag_check[i]:              t_errors[0] += 1            # Маскирование ошибки
        elif not outputs_ced_check[i] and flag_check[i]:        t_errors[1] += 1            # Пропуск ошибки
        elif not outputs_ced_check[i] and not flag_check[i]:    t_errors[2] += 1            # Обнаружение
        elif outputs_ced_check[i] and not flag_check[i]:        t_errors[3] += 1            # Ложная тревога

    return t_errors

#simulation Scheme
def scheme_error_simulations(ced, n):
    # моделирование СФК с помощью инжектирования ошибок

    # список кол-ва каждого типа ошибок
    t_errors = [0, 0]

    elements = sorted(ced.__elements__.keys())
    # максимальное число моделирований для данной СФК
    n_max = 2 ** ced.inputs() * ced.elements()

    if n_max <= n:                                  # полный перебор

        capacity = 2 ** ced.inputs()
        num = n_max

        for i in elements:
            # Список входных воздействий
            input_list = exhaustive_stimulus(ced.inputs())

            # Моделирование без инжектироания ошибок (ЭТАЛОН)
            error_list = [0] * ced.elements()
            check = ced.process(input_list, error_list, capacity)

            # Моделирование с инжектированием ошибок (СФК)
            k = elements.index(i)
            error_list[k] = 2 ** capacity - 1
            #error_list[random.randint(0, ced.elements() - 1)] = 2 ** capacity - 1
            result = ced.process(input_list, error_list, capacity)

            # Вычисление колличества ошибок каждого типа
            t_errors = scheme_type_of_err(result, check, ced.outputs(), t_errors, capacity)
    else:
        #случайное моделирование
        num = n * ced.elements()
        capacity = n

        for i in elements:
            input_list = list()
            for j in range(ced.inputs()):   input_list.append(random.randint(0, 2 ** capacity - 1))

            # Моделирование без инжектироания ошибок (ЭТАЛОН)
            error_list = [0] * ced.elements()
            check = ced.process(input_list, error_list, capacity)

            # Моделирование с инжектированием ошибок (СФК)
            # k = elements.index(i)
            # error_list[k] = 2 ** capacity - 1
            error_list[random.randint(0, ced.elements()-1)] = 2 ** capacity - 1
            result = ced.process(input_list, error_list, capacity)

            # Вычисление колличества ошибок каждого типа
            t_errors = scheme_type_of_err(result, check, ced.outputs(), t_errors, capacity)

    return t_errors, num

def scheme_type_of_err(result, check, n_outputs, t_errors, capacity):
    outputs_ced_check = list()                              #сравнение вых. СФК и ЭТАЛОНА

    result = list(result)
    check = list(check)

    for i in range(n_outputs):
        result[i] = list(bin(result[i])[2:].zfill(capacity))
        for j in range(capacity):       result[i][j] = int(result[i][j])

    for i in range(n_outputs):
        check[i] = list(bin(check[i])[2:].zfill(capacity))
        for j in range(capacity):       check[i][j] = int(check[i][j])

    result = np.transpose(result)
    check = np.transpose(check)

    for i in range(capacity):
        outputs_ced_check.append(np.array_equal(result[i], check[i]))

    # Подсчет колличества ошибок каждого типа
    for i in range(capacity):
        if outputs_ced_check[i]:              t_errors[0] += 1            # Маскирование ошибки
        elif not outputs_ced_check[i]:        t_errors[1] += 1            # Пропуск ошибки


    return t_errors


shem = sch.read_scheme('C://Users//Polinka//PycharmProjects//for_resume//LGSynth89//vg2.txt')
swc = create_ced(shem, 0)
t_errors, num = error_simulations(swc, 10000)
print('El', swc.elements())
print('SWC_err', t_errors, num)
#shem.display_truth_table()
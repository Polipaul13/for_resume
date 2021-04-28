'''ПРОГРАММНЫЙ МОДУЛЬ ДЛЯ ОПРЕДЕЛЕНИЯ СООТВЕТСВИЙ МЕЖДУ
РАЗНЫМИ ЗНАЧЕНИЯМИ ВЫХОДОВ СХЕМЫ И ПРОВЕРОЧНЫМИ ВЕКТОРАМИ
ДЛЯ МОДИФИЦИРОВАННОГО КОДА ХЭММИНГА (SWC)'''
########################################################################################################################
''' Программа составляет словарь, в котором ключами являются все варианты проверочных векторов g1...gn, а их значениями -  
списки всех наборов информационных разрядов f1...fk, которые дают данный проверочный вектор. 
k - число информационых разрядов/число выходов схемы
n - число проверочных разрядов (формируют проверочный вектор)
Проверочные разряды вычисляются с помощью порождающей матрицы'''
# k = [-inf - 2] - не работает (по условию)
# k = [3 - 16]  - быстро работает
# k = [17 - 22] - медленно, но ноутбук справляется
# k = 23 - ... - ноутбук подвисает, поэтому результатов так и не дождалась
########################################################################################################################
import numpy as np
import itertools as it

def match_vectors(k):
    # ОСНОВНЯ ФУНКЦИЯ
    if k > 2:                                                       # k - число выходов схемы
        inputs = inputs_generate(k)                                 # ВХОДНЫЕ ВЕКТОРА
        n = int(np.ceil(np.log2(k + 1)))                            # ЧИСЛО ПРОВЕРОЧНЫХ РАЗРЯДОВ
        matrix = matrix_create(n, k)                                # ПОРОЖДАЮЩАЯ МАТРИЦА
        one_line = np.sum(matrix, 1)                                # КОЛ-ВО ЕДИНИЦ В СТРОКАХ П. МАТРИЦЫ
        test = test_vectors_create(inputs, matrix, n, k, one_line)  # ПРОВЕРОЧНЫЕ ВЕКТОРА ДЛЯ ВСЕХ ВХОДНЫХ
        matches = search_matches(inputs, test, n, k)                # СЛОВАРЬ СООТВЕТСТВИЙ

        for iter in range(2 ** n):                                  # ВЫЧИСЛЯЕМ МИНИМАЛЬНОЕ КОДОВОЕ РАССТОЯНИЕ
            list_value = matches.values()
        min_code_distance = min(list_value)

    return min_code_distance

def search_matches(inputs, test_vectors, n, k):
    # ФУНКЦИЯ ДЛЯ ПОИСКА СООТВЕТСТВУЮЩИХ ПРОВЕРОЧНЫХ ВЕКТОРОВ
    # ПРИ РАЗНЫХ ВХОДНЫХ ВЕКТОРАХ

    # СОЗДАЕМ СПИСОК ВСЕХ ВОЗМОЖНЫХ ВАРИАНТОВ ПРОВЕРОЧНЫХ ВЕКТОРОВ
    stand = list()
    for m in it.product(range(2), repeat=n): stand.append(list(m))

    # СРАВНИВАЕМ ЗНАЧЕНИЯ ПРОВЕРОЧНЫХ ВЕКТОРОВ И ОБРАЗЦА
    # И ЗАПИСЫВАЕМ В СЛОВАРЬ ВСЕ ВХОДНЫЕ ВЕКТОРА ДЛЯ КОЖДОГО ПРОВЕРОЧНОГО ВЕКТОРА
    match = dict()
    for i in range(2 ** n):
        l3 = []
        for j in range(2 ** k):
            if test_vectors[j] == stand[i]: l3.append(inputs[j])
        match[str(stand[i])] = l3
    # ЗАПИСЫВАЕМ В ЗНАЧЕНИЯ КЛЮЧЕЙ МИНИМАЛЬНОЕ КОДОВОЕ РАССТОЯНИЕ
    for iter in range(2 ** n):
        m_val = match[str(stand[iter])]
        min_code = []
        for i in range(len(m_val) - 1):
            a = m_val[i]
            b = m_val[i + 1]
            count = 0
            for j in range(k):
                if a[j] != b[j]:
                    count += 1
            min_code.append(count)
        code_dist = min(min_code)
        match[str(stand[iter])] = code_dist

    return match

def test_vectors_create(inputs, matrix, n, k, one_line):
    # ФУНКЦИЯ ВЫЧИСЛЕНИЯ ПРОВЕРОЧНЫХ ВЕКТОРОВ ДЛЯ ВСЕХ ВХОДНЫХ ВЕКТОРОВ
    # (МОДИФ. ХЭММИНГ)

    # ОПРЕДЕЛЯЕМ СКОЛЬКО И КАКИЕ ВХОДЫ НАДО СЛОЖИТЬ ПО МОДУЛЮ 2
    # ДЛЯ КАЖДОГО ПРОВЕРОЧНОГО РАЗРЯДА В ОТДЕЛЬНОСТИ
    xor_inputs = []
    for iter in range(len(inputs)):
        inputs_i = inputs[iter]
        for i in range(n):
            list_1 = []
            for j in range(k):
                if matrix[i][j] == 1:
                    list_1.append(inputs_i[:k][j])
            if list_1:
                xor_inputs.append(list_1)

    # ВЫЧИСЛЯЕМ ПРОВЕРОЧНЫЕ РАЗРЯДЫ И ОБЪЕДИНЯЕМ ИХ В ПРОВЕРОЧНЫЙ ВЕКТОР
    # ДЛЯ КАЖДОГО ВАРИАНТА ВХОДНЫХ ВЕКТОРОВ
    Vec = []
    for iter in range(0, len(xor_inputs), n):
        xor_i = []
        test_2 = []
        for i in range(n):
            xor_i.append(xor_inputs[iter + i])
        for i in range(n):
            test_1 = 0
            list_2 = []
            if one_line[i] != 1:
                for j in range(one_line[i] - 1):
                    if j == 0:
                        test_1 = xor_i[i][0] ^ xor_i[i][1]
                    else:
                        test_1 = test_1 ^ xor_i[i][j + 1]
                list_2 = test_1
            else:
                list_2 = xor_i[i][0]
            test_2.append(list_2)
        Vec.append(test_2)

    return Vec

def inputs_generate(k):
    # ФУНКЦИЯ ГЕНЕРАЦИИ ВХОДНЫХ ВЕКТОРОВ

    inputs = list()
    for m in it.product(range(2), repeat=k): inputs.append(list(m))

    return inputs

def matrix_create (n, k):
    # ФУНКЦИЯ ГЕНЕРАЦИИ ПОРОЖДАЮЩЕЙ МАТРИЦЫ (МОДИФ. ХЭММИНГ)
    l1 = list()

    for m in it.product(range(2), repeat=n):
        l1.append(list(m))
    matrix = np.transpose(l1[1:k+1])

    return matrix

min_code_dist = match_vectors(8)
print('\n min: ', min_code_dist)
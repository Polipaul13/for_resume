# coding: utf-8
__author__ = 'IDM.IPPM (Roman Solovyev)'

import os
import random
from scheme.stats import *
import scheme as sa
from scheme.resynthesis.resynthesis_create_subckts import create_circuit_external_yosys
from scheme.resynthesis.resynthesis_external_stats import get_project_directory
from scheme.resynthesis.resynthesis_external_stats import external_vulnerability_map
from scheme.evolution.evolution_module import sch2chromo
project_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
import timeit
import json
import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.cross_validation import train_test_split
from sklearn.metrics import mean_squared_error
from math import sqrt
import statistics
import operator
import scheme.tmp.tests.nataly_tests as nt
import scheme.tmp.tests.dmtr_tests as dt
import matplotlib.pyplot as plt
# import keras
# import theano


def diffValid_minimize_percent(pred, real):
    if len(pred) != len(real):
        print("Len error!")

    score = abs(100*(pred - real)/real)
    score = sum(score)/len(score)
    return float(score)


def diffValid_xg(preds, train):
    train = train.get_label()
    return "error", diffValid_minimize_percent(preds, train)


def rmse(act, pred):
    return sqrt(mean_squared_error(act, pred))


def findMaximumError(pred, real):
    if len(pred) != len(real):
        print("Len error!")

    score = abs(100*(pred - real)/real)
    score = max(score)
    return float(score)


def generate_random_ckt(num_inputs, num_outputs, max_width):
    """
    :param num_inputs: Required number of inputs for ckt.
    :param num_outputs: Required number of outputs for ckt.
    :param max_width: maximum width of ckt.
    :return: generated ckt
    """

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
        ckt.__inputs__.append('in_'+i.__str__())
        current_nodes.append('in_'+i.__str__())

    elements = ["INV", "AND", "OR", "NAND", "NOR", "XOR", "XNOR"]
    for i in range(width):
        h = numInLevel[i]
        level_nodes = []
        for j in range(h):
            if i != width-1:
                o_node_name = 'wire_level_' + i.__str__() + '_pos_' + j.__str__()
            else:
                o_node_name = 'out_' + j.__str__()
            type = random.choice(elements)
            if type == 'INV':
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


# Проверяем если есть буферы то скорее всего схема глючная
def check_for_bufs(ckt):
    for el in ckt.__elements__:
        type = ckt.__elements__[el][0]
        if type == 'BUF':
            return 1
    return 0


# Проверяем что на каждом выходе схемы есть хоть один элемент
def check_ouputs_connected(ckt):
    for o in ckt.__outputs__:
        found = 0
        for el in ckt.__elements__:
            if el == o:
                found = 1
                break
        if found == 0:
            return 0
    return 1


def generate_ckts(num):
    total = 0
    min_inputs = 6
    max_inputs = 16
    min_outputs = 6
    max_outputs = 16
    min_level = 16
    max_level = 50
    while total < num:
        path_init = os.path.join(get_project_directory(), 'temp', 'machine_learning', 'ckt-{}-initial.txt'.format(total))
        path_opt = os.path.join(get_project_directory(), 'temp', 'machine_learning', 'ckt-{}.txt'.format(total))
        if (os.path.isfile(path_opt)):
            print('File ckt-{}.txt already exists. Skipping!'.format(total))
            total += 1
            continue
        inp_num = random.randint(min_inputs, max_inputs)
        out_num = random.randint(min_outputs, max_outputs)
        level_num = random.randint(min_level, max_level)
        print('Generate ckt. I: {} O: {} L: {}'.format(inp_num, out_num, level_num))
        ckt = generate_random_ckt(inp_num, out_num, level_num)
        minim = create_circuit_external_yosys(ckt)
        if minim is not None:
            if check_for_bufs(minim) == 1:
                print('Problem [BUFs]')
                continue
            if check_ouputs_connected(minim) == 0:
                print('Problem [Output connections]')
                continue
            print('Success')
            ckt.print_circuit_in_file(path_init)
            minim.print_circuit_in_file(path_opt)
            total += 1


def save_json(file, variable):
    f = open(file, 'w')
    json.dump(variable, f)
    f.close()


def load_json(file):
    f = open(file, 'r')
    variable = json.load(f, object_hook=lambda d: {int(k): [int(i) for i in v] if isinstance(v, list) else v for k, v in d.items()})
    f.close()
    return variable


def load_json2(file):
    f = open(file, 'r')
    variable = json.load(f)
    f.close()
    return variable


def load_json3(file):
    f = open(file, 'r')
    variable = json.load(f)
    f.close()
    vcopy = copy.deepcopy(variable)
    for el in vcopy.keys():
        variable[int(el)] = variable[el]
        variable.pop(el, None)
    return variable


def find_reliability_values(num):
    total = 0
    rel = dict()
    path_json = os.path.join(get_project_directory(), 'temp', 'machine_learning', 'reliability.json')
    if (os.path.isfile(path_json)):
        rel = load_json(path_json)
    while total < num:
        if total in rel.keys():
            print('Reliability for test {} already exists: {}. Skipping!'.format(total, rel[total]))
            total += 1
            continue
        file_name = os.path.join(get_project_directory(), 'temp', 'machine_learning', 'ckt-{}.txt'.format(total))
        ckt = sa.read_scheme(file_name)
        (reliability, vulnerability_map) = external_vulnerability_map(ckt, 10000)
        rel[total] = reliability
        total += 1
    save_json(path_json, rel)
    return rel


def max_from_dict(d1):
     v = list(d1.values())
     k = list(d1.keys())
     return d1[k[v.index(max(v))]]


def get_avg_dist(lvl, ckt):
    avg_dist = 0.0
    total = 0
    for el in ckt.__elements__:
        for node in ckt.__elements__[el][1]:
            dist = lvl[el] - lvl[node]
            if (dist < 0):
                print('Strange thing!')
                exit()
            avg_dist += dist
            total += 1
    return avg_dist/total


def find_numer_of_paths_for_node(ckt, node, pnum):
    if node in pnum.keys():
        return pnum[node]
    paths_num = 0
    for n in ckt.__elements__[node][1]:
        val = find_numer_of_paths_for_node(ckt, n, pnum)
        paths_num += val
    pnum[node] = paths_num
    return paths_num


def find_number_of_paths(ckt):
    pnum = dict()
    for i in ckt.__inputs__:
        pnum[i] = 1
    path_number = 0
    for o in ckt.__outputs__:
        path_number += find_numer_of_paths_for_node(ckt, o, pnum)
    return path_number


def get_ckt_parameters(ckt):
    param = dict()
    param['elem_num'] = len(ckt.__elements__)
    param['in_num'] = len(ckt.__inputs__)
    param['out_num'] = len(ckt.__outputs__)
    lvl = ckt.label_levels()
    param['max_level'] = max_from_dict(lvl)
    param['paths_number'] = find_number_of_paths(ckt)
    param['reconvergence_param'] = dt.depcy(ckt)

    # Ищем ширину каждого левела
    for node in lvl:
        str1 = 'level_size_{}'.format(lvl[node])
        if str1 in param.keys():
            param[str1] += 1
        else:
            param[str1] = 1

    # Ищем число разных элементов в каждом левеле
    for node in lvl:
        if node in ckt.__inputs__:
            continue
        elem = ckt.__elements__[node][0]
        str1 = 'level_{}_count_{}'.format(lvl[node], elem)
        if str1 in param.keys():
            param[str1] += 1
        else:
            param[str1] = 1

    # Ищем среднее расстояние между элементами
    param['avg_element_distance'] = get_avg_dist(lvl, ckt)

    for el in ckt.__elements__:
        type = ckt.__elements__[el][0]
        str1 = 'elements_{}'.format(type)
        if str1 in param.keys():
            param[str1] += 1
        else:
            param[str1] = 1

        # Цикл по всем входам (суммируем типы соединенмй между элементами)
        for node in ckt.__elements__[el][1]:
            if node in ckt.__inputs__:
                str1 = 'connect_{}_{}'.format('primary_input', type)
            else:
                type_in = ckt.__elements__[node][0]
                str1 = 'connect_{}_{}'.format(type_in, type)
            if str1 in param.keys():
                param[str1] += 1
            else:
                param[str1] = 1

        # Цикл по всем элементам (ищем количество элементов висящих на данном узле)
        fanout = 0
        for n in ckt.__elements__:
            for inp in ckt.__elements__[n][1]:
                if inp == el:
                    fanout += 1
        str1 = 'fanout_{}'.format(fanout)
        if str1 in param.keys():
            param[str1] += 1
        else:
            param[str1] = 1

    # Коннекты второго уровня
    for el in ckt.__elements__:
        type = ckt.__elements__[el][0]
        for node in ckt.__elements__[el][1]:
            if node not in ckt.__inputs__:
                type_in = ckt.__elements__[node][0]
                for node_in in ckt.__elements__[node][1]:
                    if node_in in ckt.__inputs__:
                        str1 = 'connect_lvl2_{}_{}_{}'.format('primary_input', type_in, type)
                    else:
                        type_in2 = ckt.__elements__[node_in][0]
                        str1 = 'connect_lvl2_{}_{}_{}'.format(type_in2, type_in, type)
                    if str1 in param.keys():
                        param[str1] += 1
                    else:
                        param[str1] = 1

    # Типы элементов на выходах схемы
    for el in ["INV", "AND", "OR", "NAND", "NOR", "XOR", "XNOR"]:
        str1 = 'out_connect_' + el
        param[str1] = 0
    for node in ckt.__outputs__:
        el = ckt.__elements__[node][0]
        str1 = 'out_connect_' + el
        param[str1] += 1

    return param


def find_unique_params(params):
    uni = []
    for el in params:
        p = params[el]
        for s in p:
            if s not in uni:
                uni.append(s)
    uni = sorted(uni)
    return uni


def element_to_index(str):
    if str == 'INV':
        return 1
    if str == 'BUF':
        return 2
    if str == 'AND':
        return 3
    if str == 'NAND':
        return 4
    if str == 'OR':
        return 5
    if str == 'NOR':
        return 6
    if str == 'XOR':
        return 7
    if str == 'XNOR':
        return 8
    return 0


def print_resulted_csv_with_chromo(params, chromo_len, chromos, reliability, csvfile):
    unique = find_unique_params(params)
    f = open(csvfile, "w")
    f.write('id,reliability')
    for i in range(len(unique)):
        f.write(',' + unique[i])
    for i in range(chromo_len):
        f.write(',ch_elem_{}'.format(i))
        f.write(',ch_in1_{}'.format(i))
        f.write(',ch_in2_{}'.format(i))
    f.write('\n')

    id = 1
    for el in sorted(params.keys()):
        par = params[el]
        f.write(str(id))
        f.write(',' + str(reliability[int(el)]))

        # Print main params
        for i in range(len(unique)):
            u = unique[i]
            if u in par.keys():
                f.write(','+str(par[u]))
            else:
                f.write(','+str(-1))

        # print chromosome
        ch = chromos[el][1]
        for i in range(len(ch)):
            f.write(','+str(element_to_index(ch[i][0])))
            f.write(','+str(ch[i][1]))
            f.write(','+str(ch[i][2]))
        for i in range(len(ch), chromo_len):
            f.write(',0')
            f.write(',0')
            f.write(',0')

        f.write('\n')
        id += 1

    f.close()


def print_resulted_csv(params, reliability, csvfile, start, end):
    unique = find_unique_params(params)
    f = open(csvfile, "w")
    f.write('id,reliability')
    for i in range(len(unique)):
        f.write(',' + unique[i])
    f.write('\n')

    id = 1
    for el in sorted(params.keys()):
        par = params[el]
        if id > start and id <= end:
            f.write(str(id))
            f.write(',' + str(reliability[int(el)]))

            # Print main params
            for i in range(len(unique)):
                u = unique[i]
                if u in par.keys():
                    f.write(','+str(par[u]))
                else:
                    f.write(','+str(-1))

            f.write('\n')
        id += 1

    f.close()


def find_ckts_parameters(num):
    total = 0
    print('Calc CKT Parameters...')
    params = dict()
    path_json = os.path.join(get_project_directory(), 'temp', 'machine_learning', 'parameters.json')
    if (os.path.isfile(path_json)):
        params = load_json3(path_json)
    while total < num:
        path_opt = os.path.join(get_project_directory(), 'temp', 'machine_learning', 'ckt-{}.txt'.format(total))
        ckt = sa.read_scheme(path_opt)
        if total not in params:
            params[total] = get_ckt_parameters(ckt)
        total += 1

    if not os.path.isfile(path_json):
        save_json(path_json, params)
    return params


def find_ckts_singlepass_values(params, num):
    total = 0
    print('Calc CKT Single Pass Values...')
    spval = dict()
    path_json = os.path.join(get_project_directory(), 'temp', 'machine_learning', 'sp_values.json')
    if (os.path.isfile(path_json)):
        spval = load_json(path_json)
    while total < num:
        path_opt = os.path.join(get_project_directory(), 'temp', 'machine_learning', 'ckt-{}.txt'.format(total))
        ckt = sa.read_scheme(path_opt)
        if total not in spval:
            spval[total] = nt.singlepass_method_lk(ckt)
        params[total]['single_pass_value'] = spval[total]
        total += 1

    save_json(path_json, spval)
    return spval


def debug_ckt():
    file_name = os.path.join(get_project_directory(), 'temp', 'machine_learning', 'ckt-{}.txt'.format(2))
    ckt = sa.read_scheme(file_name)
    (reliability, vulnerability_map) = external_vulnerability_map(ckt, 10000)
    print(reliability)


def get_features(train):
    output = list(train.columns)
    output.remove('id')
    output.remove('reliability')
    return output


def create_feature_map(features):
    outfile = open('xgb.fmap', 'w')
    for i, feat in enumerate(features):
        outfile.write('{0}\t{1}\tq\n'.format(i, feat))
    outfile.close()


def print_importance(features, gbm):
    create_feature_map(features)
    importance = gbm.get_fscore(fmap='xgb.fmap')
    importance = sorted(importance.items(), key=operator.itemgetter(1), reverse=True)
    print('Importance array:')
    print(importance)


def create_feature_importance_image(features, gbm, png_file, length=0):
    create_feature_map(features)
    importance = gbm.get_fscore(fmap='xgb.fmap')
    importance = sorted(importance.items(), key=operator.itemgetter(1))

    df = pd.DataFrame(importance, columns=['feature', 'fscore'])
    df['fscore'] = df['fscore'] / df['fscore'].sum()
    if length != 0 and length < len(df.index):
        df = df.iloc[-length:]
    param_num = len(df.index)

    featp = df.plot(kind='barh', x='feature', y='fscore', legend=False, figsize=(6, int(1+param_num/2)))
    plt.title('XGBoost Feature Importance')
    plt.xlabel('relative importance')
    fig_featp = featp.get_figure()
    fig_featp.savefig(png_file, bbox_inches='tight', pad_inches=1)
    plt.clf()


def create_histogram(diff, png_hist_file):
    n, bins, patches = plt.hist(diff, 50, normed=1, facecolor='g', alpha=0.75)
    plt.xlabel('Difference (percent)')
    plt.ylabel('Probability')
    plt.grid(True)
    plt.savefig(png_hist_file)
    plt.clf()


def run_xgboost(train_csv, test_csv, xgb_model):

    # Начальное значение для генератора случаных чисел (можно менять каждый запуск)
    random_state = 51
    # Сколько от данных брать на валидацию (в данном случае 10%)
    test_size = 0.1
    # Сколько максимально нужно итераци
    num_boost_round = 100
    # После скольки итераций если не было улучшений останавливать прогон
    early_stopping_rounds = 100
    # Параметры XGBoost
    eta = 0.2
    max_depth = 5
    subsample = 0.95
    colsample_bytree = 0.9

    print("Load train.csv")
    train = pd.read_csv(train_csv)
    features = get_features(train)
    print('Features: ' + str(features))
    print("Load test.csv")
    test = pd.read_csv(test_csv)

    print("Split train")
    X_train, X_valid = train_test_split(train, test_size=test_size, random_state=random_state)
    y_train = X_train['reliability']
    y_valid = X_valid['reliability']

    if os.path.isfile(xgb_model) and 1:
        print('Model already exists: {}. Delete it if you want to recalculate.'.format(xgb_model))
        gbm = xgb.Booster() #init model
        gbm.load_model(xgb_model) # load data
    else:
        params = {
            "objective": "reg:linear",
            # "eval_metric": "rmse",
            "eta": eta,
            "max_depth": max_depth,
            "silent": 1,
            "subsample": subsample,
            "colsample_bytree": colsample_bytree,
            "seed": random_state
        }

        dtrain = xgb.DMatrix(X_train[features], y_train)
        dvalid = xgb.DMatrix(X_valid[features], y_valid)

        watchlist = [(dtrain, 'train'), (dvalid, 'eval')]
        gbm = xgb.train(params, dtrain, num_boost_round, evals=watchlist, feval=diffValid_xg, early_stopping_rounds=early_stopping_rounds, verbose_eval=True)

        print('Saving model...')
        gbm.save_model(xgb_model)

    gbm.dump_model(xgb_model + '.raw.txt')

    print("Validating")
    if hasattr(gbm, 'best_ntree_limit'):
        yhat = gbm.predict(xgb.DMatrix(X_valid[features]), ntree_limit=gbm.best_ntree_limit)
    else:
        yhat = gbm.predict(xgb.DMatrix(X_valid[features]))
    correct = rmse(y_valid.values, yhat)
    print('RMSE value: {:.6f}'.format(correct))

    mean = statistics.mean(train['reliability'])
    stdev = statistics.stdev(train['reliability'])
    min = train['reliability'].min()
    max = train['reliability'].max()
    print('Reliability mean: ' + str(mean))
    print('Reliability stdev: ' + str(stdev))
    print('Reliability range form {} to {}'.format(min, max))

    diff = y_valid.values - yhat
    mean = statistics.mean(diff)
    stdev = statistics.stdev(diff)
    min = diff.min()
    max = diff.max()
    min_pos = diff.tolist().index(diff.min())
    max_pos = diff.tolist().index(diff.max())
    print('Critical test min: {}, {}, {}, {}'.format(min_pos, X_valid['id'].iloc[min_pos], X_valid['reliability'].iloc[min_pos], X_valid['reliability'].iloc[min_pos]-yhat[min_pos]))
    print('Critical test max: {}, {}, {}, {}'.format(max_pos, X_valid['id'].iloc[max_pos], X_valid['reliability'].iloc[max_pos], X_valid['reliability'].iloc[max_pos]-yhat[max_pos]))
    print('Prediction difference mean: ' + str(mean))
    print('Prediction difference stdev: ' + str(stdev))
    print('Prediction difference range form {} to {}'.format(min, max))
    print('Max difference percent: {} %'.format(findMaximumError(yhat, y_valid.values)))

    print_importance(features, gbm)
    png_imp_file_path = os.path.join(get_project_directory(), 'temp', 'machine_learning', 'feature_importance_plot.png')
    create_feature_importance_image(features, gbm, png_imp_file_path, 30)

    if hasattr(gbm, 'best_ntree_limit'):
        final_prediction = gbm.predict(xgb.DMatrix(test[features]), ntree_limit=gbm.best_ntree_limit)
    else:
        final_prediction = gbm.predict(xgb.DMatrix(test[features]))
    correct = rmse(test['reliability'].values, final_prediction)

    print('Prediction on test set. RMSE value: {:.6f}'.format(correct))
    diff = test['reliability'].values - final_prediction
    mean = statistics.mean(diff)
    stdev = statistics.stdev(diff)
    min = diff.min()
    max = diff.max()
    print('Prediction difference mean: ' + str(mean))
    print('Prediction difference stdev: ' + str(stdev))
    print('Prediction difference range form {} to {}'.format(min, max))
    print('Max difference percent: {} %'.format(findMaximumError(final_prediction, test['reliability'].values)))

    prediction_file_path = os.path.join(get_project_directory(), 'temp', 'machine_learning', 'last_prediction.json')
    save_json(prediction_file_path, final_prediction.tolist())

    diff = (test['reliability'] - final_prediction)/test['reliability']
    diff *= 100
    png_hist_file_path = os.path.join(get_project_directory(), 'temp', 'machine_learning', 'diff_histogram.png')
    create_histogram(diff.tolist(), png_hist_file_path)

    return gbm


def find_ckts_chromosomes(num):
    total = 0
    print('Calc CKT Chromosomes...')
    max_len = 0
    chromos = dict()
    path_json = os.path.join(get_project_directory(), 'temp', 'machine_learning', 'chromos.json')
    while total < num:
        path_opt = os.path.join(get_project_directory(), 'temp', 'machine_learning', 'ckt-{}.txt'.format(total))
        ckt = sa.read_scheme(path_opt)
        chromos[total] = sch2chromo(ckt)
        if len(chromos[total][1]) > max_len:
            max_len = len(chromos[total][1])
        total += 1
    save_json(path_json, chromos)
    return max_len, chromos


def print_real_circuits_info(path_csv_test, path_csv_test_real):
    test = pd.read_csv(path_csv_test)
    features = get_features(test)

    if 1:
        ckt_path = os.path.join(get_project_directory(), 'circuits', 'LGSynth89')
        ckt_list = ['5xp1.txt', 'alu2_synth.txt', 'alu4_synth.txt', 'cm138a_synth.txt',
                    'cu_synth.txt', 'f51m_synth.txt', 'misex1.txt', 'misex3.txt', 'misex3c.txt',
                    'x2_synth.txt']
    if 0:
        ckt_path = os.path.join(get_project_directory(), 'temp', 'machine_learning')
        ckt_list = ['ckt-19999.txt', 'ckt-19998.txt', 'ckt-19997.txt', 'ckt-19996.txt',
                    'ckt-19995.txt', 'ckt-19994.txt', 'ckt-19993.txt', 'ckt-19992.txt', 'ckt-19991.txt',
                    'ckt-19990.txt']
    ckt_list_path = []
    for ckt in ckt_list:
        ckt_list_path.append(os.path.join(ckt_path, ckt))

    total = 0
    spval = dict()
    rel = dict()
    params = dict()
    for cp in ckt_list_path:
        ckt_init = sa.read_scheme(cp)
        ckt = create_circuit_external_yosys(ckt_init)
        if ckt is not None:
            if check_for_bufs(ckt) == 1:
                print('Problem [BUFs]')
                exit()
            if check_ouputs_connected(ckt) == 0:
                print('Problem [Output connections]')
                exit()
            print('Success')

        (reliability, vulnerability_map) = external_vulnerability_map(ckt, 10000)
        rel[total] = reliability
        params[total] = get_ckt_parameters(ckt)
        spval[total] = nt.singlepass_method_lk(ckt)
        params[total]['single_pass_value'] = spval[total]
        for f in features:
            if f not in params[total].keys():
                params[total][f] = -1
        total += 1
    print_resulted_csv(params, rel, path_csv_test_real, 0, len(params))


def analize_real_circuits(xgb_model, test_csv):
    gbm = xgb.Booster() #init model
    gbm.load_model(xgb_model) # load data
    print("Load test.csv")
    test = pd.read_csv(test_csv)
    features = get_features(test)
    print('Features: ' + str(features))
    yhat = gbm.predict(xgb.DMatrix(test[features]))
    correct = rmse(test['reliability'], yhat)
    real = test['reliability'].tolist()
    for i in range(len(yhat)):
        perc = 100*(yhat[i] - real[i])/real[i]
        print("Real: {} Predicted: {} Diff: {}%".format(round(real[i], 2), round(yhat[i], 2), round(perc, 2)))
    print('RMSE value: {:.6f}'.format(correct))


# debug_ckt()
random.seed(1)
path_csv_train = os.path.join(get_project_directory(), 'temp', 'machine_learning', 'CSV', '!train.csv')
path_csv_test = os.path.join(get_project_directory(), 'temp', 'machine_learning', 'CSV', '!test.csv')
path_csv_test_real_circ = os.path.join(get_project_directory(), 'temp', 'machine_learning', 'CSV', '!test_real.csv')
xgb_model = os.path.join(get_project_directory(), 'temp', 'machine_learning', 'models', 'model.xgb')

if 0:
    test_num = 20000
    # generate_ckts(test_num)
    rel = find_reliability_values(test_num)
    params = find_ckts_parameters(test_num)
    sp_values = find_ckts_singlepass_values(params, test_num)
    # max_len, chromos = find_ckts_chromosomes(test_num)
    split = round(3*test_num/4)
    print_resulted_csv(params, rel, path_csv_train, 0, split)
    print_resulted_csv(params, rel, path_csv_test, split, test_num)

if 1:
    # gbm = run_xgboost(path_csv_train, path_csv_test, xgb_model)
    print_real_circuits_info(path_csv_test, path_csv_test_real_circ)
    analize_real_circuits(xgb_model, path_csv_test_real_circ)


# 3.31 - Initial RMSE
# 3.2073792386409905 - added variables level_N_count_ELEM
# 3.169510 - connection of 3 elements
# 2.4233 - added features "paths_number" and "single_pass_value"
# 2.380795 - added number output elements of different types
# 1.78 - added corrected single_pass and number of reconv paths

# New metric (Avg diff in percent):
# RMSE: 1.826477 Metric: 3.147930% Max difference percent: 21.5%

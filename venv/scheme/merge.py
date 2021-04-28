from itertools import combinations
from os import system

import scheme.stats as stat
from scheme.tmp.old import scheme as sc


def choose(n, k):
    """
    A fast way to calculate binomial coefficients by Andrew Dalke (contrib).
    """
    if 0 <= k <= n:
        ntok = 1
        ktok = 1
        for t in range(1, min(k, n - k) + 1):
            ntok *= n
            ktok *= t
            n -= 1
        return ntok // ktok
    else:
        return 0


def espresso_to_rom(espresso_filename, rom_filename):
    # system("del minimized.dat")
    # system("del res.wb")
    system(".\misc\espresso.exe -Dexact " + espresso_filename + " >> minimized.dat")
    system(".\misc\misii.exe -f script -t pla -T blif minimized.dat")
    system("php .\misc\\blif2rom.php " + rom_filename)
    system("del minimized.dat")
    system("del res.wb")


def st_voter_scheme(outputs, redundancy):
    if outputs < 1:
        return st_voter_scheme(1, redundancy)
    st_voter_part_tt = stat.standard_voter_truth_table(1, redundancy)
    stat.write_truth_table_to_espresso(st_voter_part_tt, "st_voter_temp_tt.txt")
    espresso_to_rom("st_voter_temp_tt.txt", "st_voter_temp.txt")
    st_voter_part = sc.fread_scheme("st_voter_temp.txt")
    st_voter = sc.replicate(st_voter_part, 0, outputs)
    return st_voter


def most_connected_outputs(sch, outputs_to_choose, redundancy=3, p=0.001):
    outputs_number = sch.outputs()
    # lazy implemenatation
    best_opt_voter_elements = 100000
    best_comb = list(range(outputs_to_choose))
    for outputs_comb in map(list, combinations(range(outputs_number), outputs_to_choose)):
        print(outputs_comb)
        print(best_opt_voter_elements)
        table_reduce = stat.transition_table(sch, tests=1000, prob=p, indexes=outputs_comb)

        opt_tr = stat.optimal_voter_truth_table(table_reduce, redundancy)
        stat.write_truth_table_to_espresso(opt_tr, "opt_voter_temp_tt.txt")
        espresso_to_rom("opt_voter_temp_tt.txt", "opt_voter_temp.txt")
        opt_voter = sc.fread_scheme("opt_voter_temp.txt")
        if opt_voter.elements() < best_opt_voter_elements:
            best_comb = outputs_comb
            best_opt_voter_elements = opt_voter.elements()

    st_voter = st_voter_scheme(outputs_to_choose, redundancy)
    print("best combination ", best_comb)
    print("opt_voter_elements ", best_opt_voter_elements)
    print("st_voter_elements ", st_voter.elements())
    print("diff ", best_opt_voter_elements / st_voter.elements())

    return best_comb


def mix_connections(outputs, c_outputs, redundancy):
    scheme_outputs = list(range(outputs * redundancy))
    voter_inputs = list(range(outputs * redundancy))

    not_c_outputs = [i for i in range(outputs) if i not in c_outputs]

    c_outputs_numb = len(c_outputs)
    not_c_outputs_numb = outputs - c_outputs_numb

    connected = [i + j * outputs for j in range(redundancy) for i in c_outputs]
    unconnected = [i + j * outputs for i in not_c_outputs for j in range(redundancy)]

    part1 = list(zip(connected, range(c_outputs_numb * redundancy)))
    part2 = list(zip(unconnected, range(c_outputs_numb * redundancy, outputs * redundancy)))

    return list(part1) + list(part2)


def test_scheme(sch, p, redundancy, outputs_to_choose, debug=False):
    c_outputs = stat.most_connected_outputs(sch, outputs_to_choose)

    ttable_reduce = stat.transition_table(sch, tests=1000, prob=p, indexes=c_outputs)
    opt_tr = stat.optimal_voter_truth_table(ttable_reduce, redundancy)

    stat.write_truth_table_to_espresso(opt_tr, "opt_voter_part_tt.txt")
    print("opt_voter_part_tt")

    last_outputs = sch.outputs() - outputs_to_choose
    print('opt_voter')
    espresso_to_rom("opt_voter_part_tt.txt", "opt_voter_part.txt")

    opt_voter_part = sc.fread_scheme("opt_voter_part.txt")
    print('st_voter_part')
    st_voter_part = st_voter_scheme(last_outputs, redundancy)
    standard_voter = st_voter_scheme(sch.outputs(), redundancy)

    r_scheme = sc.replicate(sch, 1, redundancy)

    if last_outputs == 0:
        mix_voter = opt_voter_part
    else:
        mix_voter = sc.merge(opt_voter_part, st_voter_part, [])

    mix_connection_pairs = mix_connections(sch.outputs(), c_outputs, redundancy)
    redundant_mix = sc.merge(r_scheme, mix_voter, mix_connection_pairs)
    st_connection_pairs = mix_connections(sch.outputs(), [], redundancy)
    redundant_standard = sc.merge(r_scheme, standard_voter, st_connection_pairs)

    return c_outputs, stat.eof_p(sch, 1, debug), stat.eof_p(redundant_standard, 1, debug), stat.eof_p(redundant_mix, 1,
                                                                                                      debug), sc.scheme_cmp(
        sch, redundant_standard), sc.scheme_cmp(sch, redundant_mix), redundant_standard, redundant_mix
    # return c_outputs, stat.eof(sch, 10000, 0.0001), stat.eof(redundant_standard, 10000, 0.0001), stat.eof(redundant_mix, 10000, 0.0001), sc.scheme_cmp(sch, redundant_standard), sc.scheme_cmp(sch, redundant_mix), redundant_standard, redundant_mix


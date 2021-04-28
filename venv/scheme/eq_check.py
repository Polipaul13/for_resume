import subprocess
import os
import scheme as sc

def get_project_directory():
    project_directory = os.path.abspath(os.path.dirname(__file__))
    return project_directory


def equivalence_check_abc():
    '''
     Проводим проверку на эквивалентность двух схем в директории
     utils/bin/win32/abc - sch1.v и sch2.v
     :return: возвращаем 1 - в случае эквивалентности
                         0 - в обратном случае
                         сообщение об ошибке - при ошибке
     '''


    dfile = os.path.dirname(get_project_directory())
    run_path = os.path.join(dfile, "utils", "bin", "win32", "abc")
    s1_path = 'sch1.v'
    s2_path = 'sch2.v'
    check_txt = 'check.txt'

    abc_exe = os.path.join(run_path, "abc.exe")

    f = open(os.path.join(run_path, 'check.txt'), 'w')
    f.write('cec ' + s1_path + ' ' + s2_path +'\n')
    f.close()
    # print('OK')
    # exit()
    # checking...
    exe = abc_exe + " -f " + check_txt
    try:
        ret = subprocess.check_output(exe, cwd=run_path, timeout=60).decode('UTF-8')
    except subprocess.TimeoutExpired:
        ret = 'Error: ' + exe
        print('Timeout')
    except:
        ret = 'Error: ' + exe + ' Working dir:' + run_path
    # print(ret)
    if 'NOT EQUIVALENT' in ret:
        #print('Schemes are NOT equivalent')
        result = 0
    elif 'are equivalent' in ret:
        #print('Schemes are equivalent')
        result = 1
    else:
        #print('EQUIVALENCE CHECK FAILED')
        print(ret)
        result = None
    if os.path.isfile(os.path.join(run_path, s1_path)):
        os.remove(os.path.join(run_path, s1_path))
    if os.path.isfile(os.path.join(run_path, s2_path)):
        os.remove(os.path.join(run_path, s2_path))
    return result

def eq_check(sch1, sch2):

    '''
     Проводим проверку на эквивалентность двух схем в
     SchemeAlt() формате - sch1 и sch2
     :return: возвращаем 1 - в случае эквивалентности
                         0 - в обратном случае
                         сообщение об ошибке - при ошибке
     '''

    dfile = os.path.dirname(get_project_directory())
    run_path = os.path.join(dfile, "utils", "bin", "win32", "abc")
    s1_path = 'sch1.v'
    s2_path = 'sch2.v'
    sch1.print_verilog_in_file(os.path.join(run_path, s1_path), "top")
    sch2.print_verilog_in_file(os.path.join(run_path, s2_path), "top")
    ret = equivalence_check_abc()
    return ret

if __name__ == '__main__':
    c17 = sc.read_scheme("..\\circuits\\ISCAS\\c17.txt")
    c18 = sc.read_scheme("..\\circuits\\ISCAS\\c17.txt")
    print(eq_check(c17, c18))
    c18.__elements__['G10gat'] = ('AND', ['G1gat', 'G3gat'])
    print(eq_check(c17, c18))
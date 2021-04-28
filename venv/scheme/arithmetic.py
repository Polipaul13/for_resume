from math import log2, ceil
from operator import mul
from functools import reduce
from copy import deepcopy

from scheme.utils.python.binary_op import *


def add_polinomials(poly1, poly2):
    result = deepcopy(poly1)

    for key, value in poly2.items():
        if key in result:
            result[key] += value
        else:
            result[key] = value

    result = {key: value for key, value in result.items() if value != 0}

    return result


def neg_polinomial(poly):
    return {key: -value for key, value in poly.items() if value != 0}


def mult_polinomials(poly1, poly2):
    result = {}
    for key1, value1 in poly1.items():
        for key2, value2 in poly2.items():

            result_key = key1 | key2
            result_value = value1 * value2
            if result_key in result:
                result[result_key] += result_value
            else:
                result[result_key] = result_value
    result = {key: value for key, value in result.items() if value != 0}

    return result


class Polynomial:
    def __init__(self, monomials):
        self.monomials = dict(monomials)

    def __add__(self, poly):
        monomials = add_polinomials(self.monomials, poly.monomials)
        return Polynomial(monomials)

    def __radd__(self, number):
        return Polynomial({0: number}) + self

    def __neg__(self):
        monomials = neg_polinomial(self.monomials)
        return Polynomial(monomials)

    def __sub__(self, poly):
        return self + (-poly)

    def __rsub__(self, number):
        return Polynomial({0: number}) - self

    def __mul__(self, poly):
        monomials = mult_polinomials(self.monomials, poly.monomials)
        return Polynomial(monomials)

    def __rmul__(self, number):
        return Polynomial({0: number}) * self

    def __and__(self, poly):
        return self * poly

    def __or__(self, poly):
        return self + poly - (self * poly)

    def __xor__(self, poly):
        return self + poly - (2 * self * poly)

    def __str__(self):
        return str(self.monomials)

    def process(self, inputs):
        N = len(inputs)

        def process_monomial(key, value, inputs):
            key_vec = num2vec(key, N)
            vec = [inputs[i] for i in range(N) if key_vec[i] == 1]
            return value * reduce(mul, vec, 1)

        return sum([process_monomial(key, value, inputs) for key, value in self.monomials.items()])


def arithmetic_polynomial(sch):
    N = sch.inputs()
    M = sch.outputs()
    inputs = [Polynomial({2 ** i: 1}) for i in range(N)]
    polinomials_by_outputs = sch.process(inputs)

    return sum([2 ** i * polinomials_by_outputs[i] for i in range(M)])


def polynomial_to_str(poly, inputs_names=None):
    N = ceil(max(map(log2, [key for key in poly.monomials.keys() if key != 0])))
    if inputs_names is None:
        inputs_names = ['i' + str(j) for j in range(N)]

    def sign_to_str(value):
        if value < 0:
            return '-'
        else:
            return '+'

    def value_to_str(value):
        return str(abs(value))

    def monomial_to_str(key, value):
        return sign_to_str(value) + ' ' + value_to_str(value) + ''.join(
            [inputs_names[i] for i in range(N) if num2vec(key, N)[i] == 1])

    return ' '.join([monomial_to_str(key, value) for key, value in poly.monomials.items()])
#               This file is part of the QuTIpy package.
#                https://github.com/sumeetkhatri/QuTIpy
#
#                   Copyright (c) 2023 Sumeet Khatri.
#                       --.- ..- - .. .--. -.--
#
#
# SPDX-License-Identifier: AGPL-3.0
#
#  This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import itertools

import numpy as np
from numpy.linalg import matrix_power, inv

from qutipy.general_functions import Tr, dag, ket, tensor, eye


def discrete_Weyl_X(d):
    """
    Generates the X shift operators.
    """

    X = ket(d, 1) @ dag(ket(d, 0))

    for i in range(1, d):
        X = X + ket(d, np.mod(i + 1,d)) @ dag(ket(d, i))

    return X


def discrete_Weyl_Z(d):
    """
    Generates the Z phase operators.
    """

    w = np.exp(2 * np.pi * 1j / d)

    Z = ket(d, 0) @ dag(ket(d, 0))

    for i in range(1, d):
        Z = Z + w**i * ket(d, i) @ dag(ket(d, i))

    return Z


def discrete_Weyl(d, z, x):
    """
    Generates the discrete Weyl operator Z^zX^x.
    """

    return matrix_power(discrete_Weyl_Z(d), z) @ matrix_power(discrete_Weyl_X(d), x)


def discrete_Weyl_basis(d):
    """
    Generates a list of all d^2 discrete-Weyl operators.
    """

    B = []
    for z in range(d):
        for x in range(d):
            B.append(discrete_Weyl(d, z, x))

    return B


def generate_nQudit_X(d, indices):
    """
    Generates a tensor product of discrete Weyl-X operators. indices is a
    list of dits (i.e., each element of the list is a number between 0 and
    d-1).
    """

    X = discrete_Weyl_X(d)

    out = 1

    for index in indices:
        out = tensor(out, matrix_power(X, index))

    return out


def generate_nQudit_Z(d, indices):
    """
    Generates a tensor product of discrete Weyl-Z operators. indices is a
    list of dits (i.e., each element of the list is a number between 0 and
    d-1).
    """

    Z = discrete_Weyl_Z(d)

    out = 1

    for index in indices:
        out = tensor(out, matrix_power(Z, index))

    return out


def nQudit_discrete_Weyl_basis(d, n):
    """
    Generates a list of all n-fold tensor products of the
    discrete Weyl operators acting in d dimensions.
    """

    S = list(itertools.product(range(d), repeat=n))

    B = []

    for s1 in S:
        for s2 in S:
            B.append(generate_nQudit_Z(d, s1) @ generate_nQudit_X(d, s2))

    return B


def nQudit_cov_matrix(X, d, n):
    """
    Generates the matrix of second moments (aka covariance matrix) of an
    n-qudit operator X.
    """

    S = nQudit_quadratures(d, n)

    V = np.array(np.zeros((2 * n, 2 * n)), dtype=np.complex128)

    for i in range(2 * n):
        for j in range(2 * n):
            V[i, j] = Tr(X @ S[i + 1] @ dag(S[j + 1]))

    return V


def nQudit_quadratures(d, n):
    """
    Returns the list of n-qudit "quadrature" operators, which are defined as
    (for two qudits)

        S[0]=X(0) ⊗ Id
        S[1]=Z(0) ⊗ Id
        S[2]=Id ⊗ X(0)
        S[3]=Id ⊗ Z(0)

    In general, for n qubits:

        S[0]=X(0) ⊗ Id ⊗ ... ⊗ Id
        S[1]=Z(0) ⊗ Id ⊗ ... ⊗ Id
        S[2]=Id ⊗ X(0) ⊗ ... ⊗ Id
        S[3]=Id ⊗ Z(0) ⊗ ... ⊗ Id
        .
        .
        .
        S[2n-2]=Id ⊗ Id ⊗ ... ⊗ X(0)
        S[2n-1]=Id ⊗ Id ⊗ ... ⊗ Z(0)
    """

    S = {}

    count = 0

    for i in range(1, 2 * n + 1, 2):
        v = list(np.array(dag(ket(n, count)), dtype=int).flatten())
        S[i] = generate_nQudit_X(d, v)
        S[i + 1] = generate_nQudit_Z(d, v)
        count += 1

    return S


def nQudit_Weyl_coeff(X, d, n):
    """
    Generates the coefficients of the operator X acting on n qudit
    systems.
    """

    C = {}

    S = list(itertools.product(*[range(0, d)] * n))

    for s in S:
        s = list(s)
        for t in S:
            t = list(t)
            G = generate_nQudit_X(d, s) @ generate_nQudit_Z(d, t)
            C[(str(s), str(t))] = (1 / d**n) * np.around(Tr(dag(G) @ X), 10)

    return C


def flip_sign(d):
    """
    Generates the operator that flips the sign of the standard basis
    elements in d dimension, i.e., it does
        |i> --> |-i>,
    where the negation is performed modulo d.
    """

    P = ket(d, 0) @ dag(ket(d, 0))

    for i in range(1, d):
        P = P + ket(d, np.mod(-i,d)) @ dag(ket(d, i))

    return P


def CNOT_qudit(d,alt=False):
    """
    Generates the qudit CNOT gate, which we define as
        |i>|j> --> |i>|i-j>,
    where the subtraction is performed modulo d.

    If alt=True, then we use the definition
        |i>|j> --> |i>|i+j>,
    where the addition is performed modulo d.

    Both definitions come from:
        'Efficient bipartite quantum state purification in 
        arbitrary dimensional Hilbert spaces', Alber et al.,
        J. Phys. A: Math. Gen. 34, 8821 (2001), arXiv:quant-ph/0102035
    """

    P=flip_sign(d)

    C=tensor(ket(d,0)@dag(ket(d,0)),eye(d))

    X=discrete_Weyl_X(d)

    for i in range(1,d):
        Xi=matrix_power(X,i)
        if alt:
            C+=tensor(ket(d,i)@dag(ket(d,i)),Xi)
        else:    
            C+=tensor(ket(d,i)@dag(ket(d,i)),Xi@P)

    return C



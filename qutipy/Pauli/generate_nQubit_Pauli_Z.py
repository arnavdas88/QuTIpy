'''
This code is part of QuTIPy.

(c) Copyright Sumeet Khatri, 2021

This code is licensed under the Apache License, Version 2.0. You may
obtain a copy of this license in the LICENSE.txt file in the root directory
of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.

Any modifications or derivative works of this code must retain this
copyright notice, and modified files need to carry a notice indicating
that they have been altered from the originals.
'''


import numpy as np

from qutipy.general_functions import tensor,eye


def generate_nQubit_Pauli_Z(indices):

    '''
    Generates a tensor product of Pauli-Z operators for n qubits. indices is
    a list of bits.
    '''

    Id=eye(2)
    Sz=np.matrix([[1,0],[0,-1]])

    out=1

    for index in indices:
        if index==0:
            out=tensor(out,Id)
        elif index==1:
            out=tensor(out,Sz)
        else:
            return('Error: Indices must be bits, either 0 or 1!')
    
    return out
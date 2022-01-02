# Copyright (c) 2022 Michael Casadevall
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

'''Contains the top level objects for vaccine codes'''

import enum

class VaccineTypes(enum.Enum):
    '''Enumerated values for vaccine codes'''
    PFIZER_COMIRNATY = enum.auto()
    JANSSEN = enum.auto()
    MODERNA = enum.auto()
    ASTRAZENECA = enum.auto()
    NOVAVAX = enum.auto()
    SINOPHARM = enum.auto()
    CORONAVAX = enum.auto()
    UNKNOWN = enum.auto()

FHIRVaccineCodeDictionary = {
    # Phfizer vaccine codes 
    208 : VaccineTypes.PFIZER_COMIRNATY,
    217 : VaccineTypes.PFIZER_COMIRNATY,
    218 : VaccineTypes.PFIZER_COMIRNATY,

    207 : VaccineTypes.MODERNA,

    212 : VaccineTypes.JANSSEN,

    210 : VaccineTypes.ASTRAZENECA,

    # non us codes, known to be incomplete - NC 01/02/22
    510 : VaccineTypes.SINOPHARM,
    511 : VaccineTypes.NOVAVAX,

    # Unknwon code, should never use
    213 : VaccineTypes.UNKNOWN
}
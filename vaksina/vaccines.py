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
import json

class VaccineManager(object):
    '''Manages all data for vaccines as needed'''
    
    def __init__(self):
        self._known_vaccine_list = []

    def load_vaccine_info(self, raw_file):
        '''Loads data file with all known vaccine information'''
        vax_info = json.loads(raw_file)
        for vax in vax_info['known_vaccines']:
            v = Vaccine.load_from_json(vax)
            self._known_vaccine_list.append(v)

    def get_vaccine_by_fhir_code(self, wanted_fhir_code):
        '''Walks the vaccine list, and returns vaccine obj based off FHIR'''

        for vaccine in self._known_vaccine_list:
            for fhir_code in vaccine.fhir_codes:
                if fhir_code == wanted_fhir_code:
                    return vaccine

        raise ValueError("Unknown vaccine")

    def get_vaccine_by_identifer(self, identifer):
        '''Gets a vaccine by the identifer in the JSON file'''
        for vaccine in self._known_vaccine_list:
            if self.vaccine_identifier == identifer:
                return vaccine
        
        raise ValueError("Unknown vaccine")

class Vaccine(object):
    '''Base class for vaccines'''
    def __init__(self):
        self.vaccine_identifier = None
        self.number_of_doses = None
        self.recommended_minimum_days_between_doses = None
        self.fhir_codes = []

    def load_from_json(v):
        '''Deserailizes vaccine information from JSON file'''
        vax = Vaccine()
        vax.vaccine_identifier = v['vaccine_identifier']
        vax.number_of_doses = v['number_of_doses']
        vax.recommended_minimum_days_between_doses = \
            v['recommended_minimum_days_between_doses']
        vax.fhir_codes = v['fhir_codes']
        return vax


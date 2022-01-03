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

import unittest

from datetime import datetime

import json
import vaksina.fhir_parser as fp
import vaksina.vaccines as vac

TEST_DATA_SHC = 'tests/data/shc/'
TEST_DATA_FHIR = 'tests/data/fhir/'

TEST_OFFICIAL_DATA_ROOT = TEST_DATA_SHC + 'official/'

VACCINE_INFO = 'tests/data/vaccine_info.json'

# Example test file 2 doesn't have any patient data in it
TEST_EXAMPLE_PATIENT = TEST_DATA_FHIR + 'patient_data.json'
TEST_EXAMPLE_IMMUNIZATION = TEST_DATA_FHIR + 'immunization_data.json'

TEST_DATA_EXAMPLE_00_FILE = TEST_DATA_SHC + 'example-00-a-fhirBundle.json'
TEST_DATA_EXAMPLE_02_FILE = TEST_DATA_SHC + 'example-02-a-fhirBundle.json'
TEST_DATA_EXAMPLE_03_FILE = TEST_DATA_SHC + 'example-03-a-fhirBundle.json'

class TestFHIRParser(unittest.TestCase):
    '''Basic test skeleton'''
    def setUp(self):
        '''Do test setup stuff'''
        self.vaccine_mgr = vac.VaccineInfoManager()
        with open(VACCINE_INFO) as f:
            self.vaccine_mgr.load_vaccine_info(f.read())

    def tearDown(self):
        '''If teardown is needed'''
        pass

    def test_parse_person_record(self):
        '''Tests if how we handle a Person entry'''
        fhir_parser = fp.FHIRParser(self.vaccine_mgr)

        with open(TEST_EXAMPLE_PATIENT) as f:
            json_parse = json.loads(f.read())

        patient = fhir_parser.parse_person_record(json_parse)

        # Check that we have valid information
        #
        # names is a list because FHIR can have multiple
        # patients in a given record, and I don't want to
        # blow unexpectedly

        comparsion_time = datetime.fromisoformat("1951-01-20")
        self.assertEqual(len(patient.names), 1)
        self.assertEqual(patient.names[0], "John B. Anyperson")
        self.assertEqual(patient.dob, comparsion_time)

    def test_parse_immunization_record(self):
        '''Tests that the test environment exists'''
        fhir_parser = fp.FHIRParser(self.vaccine_mgr)

        with open(TEST_EXAMPLE_IMMUNIZATION) as f:
            json_parse = json.loads(f.read())

        i = fhir_parser.parse_immunization_record(json_parse)
        issurance_date_test = datetime.fromisoformat("2021-01-01")

        self.assertEqual(i.vaccine_administered.vaccine_identifier, "MODERNA")
        self.assertEqual(i.date_given, issurance_date_test)
        self.assertEqual(i.lot_number, '0000001')
        self.assertEqual(i._shc_parent_object, 'resource:0')

    def parse_bundle_to_persons(self):
        '''Test parsing a decoding of a full FHIR bundle'''
        pass

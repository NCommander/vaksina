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

import json
import unittest
from datetime import datetime

import vaksina.fhir_parser as fp
import vaksina.vaccines as vac

TEST_DATA_SHC = "tests/data/shc/"
TEST_DATA_FHIR = "tests/data/fhir/"

TEST_OFFICIAL_DATA_ROOT = TEST_DATA_SHC + "official/"

VACCINE_INFO = "tests/data/vaccine_info.json"

# Example test file 2 doesn't have any patient data in it
TEST_PATIENT = TEST_DATA_FHIR + "patient_data.json"
TEST_IMMUNIZATION = TEST_DATA_FHIR + "immunization_data.json"
TEST_BUNDLE_VACCINE_STATUS_ENTERED_IN_ERROR = (
    TEST_DATA_FHIR + "bundle_vaccine_status_entered_in_error.json"
)
TEST_IMMUNIZATION_UNKNOWN_SYSTEM = (
    TEST_DATA_FHIR + "immunization_data_unknown_system.json"
)
TEST_BUNDLE_WITH_EXTRA_DATA = TEST_DATA_FHIR + "bundle_with_extra_data.json"
TEST_BUNDLE_DANGLING_REFERENCE = TEST_DATA_FHIR + "bundle_dangling_reference.json"
TEST_BUNDLE_MULTIPLE_PEOPLE = TEST_DATA_FHIR + "bundle_multiple_people.json"
TEST_BUNDLE_URL_COLLISION = TEST_DATA_FHIR + "bundle_url_collision.json"

# Example test file 2 doesn't have any patient data in it
TEST_DATA_EXAMPLE_00_FILE = TEST_DATA_SHC + "official/example-00-a-fhirBundle.json"
TEST_DATA_EXAMPLE_01_FILE = TEST_DATA_SHC + "official/example-01-a-fhirBundle.json"
TEST_DATA_EXAMPLE_02_FILE = TEST_DATA_SHC + "official/example-02-a-fhirBundle.json"
TEST_DATA_EXAMPLE_03_FILE = TEST_DATA_SHC + "official/example-03-a-fhirBundle.json"


class TestFHIRParser(unittest.TestCase):
    """Basic test skeleton"""

    def validate_jane_c_anyperson(self, p):
        """This is the test data from official example 01"""
        comparsion_dob = datetime.fromisoformat("1961-01-20")

        self.assertEqual(len(p.names), 1)
        self.assertEqual(p.names[0], "Jane C. Anyperson")
        self.assertEqual(p.dob, comparsion_dob)
        self.assertEqual(len(p.immunizations), 2)

        comparsion_date_1 = datetime.fromisoformat("2021-01-01")

        if p.immunizations[0].date_given == comparsion_date_1:
            first_shot = p.immunizations[0]
            second_short = p.immunizations[1]
        else:
            second_short = p.immunizations[0]
            first_shot = p.immunizations[1]

        self.assertEqual(
            first_shot.vaccine_administered.vaccine_identifier, "PFIZER_COMIRNATY"
        )
        self.assertEqual(first_shot.lot_number, "0000002")

        self.assertEqual(
            second_short.vaccine_administered.vaccine_identifier, "PFIZER_COMIRNATY"
        )
        self.assertEqual(second_short.lot_number, "0000008")

    def validate_john_b_anyperson(self, p):
        """Validate John from Example 0"""
        comparsion_dob = datetime.fromisoformat("1951-01-20")

        self.assertEqual(len(p.names), 1)
        self.assertEqual(p.names[0], "John B. Anyperson")
        self.assertEqual(p.dob, comparsion_dob)
        self.assertEqual(len(p.immunizations), 2)

        comparsion_date_1 = datetime.fromisoformat("2021-01-01")

        if p.immunizations[0].date_given == comparsion_date_1:
            first_shot = p.immunizations[0]
            second_short = p.immunizations[1]
        else:
            second_short = p.immunizations[0]
            first_shot = p.immunizations[1]

        self.assertEqual(first_shot.vaccine_administered.vaccine_identifier, "MODERNA")
        self.assertEqual(first_shot.lot_number, "0000001")

        self.assertEqual(
            second_short.vaccine_administered.vaccine_identifier, "MODERNA"
        )
        self.assertEqual(second_short.lot_number, "0000007")

    def setUp(self):
        """Do test setup stuff"""
        self.vaccine_mgr = vac.VaccineInfoManager()
        with open(VACCINE_INFO) as f:
            self.vaccine_mgr.load_vaccine_info(f.read())

    def tearDown(self):
        """If teardown is needed"""
        pass

    def test_parse_person_record(self):
        """Tests if how we handle a Person entry"""
        fhir_parser = fp.FHIRParser(self.vaccine_mgr)

        with open(TEST_PATIENT) as f:
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

    def test_parse_person_record(self):
        """Tests if how we handle a Person entry"""
        fhir_parser = fp.FHIRParser(self.vaccine_mgr)

        with open(TEST_IMMUNIZATION) as f:
            json_parse = json.loads(f.read())

        with self.assertRaises(ValueError):
            fhir_parser.parse_person_record(json_parse)

    def test_parse_immunization_record(self):
        """Tests decoding FHIR Immunization Record"""
        fhir_parser = fp.FHIRParser(self.vaccine_mgr)

        with open(TEST_IMMUNIZATION) as f:
            json_parse = json.loads(f.read())

        i = fhir_parser.parse_immunization_record(json_parse)
        issurance_date_test = datetime.fromisoformat("2021-01-01")

        self.assertEqual(i.vaccine_administered.vaccine_identifier, "MODERNA")
        self.assertEqual(i.date_given, issurance_date_test)
        self.assertEqual(i.lot_number, "0000001")
        self.assertEqual(i._shc_parent_object, "resource:0")

    def test_parse_immunization_record_unknown_system(self):
        """Tests graceful exit if we have unknown vaccine coding"""
        fhir_parser = fp.FHIRParser(self.vaccine_mgr)

        with open(TEST_IMMUNIZATION_UNKNOWN_SYSTEM) as f:
            json_parse = json.loads(f.read())

        with self.assertRaises(ValueError):
            i = fhir_parser.parse_immunization_record(json_parse)

    def test_immunization_parse_with_non_immunization(self):
        """Tests graceful exit if we have unknown vaccine coding"""
        fhir_parser = fp.FHIRParser(self.vaccine_mgr)

        with open(TEST_DATA_EXAMPLE_00_FILE) as f:
            json_parse = json.loads(f.read())

        with self.assertRaises(ValueError):
            i = fhir_parser.parse_immunization_record(json_parse)

    def test_incomplete_immunization_records_are_not_handled(self):
        """Test that logged in error or similar case is not counted"""
        fhir_parser = fp.FHIRParser(self.vaccine_mgr)

        with open(TEST_BUNDLE_VACCINE_STATUS_ENTERED_IN_ERROR) as f:
            json_parse = json.loads(f.read())
        p = fhir_parser.parse_bundle_to_persons(json_parse)[0]

        self.assertEqual(len(p.immunizations), 1)

    def test_fhir_bunder_with_additional_sections(self):
        """Test that we gracefully handle FHIR with additional sections"""
        fhir_parser = fp.FHIRParser(self.vaccine_mgr)

        with open(TEST_BUNDLE_WITH_EXTRA_DATA) as f:
            json_parse = json.loads(f.read())

        p_list = fhir_parser.parse_bundle_to_persons(json_parse)

        self.assertEqual(len(p_list), 1)
        p = p_list[0]
        comparsion_dob = datetime.fromisoformat("1951-01-20")

        self.assertEqual(len(p.names), 1)
        self.assertEqual(p.names[0], "John B. Anyperson")
        self.assertEqual(p.dob, comparsion_dob)
        self.assertEqual(len(p.immunizations), 2)

    def test_fhir_bunder_non_bundle(self):
        """Test that we only accept bundles correctly"""
        fhir_parser = fp.FHIRParser(self.vaccine_mgr)

        with open(TEST_IMMUNIZATION) as f:
            json_parse = json.loads(f.read())

        with self.assertRaises(ValueError):
            fhir_parser.parse_bundle_to_persons(json_parse)

    def test_properly_handle_dangling_reference(self):
        """Test that we only accept bundles correctly"""
        fhir_parser = fp.FHIRParser(self.vaccine_mgr)

        with open(TEST_BUNDLE_DANGLING_REFERENCE) as f:
            json_parse = json.loads(f.read())

        with self.assertRaises(ValueError):
            fhir_parser.parse_bundle_to_persons(json_parse)

    def test_parse_multiple_people_in_bundle(self):
        """Test decoding official sample 00 fhir bundle"""
        fhir_parser = fp.FHIRParser(self.vaccine_mgr)

        with open(TEST_BUNDLE_MULTIPLE_PEOPLE) as f:
            json_parse = json.loads(f.read())
        p_list = fhir_parser.parse_bundle_to_persons(json_parse)
        self.assertEqual(len(p_list), 2)

        print(p_list[0].names[0])
        print(p_list[1].names[0])

        if p_list[0].names[0] == "Jane C. Anyperson":
            jane_p = p_list[0]
            john_p = p_list[1]
        else:
            jane_p = p_list[1]
            john_p = p_list[0]

        self.validate_john_b_anyperson(john_p)
        self.validate_jane_c_anyperson(jane_p)

    def test_proepr_bailout_with_duplicate_url(self):
        """Test decoding official sample 00 fhir bundle"""
        fhir_parser = fp.FHIRParser(self.vaccine_mgr)

        with open(TEST_BUNDLE_URL_COLLISION) as f:
            json_parse = json.loads(f.read())

        with self.assertRaises(ValueError):
            fhir_parser.parse_bundle_to_persons(json_parse)

    ## Down here, we test that we can successfully read/load official
    ## specification data. Example 2 is expected to fail as is it is
    ## not a valid COVID19 card

    def test_parse_official_example_00(self):
        """Test decoding official sample 00 fhir bundle"""
        fhir_parser = fp.FHIRParser(self.vaccine_mgr)

        with open(TEST_DATA_EXAMPLE_00_FILE) as f:
            json_parse = json.loads(f.read())
        p_list = fhir_parser.parse_bundle_to_persons(json_parse)

        self.assertEqual(len(p_list), 1)
        p = p_list[0]
        self.validate_john_b_anyperson(p)

    def test_parse_official_example_01(self):
        """Test decoding official sample 01 fhir bundle"""
        fhir_parser = fp.FHIRParser(self.vaccine_mgr)

        with open(TEST_DATA_EXAMPLE_01_FILE) as f:
            json_parse = json.loads(f.read())
        p_list = fhir_parser.parse_bundle_to_persons(json_parse)

        self.assertEqual(len(p_list), 1)
        p = p_list[0]
        self.validate_jane_c_anyperson(p)

    def test_parse_official_example_02(self):
        """Test decoding official sample 02 fhir bundle

        NOTE: expected 0 result because no patient data"""
        fhir_parser = fp.FHIRParser(self.vaccine_mgr)

        with open(TEST_DATA_EXAMPLE_02_FILE) as f:
            json_parse = json.loads(f.read())
        p_list = fhir_parser.parse_bundle_to_persons(json_parse)

        self.assertEqual(len(p_list), 0)

    def test_parse_official_example_03(self):
        """Test decoding official sample 03 fhir bundle"""
        fhir_parser = fp.FHIRParser(self.vaccine_mgr)

        with open(TEST_DATA_EXAMPLE_03_FILE) as f:
            json_parse = json.loads(f.read())
        p_list = fhir_parser.parse_bundle_to_persons(json_parse)

        self.assertEqual(len(p_list), 1)
        p = p_list[0]
        comparsion_dob = datetime.fromisoformat("1960-04-22")

        self.assertEqual(len(p.names), 1)
        self.assertEqual(p.names[0], "Johnny Revoked")
        self.assertEqual(p.dob, comparsion_dob)
        self.assertEqual(len(p.immunizations), 2)

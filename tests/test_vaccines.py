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

import vaksina.vaccines as vac

VACCINE_INFO = "tests/data/vaccine_info.json"


def get_vac_manager():
    vac_mgr = vac.VaccineInfoManager()
    with open(VACCINE_INFO) as f:
        vac_mgr.load_vaccine_info(f.read())

    return vac_mgr


class TestVaccineManager(unittest.TestCase):
    """Basic test skeleton"""

    def setUp(self):
        """Do test setup stuff"""
        pass

    def tearDown(self):
        """If teardown is needed"""
        pass

    def test_load_vaccine_info(self):
        """Test loading vaccine information database"""
        vac_mgr = get_vac_manager()

        self.assertEqual(len(vac_mgr._known_vaccine_list), 7)

    def test_vaccine_by_fhir_code_single(self):
        """Ensures that we can properly load vaccine by single FHIR code"""

        vac_mgr = get_vac_manager()

        # We want to test multiple cases, first
        # handle simple test of vaccine with only
        # one code

        vaccine = vac_mgr.get_vaccine_by_fhir_code(207)
        self.assertIsNotNone(vaccine)
        self.assertEqual(vaccine.vaccine_identifier, "MODERNA")

    def test_vaccine_by_fhir_code_multiple(self):
        """Ensures that we can properly load vaccine with multiple codes"""

        vac_mgr = get_vac_manager()

        # ​Pfizer in our test set has multiple codes, we need
        # to retrieve it multiple ways, but make sure it all
        # points to the same thing

        vaccine1 = vac_mgr.get_vaccine_by_fhir_code(208)
        self.assertIsNotNone(vaccine1)
        self.assertEqual(vaccine1.vaccine_identifier, "PFIZER_COMIRNATY")

        # Let's try and get via another code method
        vaccine2 = vac_mgr.get_vaccine_by_fhir_code(217)
        self.assertIsNotNone(vaccine2)
        self.assertEqual(vaccine2.vaccine_identifier, "PFIZER_COMIRNATY")

        self.assertEqual(vaccine1, vaccine2)

    def test_vaccine_by_fhir_code_not_found(self):
        """Test handling FHIR code not found"""
        vac_mgr = get_vac_manager()
        with self.assertRaises(ValueError):
            vac_mgr.get_vaccine_by_fhir_code(1)

    def test_get_vaccine_by_identifier(self):
        """Test if we can find a given vaccine by identifier"""
        vac_mgr = get_vac_manager()
        vaccine = vac_mgr.get_vaccine_by_identifier("MODERNA")
        self.assertIsNotNone(vaccine)
        self.assertEqual(vaccine.vaccine_identifier, "MODERNA")

    def test_get_vaccine_by_identifier_bad_identifier(self):
        """Test if we can find a given vaccine with bad identifier"""
        vac_mgr = get_vac_manager()
        with self.assertRaises(ValueError):
            vaccine = vac_mgr.get_vaccine_by_identifier("DOES NOT EXIST")

    def test_get_vaccines_by_doses_1(self):
        """Test if we can retrieve number of vaccines via dose"""
        vac_mgr = get_vac_manager()
        vac_list = vac_mgr.get_vaccines_by_required_doses(1)
        self.assertEqual(len(vac_list), 1)

    def test_get_vaccines_by_doses_2(self):
        """Test if we can retrieve number of vaccines via dose"""
        vac_mgr = get_vac_manager()
        vac_list = vac_mgr.get_vaccines_by_required_doses(2)

        # Five is correct, because we have 7 in the test data
        # 1 with one dose, one with -1 (aka unknown) and five
        # with 2 doses.

        self.assertEqual(len(vac_list), 5)

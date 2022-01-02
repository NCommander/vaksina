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

'''So this module exists because the reference implementations parse
that can handle the SMART FHIRs data is in development, poorly documented
and to quote the *official* SMARTS specification, you can hack it 
together from a bunch of freestandin libraries. Since there's no 
validated turnkey solution, there's going to be a lot of health
providers that will DIY it, and do it wrong.

So, unfortunately, we're going to have to parse this ourselves.

This is going to suck ~ NCommander'''

import json
from datetime import datetime

import vaksina as v

class FHIRParser(object):
    # {'lotNumber': '0000001',
    #  'occurrenceDateTime': '2021-01-01',
    #  'patient': {'reference': 'resource:0'},
    #  'performer': [{'actor': {'display': 'ABC General Hospital'}}],
    #  'resourceType': 'Immunization',
    #  'status': 'completed',
    #  'vaccineCode': {'coding': [{'code': '207',
    #                              'system': 'http://hl7.org/fhir/sid/cvx'}]}}

    @staticmethod
    def parse_immunization_record(resource):
        '''Confirms FHIR Immunization record to object'''

        # It's possible that multiple vaccines can be given in
        # single day. This isn't done for COVID per say, but
        # because FIRS is a general purpose specification, we
        # should handle this, especially if there are future
        # multishot COVID vaccinations that *are* given at later
        # point, because data structures are important

        immunizations = []
        vaccine_code = resource['vaccineCode']
        for code in vaccine_code['coding']:
            if code['system'] != 'http://hl7.org/fhir/sid/cvx':
                # Unknown coding
                print("ERROR: unknown vaccine coding system")
                continue

            immunization = v.Immunization()
            immunization.lot_number = resource['lotNumber']
            immunization.date_given = datetime.fromisoformat(
                resource['occurrenceDateTime'])
            immunization.vaccine_administered = code['code']
            immunization._shc_parent_object = resource['patient']['reference']

            # so register the specific vaccine, right now, just handle the "code"
            immunizations.append(immunization)

        return immunizations

    # {
    #   "resourceType": "Patient",
    #   "name": [
    #     {
    #       "family": "Anyperson",
    #       "given": [
    #         "John",
    #         "B."
    #       ]
    #     }
    #   ],
    #   "birthDate": "1951-01-20"
    # }

    @staticmethod
    def parse_person_record(resource):
        '''Converts FHIR data into People Records'''

        person = v.Person()

        # A person can have multiple names if they got married,
        # transitioned, etc. We need to list all names to handle
        # validation correctly since their COVID card may not 100%
        # match the government ID

        for name in resource['name']:
            person_name = ""
            for given_name in name['given']:
                person_name = person_name + given_name + " "
            person_name = person_name + name['family']
            person.name.append(person_name)

        person.dob = datetime.fromisoformat(resource['birthDate'])

        return person

    @staticmethod
    def parse_bundle_to_persons(bundle):
        # First, we need to sort, and create top level records

        if bundle['resourceType'] != "Bundle":
            raise ValueError("must be a FHIR Bundle")

        # So we need to map each type of resource to
        # is URI to build the end result. uri fields are
        # freeform, so yay ...

        person_uris = dict()

        immunizations = []

        for entry in bundle['entry']:
            # Determine what type of resource we're looking at
            resource = entry['resource']

            if resource['resourceType'] == 'Patient':
                person = FHIRParser.parse_person_record(resource)
                person_uris[entry['fullUrl']] = person

                # print(vars(person))
            elif resource['resourceType'] == 'Immunization':
                # ok, special case here, we only handle an immunizaiton
                # if it was actually completed, otherwise, disregard
                if resource['status'] != 'completed':
                    # FIXME: check this
                    print("FIXME: handle non-complete status")
                    continue

                immunizations = immunizations + \
                    FHIRParser.parse_immunization_record(resource)
            else:
                # its a record type we don't know/understand
                print("FIXME: LOGME, UNKNOWN RECORD")

        # Assiocate immunity records with patient records
        for immunization in immunizations:
            if immunization._shc_parent_object not in person_uris:
                raise ValueError(
                    "ERROR: DANGLING REFERENCE TO SHC PARENT OBJECT")
            person_uris[immunization._shc_parent_object].immunizations.append(
                immunization)
        

        return list(person_uris.values())

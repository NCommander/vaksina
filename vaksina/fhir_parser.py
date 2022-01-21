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

"""So this module exists because the reference implementations parse
that can handle the SMART FHIRs data is in development, poorly documented
and to quote the *official* SMARTS specification, you can hack it 
together from a bunch of freestandin libraries. Since there's no 
validated turnkey solution, there's going to be a lot of health
providers that will DIY it, and do it wrong.

So, unfortunately, we're going to have to parse this ourselves.

This is going to suck ~ NCommander"""

import json
from datetime import datetime

import vaksina as v
import vaksina.vaccines as vc


class FHIRParser(object):
    def __init__(self, vaccine_mgr):
        self.vaccine_mgr = vaccine_mgr

    # {'lotNumber': '0000001',
    #  'occurrenceDateTime': '2021-01-01',
    #  'patient': {'reference': 'resource:0'},
    #  'performer': [{'actor': {'display': 'ABC General Hospital'}}],
    #  'resourceType': 'Immunization',
    #  'status': 'completed',
    #  'vaccineCode': {'coding': [{'code': '207',
    #                              'system': 'http://hl7.org/fhir/sid/cvx'}]}}

    def parse_immunization_records(self, resource):
        """Confirms FHIR Immunization record to object"""

        # It's possible that multiple vaccines can be given in
        # single day. This isn't done for COVID per se, but
        # because FHIR is a general purpose specification, we
        # should handle this, especially if there are future
        # multishot COVID vaccinations that *are* given at later
        # point, because data structures are important

        if resource["resourceType"] != "Immunization":
            raise ValueError("Non-immunization record passed")

        immunizations = []
        vaccine_code = resource["vaccineCode"]
        for code in vaccine_code["coding"]:
            if code["system"] != "http://hl7.org/fhir/sid/cvx":
                raise ValueError("Unknown vaccine coding system")

            immunization = v.Immunization()
            immunization.lot_number = resource["lotNumber"]
            immunization.date_given = datetime.fromisoformat(
                resource["occurrenceDateTime"]
            )

            # So depending on the code we get determines the type
            # of vaccine that was issued
            immunization.vaccine_administered = (
                self.vaccine_mgr.get_vaccine_by_fhir_code(int(code["code"]))
            )

            immunization._shc_parent_object = resource["patient"]["reference"]

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
        """Converts FHIR data into People Records

        NOTE: Currently only data related to completed vaccinations
        is considered by this function. This may change on a later
        date if needed.

        To be specific, any immunization record that is not 'completed'
        is silently discarded.
        """

        if resource["resourceType"] != "Patient":
            raise ValueError("Non-patient record passed")

        person = v.Person()

        # A person can have multiple names if they got married,
        # transitioned, etc. We need to list all names to handle
        # validation correctly since their COVID card may not 100%
        # match the government ID

        for name in resource["name"]:
            person_name = ""
            for given_name in name["given"]:
                person_name = person_name + given_name + " "
            person_name = person_name + name["family"]
            person.names.append(person_name)

        person.dob = datetime.fromisoformat(resource["birthDate"])

        return person

    def parse_bundle_to_persons(self, bundle):
        # First, we need to sort, and create top level records

        if bundle["resourceType"] != "Bundle":
            raise ValueError("must be a FHIR Bundle")

        # So we need to map each type of resource to
        # is URI to build the end result. uri fields are
        # freeform, so yay ...

        person_uris = dict()
        seen_full_urls = set()

        # URLs in SMART Health Cards are freeform, and are used to
        # link objects together. It's possible in a case of multiple
        # people on a given card that a URL duplication could be used
        # as an attack. As a safeguard, load all URLs as seen, and
        # bail out *if* we get a duplicate

        immunizations = []

        for entry in bundle["entry"]:
            # Determine what type of resource we're looking at
            resource = entry["resource"]
            if entry["fullUrl"] in seen_full_urls:
                raise ValueError("Duplicate URL Detected")

            seen_full_urls.add(entry["fullUrl"])

            if resource["resourceType"] == "Patient":
                person = self.parse_person_record(resource)
                person_uris[entry["fullUrl"]] = person

                # print(vars(person))
            elif resource["resourceType"] == "Immunization":
                # ok, special case here, we only handle an immunization
                # if it was actually completed, otherwise, disregard
                if resource["status"] != "completed":
                    # FHIR specification notes that status can be one
                    # of the following values
                    #
                    # - completed
                    # - entered-in-error
                    # - not-done
                    #
                    # As such, we can completely disregard any not completed
                    # records as they will never count towards determine
                    # vaccination status
                    # FIXME: debug logger
                    continue

                immunizations.extend(self.parse_immunization_records(resource))

            # Coverage isn't properly handling an else class here
            #
            # IF we get here, then we're got an unknown record and ignoring
            # if
            # FIXME: Implement debug logger

        # Associate immunity records with patient records
        for immunization in immunizations:
            if immunization._shc_parent_object not in person_uris:
                raise ValueError("ERROR: DANGLING REFERENCE TO SHC PARENT OBJECT")
            person_uris[immunization._shc_parent_object].immunizations.append(
                immunization
            )

        return list(person_uris.values())

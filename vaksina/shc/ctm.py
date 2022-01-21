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

import base64
import json
import re
import zlib

import vaksina
import vaksina.fhir_parser as f
import vaksina.shc.key_management as km

from jose import jwk, jws
from jose.constants import ALGORITHMS


class ShcCardTypeManager(vaksina.CardManager):
    """Handles management aspects for all SMART Health Card data"""

    def __init__(self, vaccine_mgr):
        self._key_management = km.KeyManagement()
        self._vaccine_mgr = vaccine_mgr
        self._fhir_parser = f.FHIRParser(vaccine_mgr)

    def parse_card_data(self, card_data, allow_bad_sig=False):
        """Parses the direct output of a QR code to objects"""
        if card_data[0:5] != "shc:/":
            raise Exception("Not a SHC QR code")

        # based off marcan2020.medium.com/reversing-smart-health-cards-e765157fae9
        parts = re.findall("..", card_data[5:])
        b64_data = ""
        for p in parts:
            b64_data += chr(int(p) + 45)

        # So, to validate the turducken (that is say SHC data)
        # we need to unpack without checking the signature. Then
        # we can get the iss field, try and get that key from the
        # database, and then validate it

        unvalidated_vac_header = jws.get_unverified_header(b64_data)
        unvalidated_vac_data = jws.get_unverified_claims(b64_data)
        raw_unsigned_vax_data = str(
            zlib.decompress(bytes(unvalidated_vac_data), wbits=-15), "utf-8"
        )

        unsigned_vax_data = json.loads(raw_unsigned_vax_data)

        # So, fingers crossed, we have these key ids
        signing_keys = self._key_management.get_keys_for_key_id(
            unsigned_vax_data["iss"]
        )

        if signing_keys is None:
            raise Exception("Unknown Issuer" + unsigned_vax_data["iss"])

        declared_key = signing_keys.get(unvalidated_vac_header["kid"])
        if declared_key is None:
            raise Exception(
                "No valid signing key found for" + unvalidated_vac_header["kid"]
            )

        verified_data = jws.verify(b64_data, declared_key, ALGORITHMS.ES256)
        vax_data = json.loads(str(zlib.decompress(bytes(verified_data), wbits=-15), "utf-8"))

        # Assuming we got this far, ensure that this card complies with
        # the specifications we *assume* exist*
        is_health_card = False
        is_covid19_card = False
        is_immunization_card = False

        for card_type in vax_data["vc"]["type"]:
            if card_type == "https://smarthealth.cards#health-card":
                is_health_card = True
            elif card_type == "https://smarthealth.cards#immunization":
                is_immunization_card = True
            elif card_type == "https://smarthealth.cards#covid19":
                is_covid19_card = True

        if (
            is_health_card is False
            or is_covid19_card is False
            or is_immunization_card is False
        ):
            raise ValueError("Not a supported type of card")

        # Now we need to decode the FHIR data
        c = vaksina.Card()
        c.card_type = "smart_health_card"
        c.issued_by = vax_data["iss"]
        persons = self._fhir_parser.parse_bundle_to_persons(
            vax_data["vc"]["credentialSubject"]["fhirBundle"]
        )
        for person in persons:
            c.add_person(person)
        return c

    def import_signing_key(self, key_id, key_data):
        """Imports a given signing key"""
        self._key_management.enroll_key_for_key_id(key_id, key_data)

    def import_key_database(self, keydb):
        """Import the key database"""
        parsed_keys = json.loads(keydb)
        for iss, keys in parsed_keys.items():
            self.import_signing_key(iss, keys)

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

import re
import base64
import json

import zlib

from jose import jwk, jws
from jose.constants import ALGORITHMS

import vaksina
import vaksina.shc.key_management as km


class ShcCardTypeManager(vaksina.CardManager):
    '''Handles management aspects for all SMART Health Card data'''
    _key_management = None

    def __init__(self):
        self._key_management = km.KeyManagement()

    def parse_card_data(self, card_data, allow_bad_sig=False):
        '''Parses the direct output of a QR code to objects'''
        if card_data[0:5] != 'shc:/':
            raise Exception("Not a SHC QR code")

        # based off marcan2020.medium.com/reversing-smart-health-cards-e765157fae9
        parts = re.findall('..', card_data[5:])
        b64_data = ""
        for p in parts:
            b64_data += chr(int(p) + 45)

        # Padd Base64 if needed
        padding_needed = len(b64_data) % 4
        if padding_needed != 0:
            for _ in range(padding_needed):
                b64_data += '='
        jwt_data = base64.urlsafe_b64decode(b64_data)

        # So, to validate the turducken (that is say SHC data)
        # we need to unpack without checking the signature. Then
        # we can get the iss field, try and get that key from the
        # database, and then validate it

        unvalidated_vac_header = jws.get_unverified_header(b64_data)
        unvalidated_vac_data = jws.get_unverified_claims(b64_data)
        raw_unsigned_vax_data = str(zlib.decompress(
            unvalidated_vac_data, wbits=-15), 'utf-8')

        unsigned_vax_data = json.loads(raw_unsigned_vax_data)

        # So, fingers crossed, we have these key ids
        signing_keys = self._key_management.get_keys_for_key_id(
            unsigned_vax_data['iss'])

        declared_key = signing_keys.get(unvalidated_vac_header['kid'])
        if declared_key is None:
            raise Exception("No valid signing key found")

        verified_data = jws.verify(b64_data, declared_key, ALGORITHMS.ES256)
        vax_data = json.loads(
            str(zlib.decompress(verified_data, wbits=-15), 'utf-8'))

        print(vax_data)

        #signing_key = unvalidated_vac_data['kid']

        # print(signing_key)
        # if signing_key not in valid_pubkeys:
        #    print("NOT A KNOWN KEY!")
        #    return

    def import_signing_key(self, key_id, key_data):
        '''Imports a given signing key'''
        self._key_management.enroll_key_for_key_id(key_id, key_data)

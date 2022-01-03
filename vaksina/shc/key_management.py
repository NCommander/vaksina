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
from jose import jwk, jws
from jose.constants import ALGORITHMS
from jose.exceptions import JWSError

class KeyManagement(object):
    '''Handles keeping track of all known SHC key signatures'''

    def __init__(self):
        '''Default initializer'''
        pass

    def get_keys_for_key_id(self, key_id):
        '''Returns all known keys for a given kid'''
        return self._key_storage.get(key_id, None)

    def enroll_key_for_key_id(self, key_id, keydata):
        '''Enrolls a key into the Key Management system'''
        loaded_key = KeyManagement._load_pubkey(keydata)

        keys = self._key_storage.get(key_id, None)

        if keys is None:
            self._key_storage[key_id] = loaded_key
        #else:
            #raise ValueError("Cowardly refusing to enroll duplicate iss keystore")

    def _load_pubkey(jwt_pubkey):
        '''Creates jose pubkey objects from JWT JSON'''

        # SHC says this is what must be used
        valid_keys = dict()

        # Specification allows multiple keys, so lets process them one by one
        for key in jwt_pubkey['keys']:
            if key['kty'] != 'EC':
                print("ERROR: Can't load non EC key")
                continue
            
            if key['use'] != 'sig':
                print("ERROR: key type not signature")
                continue

            if key['alg'] != 'ES256':
                print("ERROR: Not ES256 key!")
                continue

            if key['crv'] != 'P-256':
                print("ERROR: not the right type of curve")
                continue

            # make sure we have x and why
            if "x" not in key or "y" not in key:
                print("x/y cooridors not found!")
                continue

            if "d" in key:
                print("SUPER ERROR: SOMEONE LEFT THE PRIVATE KEY IN PLACE!")

            valid_keys[key['kid']] = jwk.construct(key, algorithm=ALGORITHMS.ES256)

        return valid_keys

    _key_storage = dict()

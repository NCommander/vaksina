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

"""
Handles utility functions, and other things that have any specific home
such as stuff relating to JWT signing or manipulation
"""

import json
import base64
import hashlib

def _generate_kid_for_jwk_dict(jwks_dict):
    """Generates KID token per RFC 7638
    
    Unfortunately, python-jose doesn't have a way to generate key IDs for a JWK
    according to RFC 7638, and its the only permissive licensed JWT library that
    has support for ECs out of the box. This only handles ECs as of right now

    This takes a raw JWK dict, so you can load JSON data and pass it straight in
    to get the KID if it isn't present in a given key set

    At the time of writing (2022-01-06), this function is only used in test code,
    it may be worth moving out of the base library ...
    """

    if jwks_dict['kty'] != "EC": 
        raise ValueError("only EC JWKs supported!")

    kid_base = {}
    kid_base['crv'] = jwks_dict['crv']
    kid_base['kty'] = jwks_dict['kty']
    kid_base['x'] = jwks_dict['x']
    kid_base['y'] = jwks_dict['y']
    json_serial = json.dumps(kid_base, sort_keys=True, separators=(',', ':'))
    sha256_hash = hashlib.sha256(json_serial.encode('utf-8')).digest()
    b64_hash = base64.urlsafe_b64encode(sha256_hash)
    return b64_hash.decode('utf-8').rstrip("=")

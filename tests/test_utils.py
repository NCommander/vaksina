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

from jose import jwk
from jose.constants import ALGORITHMS
import os

import vaksina.utils as u

dir_path = os.path.dirname(os.path.realpath(__file__)) + '/'

SHC_OFFICIAL_KEY = (
    dir_path + 'data/shc/official/keys/jwks.json'
)


class TestUtils(unittest.TestCase):
    """Tests misc utility functions"""

    def test_ec_kid_generation(self):
        """Tests key id generation per RFC 7638"""
        
        # Load in the reference key, and confirm that we can generate
        # the same kid for each key in that test set

        keys = {}
        with open(SHC_OFFICIAL_KEY) as f:
            raw_keys = json.loads(f.read())
            for raw_key in raw_keys['keys']:
                keys[raw_key['kid']] = jwk.construct(raw_key, algorithm=ALGORITHMS.ES256)
        
        # Check if we can recreate the key

        key_count = 0 # make sure we run on both keys
        for kid, key in keys.items():
            gen_kid = u._generate_kid_for_jwk_dict(key.to_dict())
            self.assertEqual(kid, gen_kid)
            key_count = key_count +1

        self.assertEqual(key_count, 2)

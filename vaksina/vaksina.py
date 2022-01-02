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

from enum import Enum
import json

from vaksina.card_manager import CardManager

import vaksina.shc.ctm as shc_ctm
import vaksina.vaccines


class Vaksina(object):
    '''Defines public API objects, and holds per instance state information'''
    _shc_ctm = None
    _vaccine_mgr = None

    def __init__(self):
        self._vaccine_mgr = vaksina.vaccines.VaccineManager()
        self._shc_ctm = shc_ctm.ShcCardTypeManager(self._vaccine_mgr)

    def load_vaccine_info(self, raw_file):
        '''Loads data file with all known vaccine information'''
        self._vaccine_mgr.load_vaccine_info(raw_file)

    def import_signing_key(self, card_type, key_id, key_data):
        '''Imports a key into the keystore'''

        if card_type == "shc":
            self._shc_ctm.import_signing_key(key_id, key_data)

    def parse_card_data(self, card_data):
        '''Parses inbound QR code data'''

        if card_data[0:5] == 'shc:/':
            return self._shc_ctm.parse_card_data(card_data)

        #  if we get here, no known way to handle it
        raise NotImplemented

    # Get vaccine data via method

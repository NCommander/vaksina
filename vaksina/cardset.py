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


class Cardset(object):
    """A cardset contains a set of scanned cards, and can be processed
    en-mass to handle validation results as a single top level result
    subtle for serialization and validation"""

    def __init__(self):
        self._cards = {}
        self._card_count = 0

    def add_card(self, card):
        """Adds a card to a cardset"""

        card_key = "card" + str(self._card_count)
        self._cards[card_key] = card
        self._card_count = self._card_count + 1

    def to_dict(self):
        """Convert cardset to dict for serialization"""
        card_content_dict = {}

        # FIXME: implement validation serialization
        for cardname, card in self._cards.items():
            card_content_dict[cardname] = card.to_dict()

        return card_content_dict

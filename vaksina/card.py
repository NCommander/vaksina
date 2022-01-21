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


class Card(object):
    """Represents a COVID-19 Card"""

    def __init__(self):
        self.card_type = None
        self.issued_by = None
        self.persons = {}
        self._person_count = 0

    def add_person(self, card):
        """Adds a person to the card"""
        person_key = "person" + str(self._person_count)
        self.persons[person_key] = card
        self._person_count = self._person_count + 1

    def to_dict(self):
        """Convert CardObject to dictionary for validation"""
        c_dict = {
            "card_type": self.card_type,
            "issued_by": self.issued_by
        }
        person_dict = {}

        for pkey, person in self.persons.items():
            person_dict[pkey] = person.to_dict()

        c_dict["persons"] = person_dict

        return c_dict

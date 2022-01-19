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

from datetime import datetime


class Person(object):
    def __init__(self):
        self.names = []
        """name is a list of names from the vaccination card

        At least in theory, it is possible for a SMART Heart Card, or
        others to list multiple names, as that is part of the FHIR standard

        As this was explained to me, this is primary intended for cases of people
        with multiple legal aliases. I am not certain if SHC other card would be
        *issued* like that, but its also a possibility, so in the hope to avoid
        a future refactor, this is handled as a list (unfortunately)
        """

        self.dob = None
        """Handles the date of birth for a given person

        Object held in Python DateTime format"""

        self.immunizations = []
        """Immunizations are vaksina.Immunization objects, formed as a list.

        Only completed vaccinations (that is status = "completed" in SHC, or similar
        in other cards) is included, since this is not intended as a general purpose
        health record tool, merely a validator for COVID-19 QR codes
        """

    def to_dict(self):
        """Serializes data to a dictionary for use in JSON, etc."""
        person_dict = {}
        person_dict["name"] = []
        for name in self.names:
            person_dict["name"].append(name)

        person_dict["dob"] = self.dob.strftime("%Y-%m-%d")
        person_dict["immunizations"] = []
        for immunization in self.immunizations:
            person_dict["immunizations"].append(immunization.to_dict())

        return person_dict

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

'''Handles various validator functions'''

class Validators(object):
    def __init__(self):
        pass

    def validator_osha_1910_501_rules(person):
        '''
        Determines valid vaccination status based off the OSHA
        1910.501 Standard.

        https://osha.gov/laws-regs/regulations/standardnumber/1910/1910.501

        To be fully vaccinated, an individual must meet the following
        
        If one shot vaccine is used (aka J&J) then:
          - 2 weeks must pass from administration date to current date

        Otherwise, in a two shot vaccine, the following rules apply
          - each vaccine must be admined 17 days apart with 4 day grace period
          - 2 weeks from the date of administration

        This standard does not account for any boosters in use.
        '''

        # Get immunizations for person
        immunizations = person.immunizations

        # Check if user has gotten a one shot vaccine
        
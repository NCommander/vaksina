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

"""Handles various validator functions"""

from datetime import datetime


# Check if user has gotten a one shot vaccine
def is_immunization_older_than_14_days(immunization):
    current_datetime = datetime.now()
    time_since = current_datetime - immunization.date_given
    if time_since.days > 14:
        return True
    return False


class ValidationResult(object):
    def __init__(self, validation_method, person):
        self.validation_method = validation_method
        self.person = person
        self.card_validation_status = "invalid"
        self.validation_errors = None

    def to_dict(self):
        vr_dict = {
            "validation_method": self.validation_method,
            "results": {
                self.person.names[0]
                if len(self.person.names) == 1 else
                "[ " + '; '.join(self.person.names) + " ]":
                    self.card_validation_status
                    if self.card_validation_status != "failed" or self.validation_errors is None
                    else self.validation_errors
            }
        }
        return vr_dict


class Validators(object):
    def __init__(self, v, cardset):
        self.v_obj = v
        self.cardset = cardset
        self.validations = []

    def validator_osha_1910_501_rules(self, person):
        """
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
        """

        vacinfo = self.v_obj.get_vaccine_manager()
        one_shot_vaccines = vacinfo.get_vaccines_by_required_doses(1)
        two_shot_vaccines = vacinfo.get_vaccines_by_required_doses(2)

        result = ValidationResult("osha_1910_501", person)

        # Get immunizations for person
        immunizations = person.immunizations

        # Handle the simplier one shot test case now ...
        for immunization in immunizations:
            for vaccine in one_shot_vaccines:
                if immunization.is_vaccine(vaccine):
                    if is_immunization_older_than_14_days(immunization):
                        result.card_validation_status = "success"
                        self.validations.append(result)
                        return

        # So validate the two shot test cases now ...
        person_two_vaccine_dict = dict()

        # both vaccines need to match per current US protocols
        for immunization in immunizations:
            for vaccine in two_shot_vaccines:
                if immunization.is_vaccine(vaccine):
                    shots = person_two_vaccine_dict.get(vaccine.vaccine_identifier, [])
                    shots.append(immunization)
                    person_two_vaccine_dict[vaccine.vaccine_identifier] = shots

        # Now that we have a set of vaccines, we need to determine if
        # any of these shoots meet criteria
        #
        # FIXME: does not work properly with boosters

        for vaccine_series in person_two_vaccine_dict.values():
            # We need two shots to consider this
            if len(vaccine_series) < 2:
                continue

            # Determine oldest and newest shot
            oldest_vaccination = vaccine_series[0]
            newest_vaccination = vaccine_series[0]

            for vaccine in vaccine_series:
                if oldest_vaccination.date_given > vaccine.date_given:
                    oldest_vaccination = vaccine
                if newest_vaccination.date_given < vaccine.date_given:
                    newest_vaccination = vaccine

                # FIXME: not considering 17 rule from OSHA because that
                # is the duty of the healthcare provider
                if is_immunization_older_than_14_days(newest_vaccination):
                    result.card_validation_status = "success"
                    self.validations.append(result)
                    return result

        result.card_validation_status = "failed"
        self.validations.append(result)
        return result

    def to_dict(self):
        v_dict = {
            "cards": self.cardset.to_dict(),
            "validations": [val.to_dict() for val in self.validations]
        }
        return v_dict

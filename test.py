#!/usr/bin/python3

import json
import vaksina
import vaksina.shc as shc
import vaksina.shc.key_management as km
from vaksina.vaksina import Vaksina
from vaksina.validators import Validators

def main():
    v = Vaksina()

    with open("jwks.json", "r") as f:
        jwt_json = json.loads(f.read())
        v.import_signing_key("shc",
                             "https://spec.smarthealth.cards/examples/issuer",
                             jwt_json)

    with open("data/shc_keys.json", "r") as f:
        v.import_key_database('shc', f.read())

    #with open("nj-jwks.json", "r") as f:
    #    jwt_json = json.loads(f.read())
    #    v.import_signing_key("shc",
    #        "https://docket.care/nj",
    #        jwt_json
    #    )

    with open("data/vaccine_info.json") as f:
        v.load_vaccine_info(f.read())

    vax_data = None
    with open("example-01-f-qr-code-numeric-value-0.txt", "r") as f:
        vax_data = v.parse_card_data(f.read())

    #for i in vax_data[0].immunizations:
    #    print(vars(i))
    #    print(vars(i.vaccine_administered))

    print(Validators.validator_osha_1910_501_rules(v, vax_data[0]))


    # KeyManager = km.KeyManagement()

    # with open("jwks.json", "r") as f:
    #     jwt_json = json.loads(f.read())

    #     KeyManager.enroll_key_for_key_id(
    #         "https://spec.smarthealth.cards/examples/issuer",
    #         jwt_json
    #     )

    # with open("nj-jwks.json", "r") as f:
    #     KeyManager.enroll_key_for_key_id(
    #         "https://docket.care/nj",
    #         jwt_json
    #     )

    # import pprint
    # pprint.pprint(km.KeyManagement._key_storage)


if __name__ == '__main__':
    main()

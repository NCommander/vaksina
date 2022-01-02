#!/usr/bin/python3

import json
import vaksina
import vaksina.shc as shc
import vaksina.shc.key_management as km
from vaksina.vaksina import Vaksina


def main():
    v = Vaksina()

    with open("jwks.json", "r") as f:
        jwt_json = json.loads(f.read())
        v.import_signing_key("shc",
                             "https://spec.smarthealth.cards/examples/issuer",
                             jwt_json)

    with open("nj-jwks.json", "r") as f:
        jwt_json = json.loads(f.read())
        v.import_signing_key("shc",
            "https://docket.care/nj",
            jwt_json
        )

    vax_data = None
    with open("example-01-f-qr-code-numeric-value-0.txt", "r") as f:
        vax_data = v.parse_card_data(f.read())


    print(vars(vax_data[0]))
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

#!/usr/bin/env python3

import json
import vaksina
import vaksina.shc as shc
import vaksina.shc.key_management as km
from vaksina.vaksina import Vaksina
from vaksina.validators import Validators

def main():
    v = Vaksina()

    # Configuration Stuff
    with open("jwks.json", "r") as f:
        jwt_json = json.loads(f.read())
        v.import_signing_key("shc",
                             "https://spec.smarthealth.cards/examples/issuer",
                             jwt_json)

    # with open("data/shc_keys.json", "r") as f:
    #     v.import_key_database('shc', f.read())

    with open("data/vaccine_info.json") as f:
        v.load_vaccine_info(f.read())

    card = None
    with open("example-01-f-qr-code-numeric-value-0.txt", "r") as f:
        card = v.parse_card_data(f.read())

    cs = vaksina.Cardset()
    cs.add_card(card)
    print(json.dumps(cs.to_dict(), indent=2))

if __name__ == '__main__':
    main()

#!/usr/bin/python3

import json
import vaksina.shc as shc
import vaksina.shc.key_management as km

def main():
    KeyManager = km.KeyManagement()

    with open("jwks.json", "r") as f:
        jwt_json = json.loads(f.read())

        KeyManager.enroll_key_for_key_id(
            "https://spec.smarthealth.cards/examples/issuer",
            jwt_json
        )

    with open("nj-jwks.json", "r") as f:
        KeyManager.enroll_key_for_key_id(
            "https://docket.care/nj",
            jwt_json
        )

    import pprint
    pprint.pprint(km.KeyManagement._key_storage)

if __name__ == '__main__':
    main()
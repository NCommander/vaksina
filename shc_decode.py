#!/usr/bin/python3
import base64
import re
import zlib
import json
from jose import jwk, jws
from jose.constants import ALGORITHMS
from jose.exceptions import JWSError

valid_pubkeys = {}

def load_pubkey(org, filename):
    # SHC says this is what must be used
    with open(filename, 'r') as f:
        jwt_pubkey = json.loads(f.read())
        valid_keys = []

        # Specification allows multiple keys, so lets process them one by one
        for key in jwt_pubkey['keys']:
            if key['kty'] != 'EC':
                print("ERROR: Can't load non EC key")
                continue
            
            if key['use'] != 'sig':
                print("ERROR: key type not signature")
                continue

            if key['alg'] != 'ES256':
                print("ERROR: Not ES256 key!")
                continue

            if key['crv'] != 'P-256':
                print("ERROR: not the right type of curve")
                continue

            # make sure we have x and why
            if "x" not in key or "y" not in key:
                print("x/y cooridors not found!")
                continue

            if "d" in key:
                print("SUPER ERROR: SOMEONE LEFT THE PRIVATE KEY IN PLACE!")

            key_data = {}
            key_data['isn'] = org
            key_data['key'] = jwk.construct(key, algorithm=ALGORITHMS.ES256)
            #key_data['pem']= algo.from_jwk(json.dumps(key)).public_bytes(
            #    encoding=serialization.Encoding.PEM,
            #    format=serialization.PublicFormat.SubjectPublicKeyInfo
            #)

            valid_pubkeys[key['kid']] = key_data

def decode_shc(shc_string):
    if shc_string[0:5] != 'shc:/':
        raise Exception("Not a SHC QR code")

    # based off marcan2020.medium.com/reversing-smart-health-cards-e765157fae9
    parts = re.findall('..', shc_string[5:])
    b64_data = ""
    for p in parts:
        b64_data += chr(int(p) + 45)

    # Padd Base64 if needed
    padding_needed = len(b64_data) % 4
    if padding_needed != 0:
        for _ in range(padding_needed):
            b64_data += '='
    jwt_data = base64.urlsafe_b64decode(b64_data)
    print(jwt_data)
    # We first decode without validation, because
    # we need pubkey ..

    unvalidated_vac_data = jws.get_unverified_header(b64_data)
    signing_key = unvalidated_vac_data['kid']

    if signing_key not in valid_pubkeys:
        print("NOT A KNOWN KEY!")
        return

    signed_data = jws.verify(b64_data, valid_pubkeys[signing_key]['key'], ALGORITHMS.ES256)
    print("ES256 Signature Good!")

    raw_vax_data = str(zlib.decompress(signed_data, wbits=-15), 'utf-8')
    vax_data = json.loads(raw_vax_data)

    #print(json.dumps(vax_data, indent=2))


    # Ok, at this point, we need to validate if this is a COVID health care, and what else
    vc_data = vax_data['vc']
    
    is_covid_card = False
    for card_type in vc_data['type']:
        if card_type == "https://smarthealth.cards#covid19":
            is_covid_card = True

    if is_covid_card is False:
        print("ERROR: NOT A COVID-19 CARD")
    
    print("SHC is COVID-19 Vaccination Record")

    # We need to walk entries, and sort. Its technically
    # possible to have multiple People on an entry, but
    # we'll just blow up if that is the case

    person_entry = None
    immunization_entries = []

    for entry in vc_data['credentialSubject']['fhirBundle']['entry']:
        if entry["resource"]["resourceType"] == "Patient":
            person_entry = entry["resource"]

        if entry["resource"]["resourceType"] == "Immunization":
            immunization_entries.append(entry["resource"])

    print()

    # Name is kinda weird ...
    name = ""

    if len(person_entry['name']) > 1:
        print("ERROR: more than one person name?!")
        return
    
    for name_bit in person_entry['name'][0]['given']:
        name = name + name_bit + " "
    name = name + person_entry['name'][0]['family']

    print("NAME: ", name)
    print("BIRTHDATE: ", person_entry['birthDate'])

    # https://www.azdhs.gov/documents/preparedness/epidemiology-disease-control/immunization/vaccines-for-children/forms/list-of-vaccine-names-best-asiis-selection.pdf
    # handle referencing code
    # 207 == Moderna (2 shots)
    # 
    # Pfizer has multiple codes based off age. We just need two of any
    # 208
    # 217
    # 218
    #
    # J&J Janssen
    # 212 (1 shots)

    # The rest aren't approved in the US, but noting them here
    # 210 AstraZeneca
    # 211 Novavax
    # 510 Snipharm
    # 511 Coronavax
    # there is also an unspecifeied code (213), but we can't trust it

    #last_issued = None
    is_vaccinated = False
    vaccine_type = None
    shot_count = 0

    # Handle JJ as a special case, since we only need one
    for immunization in immunization_entries:
        # For a vaccine seriesto count, it must be complete,
        # and the immunization dates must be 2 weeks past the
        # latest dose
        if immunization['status'] == "completed" and \
            immunization['vaccineCode']['coding'][0]['code'] == 212:
            is_vaccinated = True
            vaccine_type = "Janseen"
            last_issued = immunization['occurrenceDateTime']
            shot_count = 1
    
    # Ok, let's handle the two shot ones
    for immunization in immunization_entries:
        vaccine_code = int(immunization['vaccineCode']['coding'][0]['code'])
        if immunization['status'] == "completed" and vaccine_code == 207:
            vaccine_type = "Moderna"
            #last_issued = immunization['occurrenceDateTime']
            shot_count = shot_count + 1

        if immunization['status'] == "completed" and \
            (vaccine_code == 208 or
             vaccine_code == 217 or
             vaccine_code == 218):
            vaccine_type = "Pfizer"
            #last_issued = immunization['occurrenceDateTime']
            shot_count = shot_count + 1

    if shot_count >= 2:
        print()
        print("User has 2 shots!")
        print("User has completed", vaccine_type, "vaccine")
        return

    # Fail
    print("User is not vaccinated ...")

    # Determine if we're properly vaccinated here
    #
    # That means you need two Moderna/Pfizer, or 1 JJ

if __name__ == '__main__':
    load_pubkey("https://spec.smarthealth.cards/examples/issuer", "jwks.json")
    load_pubkey("https://docket.care/nj", "nj-jwks.json")

    #print(valid_pubkeys)

    test_shr = 'shc:/56762909524320603460292437404460312229595326546034602925407728043360287028647167452228092861333145643765314159064022030645045908564355034142454136403706366541713724123638030437562204673740753232392543344332605736010645292953127074242843503861221276716638370841727136710336077042394332675730226770544222601121257021736673065528340559522923650441330426325035757340575658432034345960112704044325260824656173256921003638395062653365562543595852673966226766345222242373550421410404577163557156556540004331083266342936065427506158605533125032505026733958416004583609726208664139360760577774725965211064453725000470326420420075375611276204102312585575273853712105257203316528097232693173222956503170307267544445767409247677276476365777660670532056076245296629764103582305383776282730531245383635060004042920505725280023354528570544074532073665226329232458045652456875314500772559236964003307327041106370296529072552360055573237045341316871254238066824724408560437331253765255061226102377777438421011542812755872522634552207126903605421333150360022435527080426550674505577222253063359122445327165345831355903287433326404264023110553344423752762343970033030340559076438243426110521393008681224566824682935593271686068275326306568354036736106716028102840532940717569714443530422614557316069432661112475384021386033350839403372072264430968605439693550312134730543765744752052252225530312353561590035093223396155575922614111012505071157527321107273713038661226537428220036716467425620702100207160256805602022602345362403700611090306552967080373540427247345202111033743565430360431445562455368113774'
    decode_shc(test_shr)

    #json_load = json.loads(nc_covid)
    #print(json.dumps(json_load, indent=2))
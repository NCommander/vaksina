## REST/RPC API Notes

### /v1/card_data_submission:
Takes JSON object in from scanning application

#### POST
 - qr_decode (Required)
 Representation of QR Data with no processing attached

 For instance, a smart healthcard would just upload data  in the form of of shc:1234

 In case of binary data, data shall be uploaded as Base64

 - qr_data_type (Required)

 QR data type (MIME type(?), check QR standards)

#### Returns

```
{
    card_validation_status = "good"
    card_decoded_content: {
        card_type: "smart_health_card",
        first_name: "John",
        last_name: "C. Anybody",
        immunizations: [
            {
                vaccine: "MODERNA",
                given_on: "01-01-2021",
                lot_number: "1"
            },
            {
                vaccine: "MODERNA",
                given_on: "01-29-2021",
                lot_number: "20"

            },
        ],
        issued_by: "Example Issuer"
        ]
    }
    validation_error = ""
}

```
200 OK used to represent success (green check) validation.

JSON object that contains the the following fields
 * card_validity
 * first_name
 * last_name
 * immunizations (object)
 * last_administered
 * issued_by


400 Bad Request used for Red Check/Grey Check

 
from datetime import datetime

import requests

cert=('public.pem', 'private.key')


def client_assertion():
    url = "https://jwkms.ob.forgerock.financial/api/crypto/signClaims"
    issuer_id = "d3b55437-7654-41d5-94c3-89fca88d65b8"
    payload = {
        "sub": issuer_id,
        "exp": datetime.now().timestamp() + 60,
        "aud": "https://matls.as.aspsp.ob.forgerock.financial/oauth2/openbanking"
    }
    headers = {
        'issuerId': issuer_id
    }
    response = requests.request("POST", url, json=payload, headers=headers, cert=cert)
    print(response.text)


client_assertion()

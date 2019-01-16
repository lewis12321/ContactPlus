import os
import tempfile
from datetime import datetime

import requests

public_cert = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")
private_key = tempfile.NamedTemporaryFile(delete=False, suffix=".key")
public_cert.write(os.environ.get('PUBLIC_CERT').replace("\\n", "\n").encode())
private_key.write(os.environ.get('PRIVATE_KEY').replace("\\n", "\n").encode())
public_cert.close()
private_key.close()
cert = (public_cert.name, private_key.name)

client_id = "ebce07ef-e23a-4b61-924b-d7426b77880a"
redirect_uri = "https://contactplustest.herokuapp.com"


def get_client_assertion():
    url = "https://jwkms.ob.forgerock.financial/api/crypto/signClaims"
    payload = {
        "sub": client_id,
        "exp": datetime.now().timestamp() + 60,
        "aud": "https://matls.as.aspsp.ob.forgerock.financial/oauth2/openbanking"
    }
    headers = {
        'issuerId': client_id
    }
    response = requests.request("POST", url, json=payload, headers=headers, cert=cert)

    return response.text


def client_credentials(client_assertion):
    url = "https://matls.as.aspsp.ob.forgerock.financial/oauth2/realms/root/realms/openbanking/access_token"

    payload = f"grant_type=client_credentials&scope=openid%20accounts%20payments&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer&client_assertion={client_assertion}"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
    }
    response = requests.request("POST", url, headers=headers, data=payload, cert=cert)

    return response.json()


def create_payment_request(access_token):
    payload = {
        "Data": {
            "Initiation": {
                "InstructionIdentification": "ACME412",
                "EndToEndIdentification": "FRESCO.21302.GFX.20",
                "InstructedAmount": {
                    "Amount": "250.88",
                    "Currency": "GBP"
                },
                "CreditorAccount": {
                    "SchemeName": "SortCodeAccountNumber",
                    "Identification": "20793443634639",
                    "Name": "demo"
                }
            }
        },
        "Risk": {}
    }

    url = "https://rs.aspsp.ob.forgerock.financial:443/open-banking/v2.0/payments"

    headers = {
        'Authorization': f"Bearer {access_token['access_token']}",
        'x-idempotency-key': "FRESCO.21302.GFX.20",
        'x-fapi-financial-id': "0015800001041REAAY",
    }

    response = requests.request("POST", url, json=payload, headers=headers, cert=cert)

    return response.json()


def generate_request_params(payment_request):
    import requests

    url = "https://jwkms.ob.forgerock.financial:443/api/crypto/signClaims"
    payment_id = payment_request['Data']['PaymentId']

    payload = {
        "aud": "https://matls.as.aspsp.ob.forgerock.financial/oauth2/openbanking",
        "scope": "openid accounts payments",
        "iss": client_id,
        "claims": {
            "id_token": {
                "acr": {
                    "value": "urn:openbanking:psd2:sca",
                    "essential": True
                },
                "openbanking_intent_id": {
                    "value": f"{payment_id}",
                    "essential": True
                }
            },
            "userinfo": {
                "openbanking_intent_id": {
                    "value": f"{payment_id}",
                    "essential": True
                }
            }
        },
        "response_type": "code id_token",
        "redirect_uri": f"{redirect_uri}",
        "state": "10d260bf-a7d9-444a-92d9-7b7a5f088208",
        "exp": datetime.now().timestamp() + 60,
        "nonce": "10d260bf-a7d9-444a-92d9-7b7a5f088208",
        "client_id": f"{client_id}"
    }

    headers = {
        'jwkUri': "https://as.aspsp.ob.forgerock.financial/oauth2/realms/root/realms/openbanking/connect/jwk_uri",
        'issuerId': client_id,
    }

    response = requests.request("POST", url, json=payload, headers=headers, cert=cert)

    return response.text


def generate_hybrid_flow(request_param):
    url = f"https://matls.as.aspsp.ob.forgerock.financial/oauth2/realms/root/realms/openbanking/authorize?response_type=code%20id_token&client_id={client_id}&state=10d260bf-a7d9-444a-92d9-7b7a5f088208&nonce=10d260bf-a7d9-444a-92d9-7b7a5f088208&scope=openid%20payments%20accounts&redirect_uri={redirect_uri}&request={request_param}"
    return url


def get_access_token_for_payment_submission(exchange_code, client_assertion, redirect_uri):
    url = "https://matls.as.aspsp.ob.forgerock.financial/oauth2/realms/root/realms/openbanking/access_token"

    payload = f"grant_type=authorization_code&code={exchange_code}&redirect_uri={redirect_uri}&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer&client_assertion={client_assertion}"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
    }

    response = requests.request("POST", url, data=payload, headers=headers, cert=cert)

    print(response.text)
    return response.json()


def payment_submission(payment_token, payment_request):

    url = "https://rs.aspsp.ob.forgerock.financial:443/open-banking/v2.0/payment-submissions"

    payload = {
        "Data": {
            "PaymentId": f"{payment_request['Data']['PaymentId']}",
            "Initiation": {
                "InstructionIdentification": "ACME412",
                "EndToEndIdentification": "FRESCO.21302.GFX.20",
                "InstructedAmount": {
                    "Amount": "250.88",
                    "Currency": "GBP"
                },
                "CreditorAccount": {
                    "SchemeName": "SortCodeAccountNumber",
                    "Identification": "20793443634639",
                    "Name": "demo"
                }
            }
        },
        "Risk": {}
    }

    headers = {
        'Authorization': f"Bearer {payment_token['access_token']}",
        'x-idempotency-key': "FRESCO.21302.GFX.20",
        'x-fapi-financial-id': "0015800001041REAAY"
    }

    response = requests.request("POST", url, json=payload, headers=headers, cert=cert)

    print(response.text)
    return response.json()


def create_payment_dictionary(client_assertion, payment_request, exchange_code):
    payment_dict = {
        "client_assertion": client_assertion,
        "payment_request": payment_request,
        "exchange_code": exchange_code
    }
    return payment_dict


def setup_payment():
    client_assertion = get_client_assertion()
    access_token = client_credentials(client_assertion)
    payment_request = create_payment_request(access_token)
    request_param = generate_request_params(payment_request)
    exchange_code = generate_hybrid_flow(request_param)
    print(client_assertion)
    print(access_token)
    print(payment_request)
    print(request_param)
    print(exchange_code)
    #payment_dict = create_payment_dictionary(client_assertion, payment_request, exchange_code)
    return ""

def make_payment():
    payment_token = get_access_token_for_payment_submission(exchange_code, client_assertion)
    payment_submission(payment_token, payment_request)

setup_payment()
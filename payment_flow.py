import json
import os
import sys
import tempfile
import uuid
from datetime import datetime

import boto3
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
dynamodb = boto3.client('dynamodb', region_name='eu-west-2')


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
    print(f'Got client assertion: {response.text}')
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
    state = str(uuid.uuid4())

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
        "state": state,
        "exp": datetime.now().timestamp() + 60,
        "nonce": "10d260bf-a7d9-444a-92d9-7b7a5f088208",
        "client_id": f"{client_id}"
    }

    headers = {
        'jwkUri': "https://as.aspsp.ob.forgerock.financial/oauth2/realms/root/realms/openbanking/connect/jwk_uri",
        'issuerId': client_id,
    }

    response = requests.request("POST", url, json=payload, headers=headers, cert=cert)

    dynamodb.put_item(TableName='Payments', Item={'state': {'S': state}, 'data': {'S': json.dumps(payment_request)}})

    return response.text, state


def generate_hybrid_flow(request_param, state):
    url = f"https://matls.as.aspsp.ob.forgerock.financial/oauth2/realms/root/realms/openbanking/authorize?response_type=code%20id_token&client_id={client_id}&state={state}&nonce=10d260bf-a7d9-444a-92d9-7b7a5f088208&scope=openid%20payments%20accounts&redirect_uri={redirect_uri}&request={request_param}"
    return url


def get_access_token_for_payment_submission(exchange_code, client_assertion, redirect_uri):
    url = "https://matls.as.aspsp.ob.forgerock.financial/oauth2/realms/root/realms/openbanking/access_token"

    payload = f"grant_type=authorization_code&code={exchange_code}" \
              f"&redirect_uri={redirect_uri}" \
              f"&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer" \
              f"&client_assertion={client_assertion}"
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
    }

    req = requests.Request("POST", url, data=payload, headers=headers, cert=cert).prepare()
    print_request(req)

    response = requests.request("POST", url, data=payload, headers=headers, cert=cert)

    print(response.text)
    return response.json()


def payment_submission(payment_request, payment_id):
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
        'Authorization': f"Bearer {payment_id['access_token']}",
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
    request_param, state = generate_request_params(payment_request)
    auth_url = generate_hybrid_flow(request_param, state)
    print(auth_url)
    return auth_url


def make_payment(client_assertion, exchange_code, state):
    payment_token = get_access_token_for_payment_submission(client_assertion, exchange_code, redirect_uri)
    response = dynamodb.get_item(TableName='Payments', Key={'state': {'S': str(state)}})
    payment_id = json.loads(response['Item']["data"]['S'])['Data']['PaymentId']
    payment_submission(payment_token, payment_id)

def print_request(req):
    print('HTTP/1.1 {method} {url}\n{headers}\n\n{body}'.format(
        method=req.method,
        url=req.url,
        headers='\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        body=req.body,
    ))
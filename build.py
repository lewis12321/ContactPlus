import os

private_key = os.environ.get('PRIVATE_KEY', 'Test Private')
public_cert = os.environ.get('PUBLIC_CERT', 'Test Public')
env = os.environ.get('PROD')

print(env)
print(private_key)
print(public_cert)

if env == "TEST":
    f = open("private.key", "w+")
    f.write(private_key)
    f.close()

    f = open("public.pem", "w+")
    f.write(public_cert)
    f.close()

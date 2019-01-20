import bcrypt
import boto3

dynamodb = boto3.client('dynamodb', region_name='eu-west-2')


def register_user(request):
    email = request.form['email']
    hashed_bytes = bcrypt.hashpw(request.form['psw'].encode("utf-8"), bcrypt.gensalt())
    hashed = hashed_bytes.decode("utf-8")
    dynamodb.put_item(TableName='Users', Item={'email': {'S': email}, 'password': {'S': str(hashed)}})


def verify_user(request):
    email = request.form['email']
    data = dynamodb.get_item(TableName='Users', Key={'email': {'S': str(email)}})
    hashed_pw = data['Item']['password']['S']
    if bcrypt.checkpw(request.form['psw'].encode("utf-8"), hashed_pw.encode("utf-8")):
        print(True)
    else:
        print(False)


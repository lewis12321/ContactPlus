import os
from urllib import parse
from flask import Flask, render_template, request
from payment_flow import get_access_token_for_payment_submission, get_client_assertion, setup_payment

app = Flask(__name__)

redirect_uri = "https://contactplustest.herokuapp.com"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def exchange():
    fragment = parse.parse_qs(parse.urlsplit(request.data).fragment.decode("utf-8"))
    code = fragment.get('code', None)
    print(code)
    get_access_token_for_payment_submission(fragment['code'][0], get_client_assertion, redirect_uri)
    print
    return ""


@app.route("/payment/", methods=["GET"])
def payment():
    url = setup_payment()
    return render_template("payment.html", url=url)


app.run(host="0.0.0.0", port=os.getenv('PORT', 55555))

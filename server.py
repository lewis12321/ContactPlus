import os
import logging
import sys
from urllib import parse
from flask import Flask, render_template, request
from werkzeug.utils import redirect

from payment_flow import get_access_token_for_payment_submission, get_client_assertion, setup_payment, make_payment

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)

redirect_uri = "https://contactplustest.herokuapp.com"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def exchange():
    print("Submitting Payment")
    fragment = parse.parse_qs(parse.urlsplit(request.data).fragment.decode("utf-8"))
    print("1...")
    exchange_code = fragment['code'][0]
    print("2...")
    state = fragment['state'][0]
    print("3...")
    make_payment(get_client_assertion(), exchange_code, state)
    print("4...")
    return render_template("success.html", response="Success")


@app.route("/payment/", methods=["GET"])
def payment():
    print("Creating Payment...")
    url = setup_payment()
    return redirect(url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv('PORT', 55555))

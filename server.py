import os
from urllib import parse
from flask import Flask, render_template, request
from werkzeug.utils import redirect

from payment_flow import get_access_token_for_payment_submission, get_client_assertion, setup_payment, make_payment

app = Flask(__name__)

redirect_uri = "https://contactplustest.herokuapp.com"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def exchange():
    fragment = parse.parse_qs(parse.urlsplit(request.data).fragment.decode("utf-8"))
    exchange_code = fragment['code'][0]
    state = fragment['state'][0]
    make_payment(get_client_assertion(), exchange_code, state)
    return render_template("success.html", response="Success")


@app.route("/payment/", methods=["GET"])
def payment():
    print("Creating Payment...")
    url = setup_payment()
    return redirect(url)


app.run(host="0.0.0.0", port=os.getenv('PORT', 55555))

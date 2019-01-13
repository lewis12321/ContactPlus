import os
from urllib import parse
from flask import Flask, render_template, request
from payment_flow import get_access_token_for_payment_submission, get_client_assertion, setup_payment

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def exchange():
    fragment = parse.parse_qs(parse.urlsplit(request.data).fragment.decode("utf-8"))
    print(fragment)
    get_access_token_for_payment_submission(fragment['code'], get_client_assertion)
    return ""


@app.route("/payment/", methods=["GET"])
def payment():
    setup_payment()
    return ""

app.run(host="0.0.0.0", port=os.getenv('PORT', 55555))

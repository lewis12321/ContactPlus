import os
from urllib import parse

import urllib3
from flask import Flask, render_template, request

from payment_flow import get_access_token_for_payment_submission, client_assertion

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def exchange():
    fragment = parse.parse_qs(parse.urlsplit(request.data).fragment.decode("utf-8"))
    get_access_token_for_payment_submission(fragment['code'], client_assertion)
    return ""


app.run(host="0.0.0.0", port=os.getenv('PORT', 55555))

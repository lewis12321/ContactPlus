from flask import Flask, render_template, request

from payment_flow import get_access_token_for_payment_submission

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def exchange():
    print(request.data)
    get_access_token_for_payment_submission()
    return ""


app.run(host="0.0.0.0", port=55555)
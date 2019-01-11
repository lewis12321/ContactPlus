from flask import Flask, render_template, request
import sys

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def exchange():
    print(request.data)
    sys.stdout.write(request.data)
    return ""

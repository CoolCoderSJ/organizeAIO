from flask import render_template

from app import app

@app.route("/")
def index_route():
    return render_template("index.html")
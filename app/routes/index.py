from flask import render_template, session, redirect

from app import app

@app.route("/")
def index_route():
    print(session.items())
    if 'user' in session:
        return redirect("/dashboard")
    return render_template("landing.html")
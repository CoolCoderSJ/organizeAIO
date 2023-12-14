from flask import render_template, session, redirect, request
from app import app, db, get_all_docs, users, Query
from datetime import datetime

from argon2 import PasswordHasher
ph = PasswordHasher()

@app.get("/login")
def login():
    return render_template("login.html")

@app.get("/logout")
def logout():
    session.pop('user', None)
    return redirect("/")

@app.post("/login")
def login_post():
    print(request.form)
    if not request.form or not 'username' in request.form or not 'password' in request.form:
        return render_template("login.html", error="invalid request")
    
    username = request.form['username']
    password = request.form['password']

    allusers = users.list(queries=[Query.equal('name', username)])['users']
    if len(allusers) == 0:
        sessid = users.create('unique()', name=username, password=password)['$id']
        return redirect("/")
    
    user = allusers[0]
    try:
        ph.verify(user['password'], password)
    except: 
        return render_template("login.html", error="invalid password")
   
    session['user'] = user['$id']
    return redirect("/")
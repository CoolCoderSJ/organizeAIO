from flask import render_template, session, redirect, request
from app import app, db, get_all_docs
from datetime import datetime

@app.route("/hackathon/<hid>/form")
def registration_form(hid):
    form = get_all_docs(hid, "registration_form")
    return render_template("registration_form.html", form=form)

@app.post("/hackathon/<hackathon_id>/form/delete/<form_id>")
def delete_form_field(hackathon_id, form_id):
    db.delete(hackathon_id, "registration_form", form_id)
    return redirect(f"/hackathon/{hackathon_id}/form")

@app.post("/hackathon/<hackathon_id>/form/edit/<form_id>")
def edit_form_field(hackathon_id, form_id):
    data = {k: v[0] for k, v in dict(request.form).items()}
    db.update(hackathon_id, "registration_form", form_id, data)
    return redirect(f"/hackathon/{hackathon_id}/form")

@app.post("/hackathon/<hackathon_id>/form/add")
def add_form_field(hackathon_id):
    data = {k: v[0] for k, v in dict(request.form).items()}
    db.create(hackathon_id, "registration_form", "unique()", data)
    return redirect(f"/hackathon/{hackathon_id}/form")

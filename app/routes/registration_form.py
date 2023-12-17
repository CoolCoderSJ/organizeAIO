from flask import render_template, session, redirect, request
from app import app, db, get_all_docs
from datetime import datetime

@app.route("/hackathon/<hid>/form")
def registration_form(hid):
    form = get_all_docs(hid, "registration_form")
    return render_template("registration_form.html", form=form)

@app.post("/hackathon/<hackathon_id>/form/delete/<form_id>")
def delete_form_field(hackathon_id, form_id):
    field_name = db.get_document(hackathon_id, "registration_form", form_id)['field_name']
    db.delete_document(hackathon_id, "registration_form", form_id)
    db.delete_attribute(hackathon_id, "attendees", field_name)
    return redirect(f"/hackathon/{hackathon_id}/form")

@app.post("/hackathon/<hackathon_id>/form/edit/<form_id>")
def edit_form_field(hackathon_id, form_id):
    data = {k: v for k, v in request.form.items()}
    data['options'] = data['options'].split(', ')
    if data['required'] == "Yes": data['required'] = True
    else: data['required'] = False
    db.update_document(hackathon_id, "registration_form", form_id, data)
    db.update_attribute(hackathon_id, "attendees", data['field_name'], 100, False, None)
    return redirect(f"/hackathon/{hackathon_id}/form")

@app.post("/hackathon/<hackathon_id>/form/add")
def add_form_field(hackathon_id):
    data = {k: v for k, v in request.form.items()}
    data['options'] = data['options'].split(', ')
    if data['required'] == "Yes": data['required'] = True
    else: data['required'] = False
    db.create_document(hackathon_id, "registration_form", "unique()", data)
    db.create_string_attribute(hackathon_id, "attendees", data['field_name'], 100, False, None)
    return redirect(f"/hackathon/{hackathon_id}/form")

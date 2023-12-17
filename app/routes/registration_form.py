from flask import render_template, session, redirect, request
from app import app, db, get_all_docs
from datetime import datetime

@app.route("/hackathon/<hid>/form")
def registration_form(hid):
    form = get_all_docs(hid, "registration_form")
    hacks = db.get(hid)
    meta = db.get_document(hacks['$id'], "metadata", "data")

    data = {
        "id": hacks['$id'],
        "name": meta['name'],
    }
    return render_template("registration_form.html", form=form, data=data)

@app.post("/hackathon/<hackathon_id>/form/delete/<form_id>")
def delete_form_field(hackathon_id, form_id):
    field_name = db.get_document(hackathon_id, "registration_form", form_id)['field_name']
    db.delete_document(hackathon_id, "registration_form", form_id)
    db.delete_attribute(hackathon_id, "attendees", field_name)
    return redirect(f"/hackathon/{hackathon_id}/form")

@app.post("/hackathon/<hackathon_id>/form/edit/<form_id>")
def edit_form_field(hackathon_id, form_id):
    data = {k: v for k, v in request.form.items()}
    data['options'] = data['options'].replace(", ", ",").split(',')
    if data['required'] == "Yes": data['required'] = True
    else: data['required'] = False
    data['field_name'] = "".join([s for s in data['field_name'] if s.isalnum()])
    db.update_document(hackathon_id, "registration_form", form_id, data)
    attributes = db.list_attributes(hackathon_id, "attendees")['attributes']
    listOfAttributes = [attribute['key'] for attribute in attributes]
    listOfAttributes.remove("checkedIn")

    docs = get_all_docs(hackathon_id, "registration_form")
    listOfCurrentAttrs = [doc['field_name'] for doc in docs]

    notInCurrent = [attr for attr in listOfAttributes if attr not in listOfCurrentAttrs]

    if len(notInCurrent) > 0:
        db.delete_attribute(hackathon_id, "attendees", notInCurrent[0])
        db.create_string_attribute(hackathon_id, "attendees", data['field_name'], 100, False, None)
    return redirect(f"/hackathon/{hackathon_id}/form")

@app.post("/hackathon/<hackathon_id>/form/add")
def add_form_field(hackathon_id):
    data = {k: v for k, v in request.form.items()}
    data['options'] = data['options'].replace(", ", ",").split(',')
    if data['required'] == "Yes": data['required'] = True
    else: data['required'] = False
    data['field_name'] = "".join([s for s in data['field_name'] if s.isalnum()])
    db.create_document(hackathon_id, "registration_form", "unique()", data)
    db.create_string_attribute(hackathon_id, "attendees", data['field_name'], 100, False, None)
    return redirect(f"/hackathon/{hackathon_id}/form")

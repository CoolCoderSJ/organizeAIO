from flask import render_template, session, redirect, request
from app import app, db, get_all_docs
from datetime import datetime

@app.route("/hackathon/<hid>/attendees")
def attendees(hid):
    user = session['user']
    teamIds = db.get_document(hid, "metadata", "data")['teamIds']
    if not hid.startswith(user) and user not in teamIds:
        return abort(403)

    attendees = get_all_docs(hid, "attendees")
    hacks = db.get(hid)
    meta = db.get_document(hacks['$id'], "metadata", "data")

    data = {
        "id": hacks['$id'],
        "name": meta['name'],
    }
    attributes = db.list_attributes(hid, 'attendees')

    registration = get_all_docs(hid, "registration_form")
    form = {}
    for item in registration:
        form[item['field_name']] = {
            "type": item['type'],
            "required": item['required'],
            "options": item['options'],
            "default": item['default'],
            "placeholder": item['placeholder']
        }
    print(form)
    return render_template("attendees.html", attendees=attendees, data=data, attrs=attributes, form=form)

@app.post("/hackathon/<hackathon_id>/attendees/delete/<attendee_id>")
def delete_attendee(hackathon_id, attendee_id):
    user = session['user']
    teamIds = db.get_document(hackathon_id, "metadata", "data")['teamIds']
    if not hackathon_id.startswith(user) and user not in teamIds:
        return abort(403)

    db.delete_document(hackathon_id, "attendees", attendee_id)
    return redirect(f"/hackathon/{hackathon_id}/attendees")

@app.post("/hackathon/<hackathon_id>/attendees/checkin/<attendee_id>")
def checkin_attendee(hackathon_id, attendee_id):
    user = session['user']
    teamIds = db.get_document(hackathon_id, "metadata", "data")['teamIds']
    if not hackathon_id.startswith(user) and user not in teamIds:
        return abort(403)

    db.update_document(hackathon_id, "attendees", attendee_id, {"checkedIn": True})
    return redirect(f"/hackathon/{hackathon_id}/attendees")

@app.post("/hackathon/<hackathon_id>/attendees/uncheckin/<attendee_id>")
def uncheckin_attendee(hackathon_id, attendee_id):
    user = session['user']
    teamIds = db.get_document(hackathon_id, "metadata", "data")['teamIds']
    if not hackathon_id.startswith(user) and user not in teamIds:
        return abort(403)

    db.update_document(hackathon_id, "attendees", attendee_id, {"checkedIn": False})
    return redirect(f"/hackathon/{hackathon_id}/attendees")

@app.post("/hackathon/<hackathon_id>/attendees/edit/<attendee_id>")
def edit_attendee(hackathon_id, attendee_id):
    user = session['user']
    teamIds = db.get_document(hackathon_id, "metadata", "data")['teamIds']
    if not hackathon_id.startswith(user) and user not in teamIds:
        return abort(403)

    data = {k: v for k, v in request.form.items()}
    db.update_document(hackathon_id, "attendees", attendee_id, data)
    return redirect(f"/hackathon/{hackathon_id}/attendees")

@app.post("/hackathon/<hackathon_id>/attendees/add")
def add_attendee(hackathon_id):
    user = session['user']
    teamIds = db.get_document(hackathon_id, "metadata", "data")['teamIds']
    if not hackathon_id.startswith(user) and user not in teamIds:
        return abort(403)
        
    data = {k: v for k, v in request.form.items()}
    db.create_document(hackathon_id, "attendees", "unique()", data)
    return redirect(f"/hackathon/{hackathon_id}/attendees")

from flask import render_template, session, redirect, request
from app import app, db, get_all_docs
from datetime import datetime

@app.route("/hackathon/<hid>/attendees")
def attendees(hid):
    attendees = get_all_docs(hid, "attendees")
    hacks = db.get(hid)
    meta = db.get_document(hacks['$id'], "metadata", "data")

    data = {
        "id": hacks['$id'],
        "name": meta['name'],
    }
    attributes = db.list_attributes(hid, 'attendees')
    return render_template("attendees.html", attendees=attendees, data=data, attrs=attributes)

@app.post("/hackathon/<hackathon_id>/attendees/delete/<attendee_id>")
def delete_attendee(hackathon_id, attendee_id):
    db.delete(hackathon_id, "attendees", attendee_id)
    return redirect(f"/hackathon/{hackathon_id}/attendees")

@app.post("/hackathon/<hackathon_id>/attendees/checkin/<attendee_id>")
def checkin_attendee(hackathon_id, attendee_id):
    attendee = db.get(hackathon_id, "attendees", attendee_id)
    attendee['checkedIn'] = True
    db.update(hackathon_id, "attendees", attendee_id, attendee)
    return redirect(f"/hackathon/{hackathon_id}/attendees")

@app.post("/hackathon/<hackathon_id>/attendees/uncheckin/<attendee_id>")
def uncheckin_attendee(hackathon_id, attendee_id):
    attendee = db.get(hackathon_id, "attendees", attendee_id)
    attendee['checkedIn'] = False
    db.update(hackathon_id, "attendees", attendee_id, attendee)
    return redirect(f"/hackathon/{hackathon_id}/attendees")

@app.post("/hackathon/<hackathon_id>/attendees/edit/<attendee_id>")
def edit_attendee(hackathon_id, attendee_id):
    data = {k: v[0] for k, v in dict(request.form).items()}
    db.update(hackathon_id, "attendees", attendee_id, data)
    return redirect(f"/hackathon/{hackathon_id}/attendees")

@app.post("/hackathon/<hackathon_id>/attendees/add")
def add_attendee(hackathon_id):
    data = {k: v[0] for k, v in dict(request.form).items()}
    db.create(hackathon_id, "attendees", data)
    return redirect(f"/hackathon/{hackathon_id}/attendees")

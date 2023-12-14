from flask import render_template, session, redirect, request
from app import app, db, get_all_docs
from datetime import datetime

@app.route("/hackathon/<hid>/schedule")
def schedule(hid):
    schedule = get_all_docs(hid, "schedule")
    return render_template("schedule.html", schedule=schedule)

@app.post("/hackathon/<hackathon_id>/schedule/delete/<schedule_id>")
def delete_schedule_item(hackathon_id, schedule_id):
    db.delete(hackathon_id, "schedule", schedule_id)
    return redirect(f"/hackathon/{hackathon_id}/schedule")

@app.post("/hackathon/<hackathon_id>/schedule/edit/<schedule_id>")
def edit_schedule_item(hackathon_id, schedule_id):
    data = {k: v[0] for k, v in dict(request.form).items()}
    db.update(hackathon_id, "schedule", schedule_id, data)
    return redirect(f"/hackathon/{hackathon_id}/schedule")

@app.post("/hackathon/<hackathon_id>/schedule/add")
def add_schedule_item(hackathon_id):
    data = {k: v[0] for k, v in dict(request.form).items()}
    db.create(hackathon_id, "schedule", "unique()", data)
    return redirect(f"/hackathon/{hackathon_id}/schedule")
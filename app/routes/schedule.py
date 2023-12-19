from flask import render_template, session, redirect, request
from app import app, db, get_all_docs
from datetime import datetime

@app.route("/hackathon/<hid>/schedule")
def schedule(hid):
    user = session['user']
    teamIds = db.get_document(hid, "metadata", "data")['teamIds']
    judgeIds = db.get_document(hid, "metadata", "data")['judgeIds']
    if user in judgeIds:
        return redirect("/hackathon/"+hid+"/judging")
    if not hid.startswith(user) and user not in teamIds:
        return abort(403)

    hacks = db.get(hid)
    meta = db.get_document(hacks['$id'], "metadata", "data")

    data = {
        "id": hacks['$id'],
        "name": meta['name'],
    }

    schedule = get_all_docs(hid, "schedule")
    s = []
    for i in schedule:
        i['startDateTime'] = datetime.strptime(i['startDateTime'], '%Y-%m-%dT%H:%M:%S.%f%z')
        i['endDateTime'] = datetime.strptime(i['endDateTime'], '%Y-%m-%dT%H:%M:%S.%f%z')
        s.append(i)
    schedule = sorted(s, key=lambda x: x['startDateTime'])
    s1 = []
    for i in schedule:
        i['originalStart'] = str(i['startDateTime']).replace(" ", "T").split("+")[0]
        i['originalEnd'] = str(i['endDateTime']).replace(" ", "T").split("+")[0]
        i['startDateTime'] = i['startDateTime'].strftime('%m/%d %I:%M %p')
        i['endDateTime'] = i['endDateTime'].strftime('%m/%d %I:%M %p')
        s1.append(i)
    schedule = s1

    return render_template("schedule.html", schedule=schedule, data=data)

@app.post("/hackathon/<hackathon_id>/schedule/delete/<schedule_id>")
def delete_schedule_item(hackathon_id, schedule_id):
    user = session['user']
    teamIds = db.get_document(hackathon_id, "metadata", "data")['teamIds']
    if not hackathon_id.startswith(user) and user not in teamIds:
        return abort(403)

    db.delete_document(hackathon_id, "schedule", schedule_id)
    return redirect(f"/hackathon/{hackathon_id}/schedule")

@app.post("/hackathon/<hackathon_id>/schedule/edit/<schedule_id>")
def edit_schedule_item(hackathon_id, schedule_id):
    user = session['user']
    teamIds = db.get_document(hackathon_id, "metadata", "data")['teamIds']
    if not hackathon_id.startswith(user) and user not in teamIds:
        return abort(403)

    data = {k: v for k, v in request.form.items()}
    db.update_document(hackathon_id, "schedule", schedule_id, data)
    return redirect(f"/hackathon/{hackathon_id}/schedule")

@app.post("/hackathon/<hackathon_id>/schedule/add")
def add_schedule_item(hackathon_id):
    user = session['user']
    teamIds = db.get_document(hackathon_id, "metadata", "data")['teamIds']
    if not hackathon_id.startswith(user) and user not in teamIds:
        return abort(403)
        
    data = {k: v for k, v in request.form.items()}
    db.create_document(hackathon_id, "schedule", "unique()", data)
    return redirect(f"/hackathon/{hackathon_id}/schedule")
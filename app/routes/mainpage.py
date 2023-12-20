from flask import render_template, session, redirect
from app import app, db, get_all_docs, Query
from datetime import datetime

@app.route("/hackathon/<id>")
def hackathon(id):
    user = session['user']
    teamIds = db.get_document(id, "metadata", "data")['teamIds']
    judgeIds = db.get_document(id, "metadata", "data")['judgeIds']
    if user in judgeIds:
        return redirect("/hackathon/"+id+"/judging")
    if not id.startswith(user) and user not in teamIds:
        return abort(403)

    hacks = db.get(id)
    meta = db.get_document(hacks['$id'], "metadata", "data")
    today = datetime.date(datetime.now())
    try:
        daysLeft = (int(str(datetime.date(datetime.strptime(meta['startDate'], '%Y-%m-%dT%H:%M:%S.%f%z')) - today).split(" ")[0]))
    except:
        daysLeft = 0
    attendees = get_all_docs(hacks['$id'], "attendees")        
    
    data = {
        "id": hacks['$id'],
        "name": meta['name'],
        "daysLeft": daysLeft,
        "attendees": len(attendees),
        "startDate": datetime.strptime(meta['startDate'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime("%m/%d/%Y"),
        "endDate": datetime.strptime(meta['endDate'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime("%m/%d/%Y"),
    }

    checekdIn = len(get_all_docs(id, "attendees", [Query.equal("checkedIn", True)]))
    counts = {
        "registration": len(get_all_docs(id, "registration_form")),
        "schedule": len(get_all_docs(id, "schedule")),
        "projects": len(get_all_docs(id, "projects")),
        "judging": len(get_all_docs(id, "judging"))
    }
    return render_template("hackathon.html", data=data, checkedIn=checekdIn, counts=counts)
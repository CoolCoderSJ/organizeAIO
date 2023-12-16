from flask import render_template, session, redirect
from app import app, db, get_all_docs
from datetime import datetime

@app.route("/hackathon/<id>")
def hackathon(id):
    hacks = db.get(id)
    meta = db.get_document(hacks['$id'], "metadata", "data")
    today = datetime.date(datetime.now())
    try:
        daysLeft = abs(int(str(datetime.date(datetime.strptime(meta['startDate'], '%Y-%m-%dT%H:%M:%S.%f%z')) - today).split(" ")[0]))
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

    return render_template("hackathon.html", data=data)
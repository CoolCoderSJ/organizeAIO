from flask import render_template, session, redirect
from app import app, db, get_all_docs
from datetime import datetime

@app.route("/dashboard")
def dashboard():
    user = session['user']
    all_dbs = db.list(search=user)
    h = [hack for hack in all_dbs['databases']]
    all_dbs = db.list()
    for d in all_dbs['databases']:
        if d['$id'] == "data": continue
        metadata = db.get_document(d['$id'], "metadata", "data")
        if user in metadata['teamIds'] or metadata['judgeIds']:
            h.append(d)
            
    hackathons = []
    for hacks in h:
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
            "attendees": len(attendees)
        }
        hackathons.append(data)

    print(hackathons)
    return render_template("index.html", hackathons=hackathons)
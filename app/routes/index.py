from flask import render_template, session, redirect, request, flash
from app import app, db, get_all_docs, Query, storage
from datetime import datetime
import base64
from lxml.html.clean import clean_html

@app.route("/")
def index_route():
    host = request.host
    print(host)
    if not host.endswith("organizeaio.org") and not host.endswith("localhost:9738"):
        return redirect("https://organizeaio.org")
    if host.endswith("organizeaio.org"):
        slug = request.host.replace(".organizeaio.org", "")
    else:
        slug = request.host.replace(".localhost:9738", "")
    print(slug)
    
    if slug == "organizeaio.org" or slug == "localhost:9738":
        if 'user' in session:
            return redirect("/dashboard")
        return render_template("landing.html")

    hackathons = get_all_docs("data", "data", [Query.equal("slug", slug)])
    if len(hackathons) != 1:
        return redirect("https://organizeaio.org")
    hackathon = hackathons[0]
    hackathon_id = hackathon['hackathon_id']
    meta = db.get_document(hackathon_id, "metadata", "data")
    data = {
        "id": hackathon_id,
        "name": meta['name'],
    }

    meta['startDate'] = datetime.strptime(meta['startDate'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime("%a %b %d, %I:%M %p")
    meta['endDate'] = datetime.strptime(meta['endDate'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime("%a %b %d, %I:%M %p")    

    try:
        data['logo'] = base64.b64encode(storage.get_file_view(hackathon_id, meta['logoId'])).decode("utf-8")
    except Exception as e:
        print(e)
        data['logo'] = ""
    
    schedule = get_all_docs(hackathon_id, "schedule")
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
    
    try: meta['judgingCriteria'] = "<div class='text-white'>" + clean_html(meta['judgingCriteria']).replace("\n", "<br>")+"</div>"
    except: meta['judgingCriteria'] = ""

    return render_template("public.html", data=data, meta=meta, schedule=schedule)
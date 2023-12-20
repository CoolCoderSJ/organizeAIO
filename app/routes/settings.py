from flask import render_template, session, redirect, request, flash
from app import app, db, get_all_docs, Query, users, storage
from datetime import datetime

@app.get("/hackathon/<hid>/settings")
def settigns_get(hid):
    user = session['user']
    teamIds = db.get_document(hid, "metadata", "data")['teamIds']
    if not hid.startswith(user) and user not in teamIds:
        return abort(403)


    hacks = db.get(hid)
    meta = db.get_document(hacks['$id'], "metadata", "data")

    data = {
        "id": hacks['$id'],
        "name": meta['name'],
    }

    emails = {}
    for user in meta['teamIds']:
        emails[user] = users.get(user)['name']
    
    emails_j = {}
    for user in meta['judgeIds']:
        emails_j[user] = users.get(user)['name']

    slug = db.get_document("data", "data", hid)['slug']
    return render_template("settings.html", data=data, meta=meta, emails=emails, emails_j=emails_j, slug=slug)

@app.post("/hackathon/<hid>/settings")
def saveSettings(hid):
    user = session['user']
    teamIds = db.get_document(hid, "metadata", "data")['teamIds']
    if not hid.startswith(user) and user not in teamIds:
        return abort(403)
    
    data = {k: v for k, v in request.form.items()}

    slug = data['slug']
    del data['slug']

    db.update_document("data", "data", hid, {"slug": slug})
    
    teamEmails = data['teamIds'].replace(", ", ",").split(",")
    while True:
        try:
            teamEmails.remove("")
        except:
            break

    e = []
    print(teamEmails)
    for email in teamEmails:
        email = email.strip()
        user = users.list(search=email)['users'][0]['$id']
        e.append(user)
    data['teamIds'] = e

    judgeEmails = data['judgeIds'].replace(", ", ",").split(",")
    while True:
        try:
            judgeEmails.remove("")
        except:
            break
            
    e = []
    for email in judgeEmails:
        email = email.strip()
        user = users.list(search=email)['users'][0]['$id']
        e.append(user)
    data['judgeIds'] = e

    if 'file' in request.files:
        print("file found!")
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            print(os.getcwd())
            file.save(os.path.join("app/uploads", filename))
            result = storage.create_file(id, 'unique()', InputFile.from_path(os.path.join("app/uploads", filename)))
            data['logoId'] = result['$id']
            os.remove(os.path.join("app/uploads", filename))

    db.update_document(hid, "metadata", "data", data)
    flash("Settings saved!")
    return redirect(f"/hackathon/{hid}/settings")

@app.post("/hackathon/<hid>/delete")
def delete_h(hid):
    user = session['user']
    teamIds = db.get_document(hid, "metadata", "data")['teamIds']
    if not hid.startswith(user) and user not in teamIds:
        return abort(403)   
    
    db.delete(hid)
    storage.delete_bucket(hid)
    db.delete_document("data", "data", hid)
    return redirect("/")
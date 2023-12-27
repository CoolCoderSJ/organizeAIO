from flask import render_template, session, redirect, request, flash
from app import app, db, get_all_docs, Query
from datetime import datetime
import smtplib
from email.message import EmailMessage

@app.route('/hackathon/<hid>/messages')
def get_messages(hid):
    user = session['user']
    teamIds = db.get_document(hid, "metadata", "data")['teamIds']
    judgeIds = db.get_document(hid, "metadata", "data")['judgeIds']
    if user in judgeIds:
        return redirect("/hackathon/"+hid+"/judging")
    if not hid.startswith(user) and user not in teamIds:
        return abort(403)
    
    messages = get_all_docs(hid, "messages")
    meta = db.get_document(hid, "metadata", "data")

    data = {
        "id": hid,
        "name": meta['name'],
    }

    emailFields = get_all_docs(hid, "registration_form", [Query.equal("type", "email")])
    attributes = get_all_docs(hid, "registration_form")

    fieldToName = {
        "equal": "Equal To",
        "notEqual": "Not Equal To",
        "lessThan": "Less Than",
        "lessThanEqual": "Less Than or Equal To",
        "greaterThan": "Greater Than",
        "greaterThanEqual": "Greater Than or Equal To",
        "startsWith": "Starts With",
        "endsWith": "Ends With",
    }

    smtp_data = ['smtp_host', 'smtp_port', 'smtp_username', 'smtp_password', 'smtp_from', 'smtp_from_name', 'smtp_auth_method']
    for field in smtp_data:
        if not meta[field]:
            flash("Your SMTP settings are misconfigured. Blasts will not be sent until you fix SMTP settings under the settings page.")
            break
    
    if len(emailFields) == 0:
        flash("You don't have any email attributes. You won't be able to send email blasts until you add one.")

    return render_template('messages.html', messages=messages, data=data, emailFields=emailFields, meta=meta, attrs=attributes, fieldToName=fieldToName)

@app.post('/hackathon/<hid>/messages/new')
def send_message(hid):
    user = session['user']
    teamIds = db.get_document(hid, "metadata", "data")['teamIds']
    judgeIds = db.get_document(hid, "metadata", "data")['judgeIds']
    if user in judgeIds:
        return redirect("/hackathon/"+hid+"/judging")
    if not hid.startswith(user) and user not in teamIds:
        return abort(403)

    mailingList = []
    queries = []

    print(request.form)
    
    q = request.form['conditions'].replace("&quot;", '"').split("|")
    while True:
        try:
            q.remove("")
        except:
            break

    queries += q

    try:
        a = get_all_docs(hid, "attendees", queries)
    except:
        flash("Invalid queries")
        return redirect("/hackathon/"+hid+"/messages")

    for doc in a:
        for field in request.form['fields'].split("|"):
            if field in doc:
                if doc[field]:
                    mailingList.append(doc[field])

    message = request.form['message']
    subject = request.form['subject']

    meta = db.get_document(hid, "metadata", "data")

    if meta['smtp_auth_method'] == "ssl":
        server = smtplib.SMTP_SSL(meta['smtp_host'], meta['smtp_port'])
    else:
        server = smtplib.SMTP(meta['smtp_host'], meta['smtp_port'])
        server.starttls()
    
    server.login(meta['smtp_username'], meta['smtp_password'], initial_response_ok=True) 

    from_ = f"{meta['smtp_from_name']} <{meta['smtp_from']}>"
    msg = EmailMessage()
    msg.set_content(message)
    msg['From'] = from_
    msg['Subject'] = subject

    server.sendmail(from_, mailingList, msg.as_string())
    db.create_document(hid, "messages", "unique()", {
        "emailFields": request.form['fields'].split("|"),
        "conditions": q,
        "message": message,
        "subject": subject,
        "from": from_,
    })
    return redirect("/hackathon/"+hid+"/messages")
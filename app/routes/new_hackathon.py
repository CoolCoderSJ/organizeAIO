from flask import render_template, session, redirect, request
from app import app, db, get_all_docs, storage
from datetime import datetime
import uuid 

@app.route("/new/hackathon", methods=['POST'])
def new_hackathon():
    name = request.form.get("name")
    location = request.form.get("location")
    startDate = request.form.get("startDate")
    endDate = request.form.get("endDate")


    user = session['user']
    hackathon_id = f'{user}{name[:5]}'
    hackathon_id = ("".join([s for s in hackathon_id if s.isalnum()]) + str(uuid.uuid4().hex))[:36]

    storage.create_bucket(hackathon_id, hackathon_id, None, None, True, 10000000, None, None, None, True)
    
    db.create(hackathon_id, hackathon_id)
    db.create_collection(hackathon_id, "metadata", "metadata")
    db.create_collection(hackathon_id, "attendees", "attendees")
    db.create_collection(hackathon_id, "registration_form", "registration_form")
    db.create_collection(hackathon_id, "schedule", "schedule")
    db.create_collection(hackathon_id, "projects", "projects")
    db.create_collection(hackathon_id, "judging", "judging")
    db.create_collection(hackathon_id, "messages", "messages")

    db.create_string_attribute(hackathon_id, "metadata", "name", 200, False, name)
    db.create_datetime_attribute(hackathon_id, "metadata", "startDate", False, startDate)
    db.create_datetime_attribute(hackathon_id, "metadata", "endDate", False, endDate)
    db.create_string_attribute(hackathon_id, "metadata", "location", 200, False, location)
    db.create_string_attribute(hackathon_id, "metadata", "description", 500, False, None)
    db.create_string_attribute(hackathon_id, "metadata", "logoId", 999, False, None)
    db.create_string_attribute(hackathon_id, "metadata", "teamIds", 999, False, None, True)
    db.create_string_attribute(hackathon_id, "metadata", "judgeIds", 999, False, None, True)
    db.create_string_attribute(hackathon_id, "metadata", "judgingCriteria", 500, False, None)
    db.create_string_attribute(hackathon_id, "metadata", "slug", 100, False, None)
    # list of attribute keys from attendees collection, maintain order in list when rendering page
    db.create_string_attribute(hackathon_id, "metadata", "form_order", 999, False, None, True)
    ##############################################################################################
    db.create_string_attribute(hackathon_id, "metadata", "smtp_host", 100, False, None)
    db.create_string_attribute(hackathon_id, "metadata", "smtp_port", 100, False, None)
    db.create_string_attribute(hackathon_id, "metadata", "smtp_username", 100, False, None)
    db.create_string_attribute(hackathon_id, "metadata", "smtp_password", 100, False, None)
    db.create_string_attribute(hackathon_id, "metadata", "smtp_from", 100, False, None)
    db.create_string_attribute(hackathon_id, "metadata", "smtp_from_name", 100, False, None)
    # SSL OR STARTTLS
    db.create_string_attribute(hackathon_id, "metadata", "smtp_auth_method", 100, False, None)

    db.create_boolean_attribute(hackathon_id, "metadata", "showProjects", False, False)
    db.create_boolean_attribute(hackathon_id, "metadata", "showScores", False, False)
    db.create_boolean_attribute(hackathon_id, "metadata", "allowProjectCreation", False, True)
    db.create_string_attribute(hackathon_id, "metadata", "hcb_slug", 50, False, None)


    db.create_string_attribute(hackathon_id, "attendees", "name", 100, False, None)
    db.create_string_attribute(hackathon_id, "attendees", "email", 100, False, None)
    db.create_boolean_attribute(hackathon_id, "attendees", "checkedIn", False, False)


    db.create_string_attribute(hackathon_id, "registration_form", "field_name", 100, False, None)
    # one of - color, date, datetime-local, email, number, radio, range, tel, text, time, url
    db.create_string_attribute(hackathon_id, "registration_form", "type", 100, False, None)
    # for radios or range
    db.create_string_attribute(hackathon_id, "registration_form", "options", 100, False, None, True)
    db.create_string_attribute(hackathon_id, "registration_form", "placeholder", 100, False, None)
    db.create_string_attribute(hackathon_id, "registration_form", "default", 100, False, None)
    db.create_string_attribute(hackathon_id, "registration_form", "description", 500, False, None)
    db.create_boolean_attribute(hackathon_id, "registration_form", "required", False, False)


    db.create_string_attribute(hackathon_id, "schedule", "name", 100, False, None)
    db.create_datetime_attribute(hackathon_id, "schedule", "startDateTime", False)
    db.create_datetime_attribute(hackathon_id, "schedule", "endDateTime", False)
    db.create_string_attribute(hackathon_id, "schedule", "description", 999999, False, None)
    db.create_string_attribute(hackathon_id, "schedule", "location", 100, False, None)


    db.create_string_attribute(hackathon_id, "projects", "name", 100, False, None)
    db.create_string_attribute(hackathon_id, "projects", "owner", 9999, False, None, True)
    db.create_string_attribute(hackathon_id, "projects", "description", 999, False, None)
    db.create_url_attribute(hackathon_id, "projects", "links", False, None, True)
    db.create_string_attribute(hackathon_id, "projects", "coverId", 100, False, None)


    db.create_string_attribute(hackathon_id, "judging", "judgeId", 100, False, None)
    db.create_string_attribute(hackathon_id, "judging", "projectId", 100, False, None)
    db.create_string_attribute(hackathon_id, "judging", "score", 100, False, None)
    db.create_string_attribute(hackathon_id, "judging", "comment", 500, False, None)

    # one of - uncheckedin, checkedin, all_attendees
    db.create_string_attribute(hackathon_id, "messages", "emailFields", 100, False, None, True)
    db.create_string_attribute(hackathon_id, "messages", "conditions", 100, False, None, True)
    db.create_string_attribute(hackathon_id, "messages", "from", 100, False, None)
    db.create_string_attribute(hackathon_id, "messages", "message", 999, False, None)
    db.create_string_attribute(hackathon_id, "messages", "subject", 100, False, None)

    db.create_index(hackathon_id, 'attendees', 'checkedIn', 'key', ["checkedIn"], ['ASC'])
    db.create_index(hackathon_id, "attendees", "name", "key", ['name'], ['ASC'])
    db.create_index(hackathon_id, "attendees", "email", "key", ['email'], ['ASC'])
    db.create_index(hackathon_id, "registration_form", "type", "key", ['type'], ['ASC'])

    formField_name = db.create_document(hackathon_id, "registration_form", "unique()", {
        "field_name": "name",
        "type": "text",
        "options": [],
        "placeholder": "Enter your full name",
        "default": None,
        "required": True,
    })
    formField_email = db.create_document(hackathon_id, "registration_form", "unique()", {
        "field_name": "email",
        "type": "email",
        "options": [],
        "placeholder": "Enter your email",
        "default": None,
        "required": True,
    })

    db.create_document(hackathon_id, "metadata", "data", {
        "name": name,
        "startDate": startDate,
        "endDate": endDate,
        "location": location,
        "description": None,
        "logoId": None,
        "teamIds": [],
        "judgeIds": [],
        "judgingCriteria": None,
        "form_order": [formField_name['$id'], formField_email['$id']]
    })

    slug = "".join([s for s in name if s.isalnum() or s.isspace()]).replace(" ", "_")
    slug = slug.lower()
    if slug.endswith("_"): slug = slug[:-1]
    db.create_document("data", "data", hackathon_id, {
        "hackathon_id": hackathon_id,
        "slug": slug
    })


    return redirect("/hackathon/"+hackathon_id)
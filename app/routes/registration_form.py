from flask import render_template, session, redirect, request, flash
from app import app, db, get_all_docs, Query
from datetime import datetime
from time import sleep

@app.route("/register")
def public_registration():
    host = request.host
    print(host)
    if not host.endswith("organizeaio.xyz") and not host.endswith("localhost:9738"):
        return redirect("https://organizeaio.xyz")
    if host.endswith("organizeaio.xyz"):
        slug = request.host.replace(".organizeaio.xyz", "")
    else:
        slug = request.host.replace(".localhost:9738", "")
    print(slug)
    
    hackathons = get_all_docs("data", "data", [Query.equal("slug", slug)])
    if len(hackathons) != 1:
        return redirect("https://organizeaio.xyz")
    hackathon = hackathons[0]
    hackathon_id = hackathon['hackathon_id']
    meta = db.get_document(hackathon_id, "metadata", "data")
    data = {
        "id": hackathon_id,
        "name": meta['name'],
    }


    attributes = db.list_attributes(hackathon_id, 'attendees')

    registration = get_all_docs(hackathon_id, "registration_form") 
    order = meta['form_order']
    form_n = []
    for i in order:
        elem = next(item for item in registration if item["$id"] == i)
        form_n.append(elem)
    registration = form_n

    form = {}
    for item in registration:
        form[item['field_name']] = {
            "type": item['type'],
            "required": item['required'],
            "options": item['options'],
            "default": item['default'],
            "placeholder": item['placeholder'],
            "description": item['description']
        }

    print(attributes)
    attr_n = []
    for i in order:
        elem = next(item['field_name'] for item in registration if item["$id"] == i)
        elem = next(item for item in attributes['attributes'] if item["key"] == elem)
        print(elem)
        attr_n.append(elem)

    attributes['attributes'] = attr_n
    
    return render_template("public_registration.html", form=form, attrs=attributes, data=data)


@app.post("/register")
def public_register():
    host = request.host
    print(host)
    if not host.endswith("organizeaio.xyz") and not host.endswith("localhost:9738"):
        return redirect("https://organizeaio.xyz")
    if host.endswith("organizeaio.xyz"):
        slug = request.host.replace(".organizeaio.xyz", "")
    else:
        slug = request.host.replace(".localhost:9738", "")
    print(slug)
    hackathons = get_all_docs("data", "data", [Query.equal("slug", slug)])
    if len(hackathons) != 1:
        return redirect("https://organizeaio.xyz")
    hackathon = hackathons[0]
    hackathon_id = hackathon['hackathon_id']

    data = {k: v for k, v in request.form.items()}
    db.create_document(hackathon_id, "attendees", "unique()", data)

    flash("You have successfully been registered!")
    return redirect("/register")


@app.route("/hackathon/<hid>/form")
def registration_form(hid):
    user = session['user']
    teamIds = db.get_document(hid, "metadata", "data")['teamIds']
    judgeIds = db.get_document(hid, "metadata", "data")['judgeIds']
    if user in judgeIds:
        return redirect("/hackathon/"+hid+"/judging")
    if not hid.startswith(user) and user not in teamIds:
        return abort(403)

    form = get_all_docs(hid, "registration_form")
    hacks = db.get(hid)
    meta = db.get_document(hacks['$id'], "metadata", "data")

    data = {
        "id": hacks['$id'],
        "name": meta['name'],
    }
    order = meta['form_order']
    form_n = []
    print(form, order)
    for i in order:
        elem = next(item for item in form if item["$id"] == i)
        form_n.append(elem)
    return render_template("registration_form.html", form=form_n, data=data)

@app.post("/hackathon/<hackathon_id>/form/delete/<form_id>")
def delete_form_field(hackathon_id, form_id):
    user = session['user']
    teamIds = db.get_document(hackathon_id, "metadata", "data")['teamIds']
    if not hackathon_id.startswith(user) and user not in teamIds:
        return abort(403)

    field_name = db.get_document(hackathon_id, "registration_form", form_id)['field_name']
    order = db.get_document(hackathon_id, "metadata", "data")['form_order']
    order.remove(form_id)
    db.update_document(hackathon_id, "metadata", "data", {
        "form_order": order
    })
    db.delete_document(hackathon_id, "registration_form", form_id)
    db.delete_attribute(hackathon_id, "attendees", field_name)
    try: db.delete_index(hackathon_id, "attendees", field_name)
    except: pass
    return redirect(f"/hackathon/{hackathon_id}/form")

@app.post("/hackathon/<hackathon_id>/form/edit/<form_id>")
def edit_form_field(hackathon_id, form_id):
    user = session['user']
    teamIds = db.get_document(hackathon_id, "metadata", "data")['teamIds']
    if not hackathon_id.startswith(user) and user not in teamIds:
        return abort(403)

    data = {k: v for k, v in request.form.items()}
    data['options'] = data['options'].replace(", ", ",").split(',')
    if data['required'] == "Yes": data['required'] = True
    else: data['required'] = False
    data['field_name'] = "".join([s for s in data['field_name'] if s.isalnum()])
    db.update_document(hackathon_id, "registration_form", form_id, data)
    attributes = db.list_attributes(hackathon_id, "attendees")['attributes']
    listOfAttributes = [attribute['key'] for attribute in attributes]
    listOfAttributes.remove("checkedIn")

    docs = get_all_docs(hackathon_id, "registration_form")
    listOfCurrentAttrs = [doc['field_name'] for doc in docs]

    notInCurrent = [attr for attr in listOfAttributes if attr not in listOfCurrentAttrs]

    if len(notInCurrent) > 0:
        db.delete_attribute(hackathon_id, "attendees", notInCurrent[0])
        db.delete_index(hackathon_id, "attendees", notInCurrent[0])
        db.create_string_attribute(hackathon_id, "attendees", data['field_name'], 100, False, None)
        sleep(0.5)
        db.create_index(hackathon_id, "attendees", data['field_name'], "key", [data['field_name']], ['ASC'])
    return redirect(f"/hackathon/{hackathon_id}/form")

@app.post("/hackathon/<hackathon_id>/form/add")
def add_form_field(hackathon_id):
    user = session['user']
    teamIds = db.get_document(hackathon_id, "metadata", "data")['teamIds']
    if not hackathon_id.startswith(user) and user not in teamIds:
        return abort(403)

    data = {k: v for k, v in request.form.items()}
    data['options'] = data['options'].replace(", ", ",").split(',')
    if data['required'] == "Yes": data['required'] = True
    else: data['required'] = False
    data['field_name'] = "".join([s for s in data['field_name'] if s.isalnum()])
    order = db.get_document(hackathon_id, "metadata", "data")['form_order']
    data = db.create_document(hackathon_id, "registration_form", "unique()", data)
    order.append(data['$id'])
    db.update_document(hackathon_id, "metadata", "data", {
        "form_order": order
    })
    db.create_string_attribute(hackathon_id, "attendees", data['field_name'], 100, False, None)
    sleep(0.5)
    db.create_index(hackathon_id, "attendees", data['field_name'], "key", [data['field_name']], ['ASC'])
    return redirect(f"/hackathon/{hackathon_id}/form")

@app.post("/hackathon/<hackathon_id>/reorder")
def reorder_form_fields(hackathon_id):
    user = session['user']
    teamIds = db.get_document(hackathon_id, "metadata", "data")['teamIds']
    if not hackathon_id.startswith(user) and user not in teamIds:
        return abort(403)
        
    order = request.form['order']
    print(order)
    if not order: return redirect(f"/hackathon/{hackathon_id}/form")
    db.update_document(hackathon_id, "metadata", "data", {
        "form_order": order.split(",")
    })
    return redirect(f"/hackathon/{hackathon_id}/form")
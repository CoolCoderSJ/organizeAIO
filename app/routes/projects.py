from flask import render_template, session, redirect, request, flash
from app import app, db, get_all_docs, Query, storage
from appwrite.input_file import InputFile
from datetime import datetime
import base64, os
from werkzeug.utils import secure_filename

@app.route('/hackathon/<hid>/projects')
def projects(hid):
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
        "showProjects": meta['showProjects'],
        "allowProjectCreation": meta['allowProjectCreation']
    }
    projects = get_all_docs(hid, "projects")
    images = {}
    for project in projects:
        try:
            images[project['$id']] = base64.b64encode(storage.get_file_view(hid, project['coverId'])).decode("utf-8")
        except:
            images[project['$id']] = ""
            
    return render_template("projects.html", projects=projects, data=data, images=images)

@app.post("/hackathon/<id>/projects/show")
def show_projects(id):
    user = session['user']
    teamIds = db.get_document(id, "metadata", "data")['teamIds']
    if not id.startswith(user) and user not in teamIds:
        return abort(403)
    
    data = {
        "showProjects": True
    }
    db.update_document(id, "metadata", "data", data)
    return redirect(f"/hackathon/{id}/projects")

@app.post("/hackathon/<id>/projects/hide")
def hide_projects(id):
    user = session['user']
    teamIds = db.get_document(id, "metadata", "data")['teamIds']
    if not id.startswith(user) and user not in teamIds:
        return abort(403)
    
    data = {
        "showProjects": False
    }
    db.update_document(id, "metadata", "data", data)
    return redirect(f"/hackathon/{id}/projects")


@app.post("/hackathon/<id>/projects/allowcreation")
def allowcreation(id):
    user = session['user']
    teamIds = db.get_document(id, "metadata", "data")['teamIds']
    if not id.startswith(user) and user not in teamIds:
        return abort(403)
    
    data = {
        "allowProjectCreation": True
    }
    db.update_document(id, "metadata", "data", data)
    return redirect(f"/hackathon/{id}/projects")

@app.post("/hackathon/<id>/projects/dontallowcreation")
def dontallowcreation(id):
    user = session['user']
    teamIds = db.get_document(id, "metadata", "data")['teamIds']
    if not id.startswith(user) and user not in teamIds:
        return abort(403)
    
    data = {
        "allowProjectCreation": False
    }
    db.update_document(id, "metadata", "data", data)
    return redirect(f"/hackathon/{id}/projects")



@app.post('/hackathon/<id>/projects/delete/<project_id>')
def delete_project(id, project_id):
    user = session['user']
    teamIds = db.get_document(id, "metadata", "data")['teamIds']
    if not id.startswith(user) and user not in teamIds:
        return abort(403)

    db.delete_document(id, "projects", project_id)
    return redirect(f"/hackathon/{id}/projects")

@app.get('/projects')
def create_project_get():
    host = request.host
    print(host)
    if not host.endswith("organizeaio.org") and not host.endswith("localhost:9738"):
        return redirect("https://organizeaio.org")
    if host.endswith("organizeaio.org"):
        slug = request.host.replace(".organizeaio.org", "")
    else:
        slug = request.host.replace(".localhost:9738", "")
    print(slug)
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

    projects = get_all_docs(hackathon_id, "projects")
    if not meta['showProjects']: projects = []
    images = {}
    for project in projects:
        try:
            images[project['$id']] = base64.b64encode(storage.get_file_view(hackathon_id, project['coverId'])).decode("utf-8")
        except:
            images[project['$id']] = ""
            
    return render_template("public_project.html", data=data, meta=meta, projects=projects, images=images)


@app.post('/projects/new')
def create_project():
    host = request.host
    if not host.endswith("organizeaio.org") and not host.endswith("localhost:9738"):
        return redirect("https://organizeaio.org")
    if host.endswith("organizeaio.org"):
        slug = request.host.replace(".organizeaio.org", "")
    else:
        slug = request.host.replace(".localhost:9738", "")
    print(slug)
    hackathons = get_all_docs("data", "data", [Query.equal("slug", slug)])
    if len(hackathons) != 1:
        return redirect("https://organizeaio.org")
    hackathon = hackathons[0]
    hackathon_id = hackathon['hackathon_id']

    data = {k: v for k, v in request.form.items()}
    data['owner'] = data['owner'].replace(", ", ",").split(",")
    data['links'] = data['links'].replace(", ", ",").split(",")
    if 'file' in request.files:
        print("file found!")
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            print(os.getcwd())
            file.save(os.path.join("app/uploads", filename))
            result = storage.create_file(hackathon_id, 'unique()', InputFile.from_path(os.path.join("app/uploads", filename)))
            data['coverId'] = result['$id']
            os.remove(os.path.join("app/uploads", filename))


    db.create_document(hackathon_id, "projects", "unique()", data)
    flash("Project created successfully")
    return redirect(f"/projects")

@app.post('/hackathon/<id>/projects/edit/<project_id>')
def edit_project(id, project_id):
    user = session['user']
    teamIds = db.get_document(id, "metadata", "data")['teamIds']
    if not id.startswith(user) and user not in teamIds:
        return abort(403)

    data = {k: v for k, v in request.form.items()}
    data['owner'] = data['owner'].replace(", ", ",").split(",")
    data['links'] = data['links'].replace(", ", ",").split(",")
    if 'file' in request.files:
        print("file found!")
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            print(os.getcwd())
            file.save(os.path.join("app/uploads", filename))
            result = storage.create_file(id, 'unique()', InputFile.from_path(os.path.join("app/uploads", filename)))
            data['coverId'] = result['$id']
            os.remove(os.path.join("app/uploads", filename))

    db.update_document(id, "projects", project_id, data)
    return redirect(f"/hackathon/{id}/projects")

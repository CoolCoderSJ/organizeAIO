from flask import render_template, session, redirect, request, flash
from app import app, db, get_all_docs, Query, storage
from appwrite.input_file import InputFile
from datetime import datetime
import base64, os
from werkzeug.utils import secure_filename

@app.route('/hackathon/<hid>/projects')
def projects(hid):
    hacks = db.get(hid)
    meta = db.get_document(hacks['$id'], "metadata", "data")

    data = {
        "id": hacks['$id'],
        "name": meta['name'],
    }
    projects = get_all_docs(hid, "projects")
    images = {}
    for project in projects:
        images[project['$id']] = base64.b64encode(storage.get_file_view(hid, project['coverId'])).decode("utf-8")

    return render_template("projects.html", projects=projects, data=data, images=images)

@app.post('/hackathon/<id>/projects/delete/<project_id>')
def delete_project(id, project_id):
    db.delete_document(id, "projects", project_id)
    return redirect(f"/hackathon/{id}/projects")

@app.post('/projects/new')
def create_project():
    host = request.host
    if not host.endswith("organizeaio.xyz"):
        return redirect("https://organizeaio.xyz")
    slug = request.host.replace("organizeaio.xyz", "")
    hackathons = db.list_documents("data", "data", [Query.equal("slug", slug)])['documents']
    if len(hackathons) != 1:
        return redirect("https://organizeaio.xyz")
    hackathon = hackathons[0]
    hackathon_id = hackathon['hackathon_id']

    data = {k: v for k, v in request.form.items()}
    db.create_document(hackathon_id, "projects", "unique()", data)
    flash("Project created successfully")
    return redirect(f"/projects")

@app.post('/hackathon/<id>/projects/edit/<project_id>')
def edit_project(id, project_id):
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

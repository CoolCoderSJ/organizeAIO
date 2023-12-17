from flask import render_template, session, redirect, request, flash
from app import app, db, get_all_docs, Query
from datetime import datetime

@app.route('/hackathon/<id>/projects')
def projects(id):
    projects = get_all_docs(id, "projects")
    return render_template("projects.html", projects=projects)

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
    db.update_document(id, "projects", project_id, data)
    return redirect(f"/hackathon/{id}/projects")

@app.post('/hackathon/<id>/projects/add')
def add_project(id):
    data = {k: v for k, v in request.form.items()}
    db.create_document(id, "projects", "unique()", data)
    return redirect(f"/hackathon/{id}/projects")
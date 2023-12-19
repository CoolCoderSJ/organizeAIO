from flask import render_template, session, redirect, request, flash
from app import app, db, get_all_docs, Query
from datetime import datetime

@app.route("/hackathon/<hid>/judging")
def judging(hid):
    user = session['user']
    teamIds = db.get_document(hid, "metadata", "data")['teamIds']
    judgeIds = db.get_document(hid, "metadata", "data")['judgeIds']
    if not hid.startswith(user) and user not in teamIds and user not in judgeIds:
        return abort(403)
        
    projects = get_all_docs(hid, "projects")
    return render_template("judging.html", projects=projects)

@app.post("/hackathon/<hid>/judging/submitScore/<projectId>")
def submitScore(hid, projectId):
    user = session['user']
    teamIds = db.get_document(hid, "metadata", "data")['teamIds']
    judgeIds = db.get_document(hid, "metadata", "data")['judgeIds']
    if not hid.startswith(user) and user not in teamIds and user not in judgeIds:
        return abort(403)

    judgeId = session['user']
    score, comment = request.form['score'], request.form['comment']
    score = int(score)
    db.create_document(hid, "judging", "unique()", {
        "judgeId": judgeId,
        "projectId": projectId,
        "score": score,
        "comment": comment
    })
    return redirect("/hackathon/" + hid + "/judging")

@app.post("/hackathon/<hid>/judging/updateScore/<projectId>")
def updateScore(hid, projectId):
    user = session['user']
    teamIds = db.get_document(hid, "metadata", "data")['teamIds']
    judgeIds = db.get_document(hid, "metadata", "data")['judgeIds']
    if not hid.startswith(user) and user not in teamIds and user not in judgeIds:
        return abort(403)

    judgeId = session['user']
    score, comment = request.form['score'], request.form['comment']
    score = int(score)
    scoreId = request.form['scoreId']
    db.update_document(hid, "judging", scoreId, {
        "judgeId": judgeId,
        "projectId": projectId,
        "score": score,
        "comment": comment
    })
    return redirect("/hackathon/" + hid + "/judging")

@app.post("/hackathon/<hid>/judging/deleteScore/<scoreId>")
def deleteScore(hid, scoreId):
    user = session['user']
    teamIds = db.get_document(hid, "metadata", "data")['teamIds']
    judgeIds = db.get_document(hid, "metadata", "data")['judgeIds']
    if not hid.startswith(user) and user not in teamIds and user not in judgeIds:
        return abort(403)
        
    db.delete_document(hid, "judging", scoreId)
    return redirect("/hackathon/" + hid + "/judging")
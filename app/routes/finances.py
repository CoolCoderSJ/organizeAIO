from flask import render_template, session, redirect, request, flash
from app import app, db, get_all_docs, Query
import requests

@app.route('/hackathon/<hid>/finances')
def finances(hid):
    user = session['user']
    teamIds = db.get_document(hid, "metadata", "data")['teamIds']
    judgeIds = db.get_document(hid, "metadata", "data")['judgeIds']
    if user in judgeIds:
        return redirect("/hackathon/"+hid+"/judging")
    if not hid.startswith(user) and user not in teamIds:
        return abort(403)
    
    page = request.args.get("page", 1)
    page = int(page)
    if page <= 0: page = 1
    
    meta = db.get_document(hid, "metadata", "data")

    data = {
        "id": hid,
        "name": meta['name'],
    }

    hcb_slug = meta['hcb_slug']
    transactions = []
    total = "$0"
    raised = "$0"

    if hcb_slug:
        r = requests.get(f"https://hcb.hackclub.com/api/v3/organizations/{hcb_slug}") 
        org = r.json()
        total = '${:,.2f}'.format(org['balances']['balance_cents']/100)
        raised = '${:,.2f}'.format(org['balances']['total_raised']/100)

        t = requests.get(f"https://hcb.hackclub.com/api/v3/organizations/{hcb_slug}/transactions?page={page}")
        if t.status_code != 200: return redirect(f"/hackathon/{hid}/finances?page={page-1}")
        t = t.json()
        if len(t) == 0 and page > 1: return redirect(f"/hackathon/{hid}/finances?page={page-1}")
        for transaction in t:
            transactions.append({
                "memo": transaction['memo'],
                "amt": '${:,.2f}'.format(transaction['amount_cents']/100).replace("$-", "-$"),
                "date": transaction['date'],
                "negative": transaction['amount_cents'] < 0
            })
    else:
        flash("This hackathon is not connected to a HCB account. Connect one from the settings page.")

    return render_template("finances.html", data=data, transactions=transactions, total=total, raised=raised, page=page, slug=hcb_slug)
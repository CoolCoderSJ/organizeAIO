from flask import Flask, session, request, redirect
from flask_session import Session

from dotenv import load_dotenv
import os 

from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.id import ID
from appwrite.services.storage import Storage
from appwrite.services.users import Users

load_dotenv(".env")


client = Client()
client.set_endpoint(os.environ['APPWRITE_HOST'])
client.set_project(os.environ['APPWRITE_ID'])
client.set_key(os.environ['APPWRITE_KEY'])
db = Databases(client)
storage = Storage(client)
users = Users(client)


app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem" 
app.config["SECRET_KEY"] = os.environ['SECRET_KEY']
app.config["SESSION_PERMANENT"] = True
Session(app)

@app.before_request
def before_request():
    if 'user' not in session and request.path not in ['', '/', '/login', '/register', '/logout'] and not request.path.startswith("static") and not request.path.startswith("project"):
        return redirect("/")

def get_all_docs(data, collection, queries=[]):
    docs = []
    offset = 0
    queries.append(Query.offset(offset))
    queries.append(Query.limit(100))
    while True:
        results = db.list_documents(data, collection, queries=queries)
        if len(docs) == results['total']:
            break
        results = results['documents']
        docs += results
        offset += len(results)
    return docs

from .routes import *
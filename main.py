from app import app
from dotenv import load_dotenv
load_dotenv(".env")

import eventlet
from eventlet import wsgi

wsgi.server(eventlet.listen(('0.0.0.0', 9738)), app)
# app.run(host='0.0.0.0', port=9738, debug=True)
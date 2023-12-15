#!/home/user/myapp/organizeAIO/env/bin/python
import logging, sys
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

from app import app
from dotenv import load_dotenv
load_dotenv(".env")

port = sys.argv[1]
app.run(host="0.0.0.0", port=port, debug=True)
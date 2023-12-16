from app import app
from dotenv import load_dotenv
load_dotenv(".env")

app.run(host="0.0.0.0", port=9738, debug=True)
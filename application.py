import os

from flask import Flask, render_template
from flask_session import Session

from display import display
from manage import manage

app = Flask(__name__)

# Config session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Exception if DB_PATH not set
if not os.environ.get("DB_PATH"):
    raise RuntimeError("DB_PATH not set")

# Register blueprint
app.register_blueprint(display, url_prefix="/display")
app.register_blueprint(manage, url_prefix="/manage")

@app.route("/")
def webindex():
    return render_template("index.html")

import os

from flask import redirect, request, session, render_template
from functools import wraps
import sqlite3

# Config db connection
dbpath = os.getenv("DB_PATH")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/manage/login")
        return f(*args, **kwargs)
    return decorated_function


def validate_signage_owner(sid, username):
    # Query DB
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute("SELECT signageid FROM signages WHERE signageid=? AND username=?", (sid, username))
    signage = c.fetchone()
    conn.close()

    # Return value
    if signage is None:
        return False
    else:
        return True

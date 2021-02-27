import os

from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

display = Blueprint("display", __name__)

# Config db connection
dbpath = os.getenv("DB_PATH")

@display.route("")
def index():
    return render_template("display/index.html")


@display.route("begin", methods=["GET", "POST"])
def begin():
    if request.method == "POST":
        if not request.form.get("signageid") or not request.form.get("signagepw"):
            return render_template("display/error.html", msg="Please enter a Signage ID and password.")

        # Check for Signage ID in database
        sid = request.form.get("signageid").upper()
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute("SELECT COUNT(signageid) AS \"COUNT(signageid)\", password FROM signages WHERE signageid=?", (sid,))
        q = c.fetchone()
        conn.close()

        if q[0] == 0:
            return render_template("display/error.html", msg="Signage ID not found.")

        if q[1] is not None:
            if not check_password_hash(q[1], request.form.get("signagepw")):
                return render_template("display/error.html", msg="Incorrect password.")
        else:
            return render_template("display/error.html", msg="Signage could not be displayed.")

        # Save hide cursor option
        if request.form.get("hidecursor") is not None:
            session["hidecursor"] = 1
        else:
            session["hidecursor"] = 0

        session["signageid"] = sid
        return redirect("/display/show")
    else:
        return redirect("/display")


@display.route("show")
def show():
    if session.get("signageid") is None or session.get("hidecursor") is None:
        return redirect("/display")
    sid = session["signageid"]
    cursoroption = session.get("hidecursor")

    # Pop session
    session.pop("signageid")
    session.pop("hidecursor")

    # Set cursor option
    if cursoroption == 1:
        cursor = "none"
    else:
        cursor = "default"


    # Query for special css
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute("SELECT specialcss FROM signages WHERE signageid=?", (sid,))
    q = c.fetchone()
    specialcss = q[0]

    # Query for slides
    c = conn.cursor()
    c.execute("SELECT imageurl, dduration FROM slides WHERE signageid=? ORDER BY iindex ASC", (sid,))
    slides = c.fetchall()
    conn.close()

    if len(slides) < 1:
        return render_template("display/error.html", msg="Signage doesn't contain any slide.")

    return render_template("display/show.html", signageid=sid, slides=slides, css=specialcss, cursor=cursor)

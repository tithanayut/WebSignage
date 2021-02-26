import os

from flask import Blueprint, render_template, request, redirect, session
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
        if not request.form.get("signageid"):
            return render_template("display/error.html", msg="Please enter a Signage ID.")

        # Check for Signage ID in database
        sid = request.form.get("signageid").upper()
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute("SELECT COUNT(signageid) AS \"COUNT(signageid)\" FROM signages WHERE signageid=?", (sid,))
        q = c.fetchone()

        if q[0] == 0:
            return render_template("display/error.html", msg="Signage ID not found.")
        else:
            session["signageid"] = sid
            return redirect("/display/show")
    else:
        return redirect("/display")


@display.route("show")
def show():
    if not session["signageid"]:
        return redirect("/display")

    # Query for slides
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute("SELECT imageurl, dduration FROM slides WHERE signageid=? ORDER BY iindex ASC", (session["signageid"],))
    slides = c.fetchall()
    conn.close()

    if len(slides) < 1:
        return render_template("display/error.html", msg="Signage doesn't contain any slide.")

    return render_template("display/show.html", signageid=session["signageid"], slides=slides)

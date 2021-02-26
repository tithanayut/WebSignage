from flask import Blueprint, render_template, request, redirect, session
import sqlite3

display = Blueprint("display", __name__)

# Config db connection
dbpath = "database.db"

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
            session["signageid"] = request.form.get("signageid")
            return redirect("/display/show")
    else:
        return redirect("/display")

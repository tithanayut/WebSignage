import os

from flask import Blueprint, render_template, request, redirect, session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

from auth import login_required

# Config db connection
dbpath = os.getenv("DB_PATH")

manage = Blueprint("manage", __name__)

@manage.route("")
@login_required
def index():
    return render_template("manage/index.html")


@manage.route("login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        # Check for username and password
        if not request.form.get("username"):
            return render_template("manage/error.html", msg="Please enter a username.")
        elif not request.form.get("password"):
            return render_template("manage/error.html", msg="Please enter a password.")

        # Connect db and validate user
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute("SELECT username, hash FROM users WHERE username = ?", (request.form.get("username"),))
        q = c.fetchall()
        conn.close()

        if len(q) != 1 or not check_password_hash(q[0][1], request.form.get("password")):
            return render_template("manage/error.html", msg="Invalid username and/or password.")

        # Set session
        session["user_id"] = q[0][0]

        return redirect("/manage")
    else:
        return render_template("manage/login.html")


@manage.route("logout")
def logout():
    session.clear()
    return redirect("/manage")


@manage.route("register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get user's input
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate input
        if not username or not password or not confirmation:
            return render_template("manage/error.html", msg="Please complete the form.")
        if password != confirmation:
            return render_template("manage/error.html", msg="Passwords do not match.")

        # Connect db and check for duplicate username
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute("SELECT COUNT(id) AS \"COUNT(id)\" FROM users WHERE username=?", (username,))
        q = c.fetchone()

        if q[0] != 0:
            conn.close()
            return render_template("manage/error.html", msg="This username already exists")

        # Add user to database
        c.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, generate_password_hash(password)))
        conn.commit()

        conn.close()

        return redirect("login")
    else:
        return render_template("manage/register.html")


@manage.route("view")
@login_required
def view():
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute("SELECT signageid, description FROM signages WHERE username=?", (session["user_id"],))
    signages = c.fetchall()
    conn.close()
    return render_template("manage/view.html", signages=signages)


@manage.route("delete", methods=["GET", "POST"])
@login_required
def delete():
    if request.method == "POST":
        if not request.form.get("signageid"):
            return redirect("/manage/view")
        sid = request.form.get("signageid")

        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute("SELECT COUNT(id) AS \"COUNT(id)\" FROM signages WHERE username=? AND signageid=?", (session["user_id"], sid))
        q = c.fetchone()

        if q[0] == 0:
            conn.close()
            return render_template("manage/error.html", msg="Failed to delete signage.")

        c.execute("DELETE FROM signages WHERE signageid=?", (sid,))
        c.execute("DELETE FROM slides WHERE signageid=?", (sid,))
        conn.commit()

        conn.close()

        return redirect("/manage/view")
    else:
        if not request.args.get("id"):
            return redirect("/manage/view")
        return render_template("manage/delete.html", signageid=request.args.get("id"))


@manage.route("create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        # Check for user's input
        if not request.form.get("signageid") or not request.form.get("signagepw") or not request.form.get("description"):
            return render_template("manage/error.html", msg="Please complete the form.")

        sid = request.form.get("signageid").upper()
        spw = request.form.get("signagepw")
        description = request.form.get("description")

        # Check if Signage ID duplicate
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute("SELECT COUNT(id) AS \"COUNT(id)\" FROM signages WHERE signageid=?", (sid,))
        q = c.fetchone()

        if q[0] != 0:
            conn.close()
            return render_template("manage/error.html", msg="This Signage ID already exists")

        # Hash password
        spw_hashed = generate_password_hash(spw)

        # Add user to database
        c.execute("INSERT INTO signages (signageid, username, description, password) VALUES (?, ?, ?, ?)", (sid, session["user_id"], description, spw_hashed))
        conn.commit()

        conn.close()

        return redirect("/manage/view")
    else:
        return render_template("manage/create.html")


@manage.route("edit", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == "POST":
        # Check for user's input
        if not request.form.get("signageid") or not request.form.get("description"):
            return render_template("manage/error.html", msg="Please complete the form.")

        sid_old = request.form.get("signageid_old").upper()
        sid_new = request.form.get("signageid").upper()
        spw = request.form.get("signagepw")
        scss = request.form.get("specialcss")
        description = request.form.get("description")

        # Check owner
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute("SELECT signageid FROM signages WHERE signageid=? AND username=?", (sid_old, session["user_id"]))
        signage = c.fetchone()

        if signage is None:
            conn.close()
            return render_template("manage/error.html", msg="This signage cannot be edited.")

        # Check if Signage ID duplicate
        c.execute("SELECT COUNT(id) AS \"COUNT(id)\" FROM signages WHERE signageid=?", (sid_new,))
        q = c.fetchone()

        if q[0] != 0 and sid_old != sid_new:
            conn.close()
            return render_template("manage/error.html", msg="This Signage ID already exists")

        # Change password if requested
        if spw != "":
            spw_hashed = generate_password_hash(spw)
            c.execute("UPDATE signages SET signageid=?, description=?, password=?, specialcss=? WHERE signageid=?", (sid_new, description, spw_hashed, scss, sid_old))
        else:
            c.execute("UPDATE signages SET signageid=?, description=?, specialcss=? WHERE signageid=?", (sid_new, description, scss, sid_old))

        conn.commit()
        conn.close()

        return redirect("/manage/view")
    else:
        if not request.args.get("id"):
            return redirect("/manage/view")

        sid = request.args.get("id").upper()

        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute("SELECT signageid, description, specialcss FROM signages WHERE signageid=? AND username=?", (sid, session["user_id"]))
        signage = c.fetchone()
        conn.close()

        if signage is None:
            return render_template("manage/error.html", msg="This signage cannot be edited.")

        signageid = signage[0]
        description = signage[1]
        if signage[2] is not None:
            scss = signage[2]
        else:
            scss = ""

        return render_template("manage/edit.html", signageid=signageid, description=description, scss=scss)


@manage.route("slide")
@login_required
def slide():
    if not request.args.get("id"):
        return redirect("/manage/view")

    sid = request.args.get("id")

    # Check owner
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute("SELECT signageid FROM signages WHERE signageid=? AND username=?", (sid, session["user_id"]))
    signage = c.fetchone()

    if signage is None:
        conn.close()
        return render_template("manage/error.html", msg="This signage cannot be edited.")

    # Query slide
    c.execute("SELECT iindex, imageurl, dduration FROM slides WHERE signageid=? ORDER BY iindex, id ASC", (sid,))
    slides = c.fetchall()
    conn.close()

    return render_template("manage/slide.html", slides=slides, signageid=sid)


@manage.route("slide/add", methods=["GET", "POST"])
@login_required
def slide_add():
    if request.method == "POST":
        # Check for user's input
        if not request.form.get("signageid") or not request.form.get("sindex") or not request.form.get("surl") or not request.form.get("sduration"):
            return render_template("manage/error.html", msg="Please complete the form.")

        sid = request.form.get("signageid")
        surl = request.form.get("surl")

        # Validate index and duration
        try:
            sduration = int(request.form.get("sduration"))
            sindex = float(request.form.get("sindex"))
            if sduration < 0 or sindex < 0:
                return render_template("manage/error.html", msg="Duration/Index value is invalid.")
        except ValueError:
            return render_template("manage/error.html", msg="Duration/Index value is invalid.")

        # Check owner
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute("SELECT signageid FROM signages WHERE signageid=? AND username=?", (sid, session["user_id"]))
        signage = c.fetchone()

        if signage is None:
            conn.close()
            return render_template("manage/error.html", msg="This signage cannot be edited.")

        # Add slide to database
        c.execute("INSERT INTO slides (signageid, iindex, imageurl, dduration) VALUES (?, ?, ?, ?)", (sid, sindex, surl, sduration))
        conn.commit()
        conn.close()

        return redirect("/manage/slide?id=" + sid)
    else:
        if not request.args.get("id"):
            return redirect("/manage/view")

        sid = request.args.get("id")

        return render_template("manage/slide/add.html", signageid=sid)

from flask import Blueprint, render_template, request, redirect, session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

from auth import login_required

# Config db connection
dbpath = "database.db"

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

        if len(q) != 1 or not check_password_hash(q[0][1], request.form.get("password")):
            return render_template("manage/error.html", msg="Invalid username and/or password.")
        conn.close()

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

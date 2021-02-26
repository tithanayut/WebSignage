from flask import Blueprint, render_template, request, redirect, session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from auth import login_required

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

        # Validate user

        # Set session
        session["user_id"] = 1

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
        # Get user input
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate input

        # Check for duplicate username

        # Add user to database

        return redirect("login")
    else:
        return render_template("manage/register.html")

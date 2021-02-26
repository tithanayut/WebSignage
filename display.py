from flask import Blueprint, render_template, request, redirect

display = Blueprint("display", __name__)

@display.route("")
def index():
    return render_template("display/index.html")


@display.route("begin", methods=["GET", "POST"])
def begin():
    if request.method == "POST":
        if not request.form.get("signageid"):
            return render_template("display/error.html", msg="Please enter a Signage ID.")

        # Check for Signage ID in database
        # if found display
        # if not error
    else:
        return redirect("/display")

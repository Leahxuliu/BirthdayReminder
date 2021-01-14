import os

from sqlite3 import *
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from helpers import apology, login_required

from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from datetime import date

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# open sql
conn = connect('birthdays2.db', check_same_thread = False)
db = conn.cursor()



@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # get username
    username = db.execute("SELECT username FROM users WHERE id = (?)", (int(session['user_id']),)).fetchone()[0]
    # get today
    today = date.today()
    todayStr = str(today.month) + '/' + str(today.day)

    if request.method == "POST":
        name = request.form.get("Name")
        month = request.form.get("Month")
        day = request.form.get("Day")
        db.execute("INSERT INTO birthdays (username, name, month, day) VALUES (?, ?, ?, ?)", (username, name, month, day))
        conn.commit()
        return redirect("/")

    else:
        data = db.execute("SELECT * FROM birthdays WHERE username = (?)", (username, ))
        birthday_data = []
        today_birthday = []
        for each in data:
            data = {}
            data['name'] = str(each[2])
            data['birthday'] = "%s/%s" % (each[3], each[4])
            birthday_data.append(data)

            if data['birthday'] == todayStr:
                today_birthday.append(data['name'])

        today_birthday = ', '.join(today_birthday)
        return render_template("index.html", birthday_data = birthday_data, today_birthday = today_birthday)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = (?)", (request.form.get("username"),)).fetchone()

        # Ensure username exists and password is correct
        if rows == None or not check_password_hash(rows[2], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Unvalid
        if not request.form.get("username"):
            return apology("must provide username", 400)
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif request.form.get("password") != request.form.get("password2"):
            return apology("your passwords don't match", 400)
        
        cheak_Usename = db.execute("SELECT * FROM users WHERE username = ?", [request.form.get("username")])
        if cheak_Usename.fetchone() != None:
            return apology("username unavailable", 400)
        
        cheak_Email = db.execute("SELECT * FROM users WHERE email = ?", [request.form.get("Email")])
        if cheak_Email.fetchone() != None:
            return apology("Email unavailable", 400)

        # Insert username and hash of password in the database
        result = db.execute("INSERT INTO users (username, hash, email) VALUES (?, ?, ?)",
                            (request.form.get("username"), generate_password_hash(request.form.get("password")), request.form.get("email")))
        conn.commit()

        # Start session
        rows = db.execute("SELECT * FROM users WHERE username = (?)", (request.form.get("username"), ))

        # Remember which user has logged in
        session["user_id"] = rows.fetchone()[0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
    

app.run()

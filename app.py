import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

# Configure application
app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///diet.db")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)


@app.route("/signin", methods=["GET", "POST"])
def signin():
    """Sign in user"""
    if request.method == "POST":
        username = request.form.get("username")
        name = request.form.get("name")
        surname = request.form.get("surname")
        birthday = request.form.get("birthday")
        gender = request.form.get("gender")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            flash("Username is required.", "danger")
            return redirect("/signin")

        # Check if username already exists
        existing_user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if existing_user:
            flash("Username already exists.", "danger")
            return redirect("/signin")

        if not name or not surname:
            flash("Name and Surname are required.", "danger")
            return redirect("/signin")

        if not gender:
            flash("Please select your gender.", "danger")
            return redirect("/signin")

        if not birthday:
            flash("Birthday is required.", "danger")
            return redirect("/signin")

        if not password:
            flash("Password is required.", "danger")
            return redirect("/signin")

        if not confirmation:
            flash("Confirmation is required.", "danger")
            return redirect("/signin")

        if password != confirmation:
            flash("Passwords do not match.", "danger")
            return redirect("/signin")

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return redirect("/signin")

        try:
            birth_date = datetime.strptime(birthday, "%Y-%m-%d")
            today = datetime.today()

            age = (
                today.year
                - birth_date.year
                - ((today.month, today.day) < (birth_date.month, birth_date.day))
            )

            if age < 13:
                flash("You must be at least 13 years old to register.", "danger")
                return redirect("/signin")
            if age > 100:
                flash("Please enter a valid birthday.", "danger")
                return redirect("/signin")

        except ValueError:
            flash("Invalid date format.", "danger")
            return redirect("/signin")

        # Hash the password and save
        hashed_password = generate_password_hash(password)

        db.execute(
            "INSERT INTO users (username, hash, name, surname, gender, birthday) VALUES (?, ?, ?, ?, ?, ?)",
            username,
            hashed_password,
            name,
            surname,
            gender,
            birthday,
        )

        flash("Registered successfully! Please log in.", "success")
        return redirect("/login")

    else:
        return render_template("signin.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log in user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            flash("Username is required.", "danger")
            return redirect("/login")

        if not password:
            flash("Password is required.", "danger")
            return redirect("/login")

        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(user) != 1 or not check_password_hash(user[0]["hash"], password):
            flash("Invalid username or password.", "danger")
            return redirect("/login")

        session["user_id"] = user[0]["id"]

        flash("Logged in successfully!", "success")
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    """Show and edit user profile"""

    if not session.get("user_id"):
        flash("Please log in to view your profile.", "danger")
        return redirect("/login")

    user_id = session["user_id"]

    if request.method == "POST":
        name = request.form.get("name")
        surname = request.form.get("surname")
        birthday = request.form.get("birthday")
        gender = request.form.get("gender")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        if not name or not surname or not birthday or not gender:
            flash("Name, surname, birthday, and gender cannot be empty.", "danger")
            return redirect("/profile")

        try:
            birth_date = datetime.strptime(birthday, "%Y-%m-%d")
            today = datetime.today()

            age = (
                today.year
                - birth_date.year
                - ((today.month, today.day) < (birth_date.month, birth_date.day))
            )

            if age < 13:
                flash("You must be at least 13 years old.", "danger")
                return redirect("/profile")
            if age > 100:
                flash("Please enter a valid birthday.", "danger")
                return redirect("/profile")

        except ValueError:
            flash("Invalid date format.", "danger")
            return redirect("/profile")

        if new_password or confirmation:
            if new_password != confirmation:
                flash("New passwords do not match.", "danger")
                return redirect("/profile")
            if len(new_password) < 8:
                flash("Password must be at least 8 characters long.", "danger")
                return redirect("/profile")

            hashed_password = generate_password_hash(new_password)
            db.execute(
                "UPDATE users SET name = ?, surname = ?, birthday = ?, gender = ?, hash = ? WHERE id = ?",
                name,
                surname,
                birthday,
                gender,
                hashed_password,
                user_id,
            )
            flash("Changes saved successfully!", "success")
        else:
            db.execute(
                "UPDATE users SET name = ?, surname = ?, birthday = ?, gender = ? WHERE id = ?",
                name,
                surname,
                birthday,
                gender,
                user_id,
            )
            flash("Changes saved successfully!", "success")

        return redirect("/profile")

    else:
        user = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]
        return render_template("profile.html", user=user)


@app.route("/progress", methods=["GET", "POST"])
def progress():
    """Manage weight, height, BMI and goals"""

    if not session.get("user_id"):
        flash("Please log in to view your body metrics.", "danger")
        return redirect("/login")

    user_id = session["user_id"]

    if request.method == "POST":
        weight_str = request.form.get("weight")
        height_str = request.form.get("height")
        target_weight_str = request.form.get("target_weight")

        if weight_str and height_str:
            try:
                weight = float(weight_str)
                height = float(height_str)
            except ValueError:
                flash("Please enter valid numbers.", "danger")
                return redirect("/progress")

            if weight <= 0 or height <= 0:
                flash("Weight and height must be positive numbers.", "danger")
                return redirect("/progress")

            height_m = height / 100.0
            bmi = round(weight / (height_m**2), 2)

            db.execute(
                "INSERT INTO body_logs (user_id, weight, height, bmi, date) VALUES (?, ?, ?, ?, CURRENT_DATE)",
                user_id,
                weight,
                height,
                bmi,
            )
            flash(f"Log added successfully! Your BMI is {bmi}.", "success")
            return redirect("/progress")

        elif target_weight_str:
            try:
                target_weight = float(target_weight_str)
            except ValueError:
                flash("Please enter a valid target weight.", "danger")
                return redirect("/progress")

            if target_weight <= 0:
                flash("Target weight must be positive.", "danger")
                return redirect("/progress")

            existing_goal = db.execute(
                "SELECT * FROM user_goals WHERE user_id = ?", user_id
            )
            if existing_goal:
                db.execute(
                    "UPDATE user_goals SET target_weight = ? WHERE user_id = ?",
                    target_weight,
                    user_id,
                )
            else:
                db.execute(
                    "INSERT INTO user_goals (user_id, target_weight, daily_calorie_target) VALUES (?, ?, 0)",
                    user_id,
                    target_weight,
                )

            flash("Target weight updated successfully!", "success")
            return redirect("/progress")

        else:
            flash("Invalid submission.", "danger")
            return redirect("/progress")

    else:
        logs = db.execute(
            "SELECT * FROM body_logs WHERE user_id = ? ORDER BY date DESC, id DESC",
            user_id,
        )

        latest_log = logs[0] if len(logs) > 0 else None

        goals = db.execute("SELECT * FROM user_goals WHERE user_id = ?", user_id)
        goal = goals[0] if len(goals) > 0 else None

        return render_template(
            "progress.html", logs=logs, latest_log=latest_log, goal=goal
        )

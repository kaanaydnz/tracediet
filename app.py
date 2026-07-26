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
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
Session(app)


DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///diet.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

IS_POSTGRES = DATABASE_URL.startswith("postgresql://")

db = SQL(DATABASE_URL)


def init_db():
    id_column = "id SERIAL PRIMARY KEY" if IS_POSTGRES else "id INTEGER PRIMARY KEY AUTOINCREMENT"

    db.execute(f"""
        CREATE TABLE IF NOT EXISTS users (
            {id_column},
            username TEXT NOT NULL UNIQUE,
            hash TEXT NOT NULL,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            gender TEXT NOT NULL,
            birthday DATE NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS user_goals (
            user_id INTEGER PRIMARY KEY,
            target_weight REAL,
            daily_calorie_target INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    db.execute(f"""
        CREATE TABLE IF NOT EXISTS body_logs (
            {id_column},
            user_id INTEGER NOT NULL,
            weight REAL NOT NULL,
            height REAL NOT NULL,
            bmi REAL NOT NULL,
            date DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    db.execute(f"""
        CREATE TABLE IF NOT EXISTS tracker_logs (
            {id_column},
            user_id INTEGER NOT NULL,
            food_name TEXT NOT NULL,
            calories INTEGER NOT NULL,
            date DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)


init_db()


@app.route("/")
def index():
    if not session.get("user_id"):
        return render_template("index.html")

    user_id = session["user_id"]

    # Fetch user name and determine greeting based on current time
    user = db.execute("SELECT name FROM users WHERE id = ?", user_id)[0]
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    latest_log = db.execute(
        "SELECT * FROM body_logs WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT 1",
        user_id,
    )
    latest_log = latest_log[0] if latest_log else None

    foods = db.execute(
        "SELECT calories FROM tracker_logs WHERE user_id = ? AND date = CURRENT_DATE",
        user_id,
    )
    total_eaten = sum(food["calories"] for food in foods)

    goal = db.execute("SELECT target_weight FROM user_goals WHERE user_id = ?", user_id)
    target_weight = goal[0]["target_weight"] if goal else None

    return render_template(
        "index.html",
        name=user["name"],
        greeting=greeting,
        latest_log=latest_log,
        total_eaten=total_eaten,
        target_weight=target_weight,
    )


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


@app.route("/calories", methods=["GET", "POST"])
def calories():
    """Manage daily food logs and calorie tracking"""

    if not session.get("user_id"):
        flash("Please log in to view your calories.", "danger")
        return redirect("/login")

    user_id = session["user_id"]

    if request.method == "POST":
        food_name = request.form.get("food_name")
        calories_str = request.form.get("calories")

        if not food_name or not calories_str:
            flash("Food name and calories are required.", "danger")
            return redirect("/calories")

        try:
            calories = int(calories_str)
        except ValueError:
            flash("Calories must be a valid whole number.", "danger")
            return redirect("/calories")

        if calories < 0:
            flash("Calories cannot be negative.", "danger")
            return redirect("/calories")

        db.execute(
            "INSERT INTO tracker_logs (user_id, food_name, calories, date) VALUES (?, ?, ?, CURRENT_DATE)",
            user_id,
            food_name,
            calories,
        )

        flash(f"'{food_name}' added to today's log!", "success")
        return redirect("/calories")
    else:
        user = db.execute("SELECT * FROM users WHERE id = ?", user_id)[0]

        logs = db.execute(
            "SELECT * FROM body_logs WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT 1",
            user_id,
        )
        latest_log = logs[0] if len(logs) > 0 else None

        goals = db.execute("SELECT * FROM user_goals WHERE user_id = ?", user_id)
        goal = goals[0] if len(goals) > 0 else None

        daily_target = 0

        if latest_log and goal and goal["target_weight"]:
            birthday_value = user["birthday"]
            if isinstance(birthday_value, str):
                birth_date = datetime.strptime(birthday_value, "%Y-%m-%d")
            else:
                # Postgres returns DATE columns as native date objects, not strings
                birth_date = datetime.combine(birthday_value, datetime.min.time())
            today = datetime.today()
            age = (
                today.year
                - birth_date.year
                - ((today.month, today.day) < (birth_date.month, birth_date.day))
            )

            weight = latest_log["weight"]
            height = latest_log["height"]

            # BMR calculation using Mifflin-St Jeor Equation
            if user["gender"] == "male":
                bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
            else:
                bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

            tdee = bmr * 1.2

            target_w = goal["target_weight"]
            if target_w < weight:
                daily_target = int(tdee - 500)
            elif target_w > weight:
                daily_target = int(tdee + 500)
            else:
                daily_target = int(tdee)

            if user["gender"] == "male" and daily_target < 1500:
                daily_target = 1500
            elif user["gender"] == "female" and daily_target < 1200:
                daily_target = 1200

        foods = db.execute(
            "SELECT * FROM tracker_logs WHERE user_id = ? AND date = CURRENT_DATE ORDER BY id DESC",
            user_id,
        )
        total_calories = sum(food["calories"] for food in foods)

        return render_template(
            "calories.html",
            target=daily_target,
            foods=foods,
            total=total_calories,
            latest_log=latest_log,
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
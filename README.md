# TraceDiet

### 🔗 Live Demo: [tracediet.onrender.com](https://tracediet.onrender.com)
### 🎥 Video Demo: [youtu.be/F0tP1b5oVR0](https://www.youtube.com/embed/F0tP1b5oVR0?si=qZs_RkxrIrOqNfg_&start=16)

> **Note:** The app is hosted on Render's free tier, which spins down after periods of inactivity. If the site feels slow on your first visit, give it 30–60 seconds to wake up.

## Description

TraceDiet is a personalized, web-based diet and fitness tracker designed to ease the process of monitoring daily caloric intake and physical progress. The backend is built with Python, Flask, and PostgreSQL, and the frontend uses HTML, CSS, and Bootstrap 5.

## Tech Stack

- **Backend:** Python, Flask
- **Database:** PostgreSQL ([Neon](https://neon.com) — serverless Postgres)
- **Frontend:** HTML, CSS, Bootstrap 5, Jinja templating
- **Deployment:** [Render](https://render.com) (web service) + Neon (database), deployed straight from this GitHub repo
- **Auth & Sessions:** Werkzeug password hashing, Flask-Session

## Project Structure

* **`app.py`**: The core of the application. It contains all the Flask routing logic, session management, and backend data processing. It handles user authentication (register, login, logout), form validations, and database queries. It is also responsible for executing the mathematical formulas, such as calculating the BMI and implementing the Mifflin-St Jeor equation based on data retrieved from the database.
* **`layout.html`**: The foundational Jinja template that all other HTML pages inherit from. It includes the `<head>` metadata, Bootstrap links, and the navigation bar. By using Jinja's `{% block main %}`, it ensures a consistent layout across the entire application without code duplication.
* **`index.html`**: The personalized dashboard. It greets the user based on the time of day and dynamically displays their current BMI, the total calories consumed that day, and their target weight.
* **`calories.html`**: The interface where users can log their daily food intake. It contains a form to input the food name and its caloric value. The backend captures this data and instantly updates the daily total shown on the dashboard.
* **`progress.html`**: A dedicated section for users to log updates to their physical metrics — weight and height. When new data is submitted, the application recalculates their BMI and adjusts their caloric needs accordingly. It also includes the target weight selection feature.
* **`profile.html`**: Allows users to manage their account. They can easily update their personal information or change account details when needed.
* **`signin.html` & `login.html`**: The gateways to the application. They provide secure forms for users to create an account or access their existing dashboard.

## Design Choices

While developing TraceDiet, I made several deliberate design decisions to keep the application robust, portable, and user-friendly.

**1. Automated Database Initialization**

One of the most significant choices I made was discarding the `schema.sql` file often used in class examples. I wanted TraceDiet to be completely "plug-and-play." I wrote an `init_db()` function directly within the Python code that automatically checks whether the required tables exist and creates them if they don't — no manual setup step needed. This same function works against both SQLite (for local development) and PostgreSQL (in production), switching schema syntax based on the `DATABASE_URL` environment variable.

**2. Mobile-Friendly Navigation Bar**

Another area I focused on was the mobile navigation experience. By default, Bootstrap hides core navigation behind a "hamburger" menu on small screens. I felt hiding features like Home, Calories, and Progress behind a dropdown hurt usability, so instead I built a custom `flex-wrap` and grid-based navbar. On mobile, the "TraceDiet" brand centers at the top and the nav links wrap symmetrically underneath, giving a clean, app-like feel without any hidden menus.

**3. Scientific Method for Calorie Tracking**

Rather than a flat-rate calorie estimate, TraceDiet implements the Mifflin-St Jeor equation to calculate BMR and daily calorie targets based on age, gender, weight, and height — making the numbers shown on the dashboard scientifically grounded.

**4. Production-Ready Deployment**

The app is deployed on Render directly from this repository, with continuous deployment on every push to `main`. The database runs on Neon's serverless PostgreSQL, which keeps user data persistent (unlike ephemeral free-tier disks) while still being fully free to run.

## Running Locally

```bash
git clone https://github.com/kaanaydnz/tracediet.git
cd tracediet
pip install -r requirements.txt
python app.py
```

By default the app falls back to a local SQLite database (`diet.db`) when no `DATABASE_URL` environment variable is set, so no external database is required to run it locally. Visit `http://localhost:5000` in your browser.

## Conclusion

Building TraceDiet was a challenging but very practical experience. It brought together database design and SQL queries, Python backend logic, and responsive frontend development — and took it a step further by actually deploying it as a live, publicly accessible application with a production-grade database. The final product is a functional, mobile-ready web application that solves a real-world problem.
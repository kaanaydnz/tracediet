# TraceDiet
#### Video Demo: https://youtu.be/F0tP1b5oVR0
#### Description:
TraceDiet is a personalized, web-based diet and fitness tracker designed to ease the process of monitoring daily caloric intake and physical progress. This application has Python, Flask, and SQLite on the backend, and HTML, CSS, and Bootstrap 5 on the frontend.

### Project Structure
*   **`app.py`**: This is the core of the application. It contains all the Flask routing logic, session management, and backend data processing. It handles user authentication (register, login, logout), form validations, and database queries. It is also responsible for executing the mathematical formulas, such as calculating the BMI and implementing the Mifflin-St Jeor equation based on the data retrieved from the SQLite database.
*   **`layout.html`**: The foundational Jinja template that all other HTML pages inherit from. It includes the `<head>` metadata, Bootstrap links, and the navigation bar. By using Jinja's `{% block main %}`, it ensures a consistent layout across the entire application without code duplication.
*   **`index.html`**: The personalized dashboard. It greets the user based on the time of day and dynamically displays their current BMI, the total calories consumed that day, and their target weight.
*   **`calories.html`**: The interface where users can log their daily food intake. It contains a form to input the food name and its caloric value. The backend captures this data and instantly updates the daily total shown on the dashboard.
*   **`progress.html`**: A dedicated section for users to log updates to their physical metrics that are weight and height. When new data is submitted, the application recalculates their BMI and adjusts their caloric needs accordingly. It also has the target weight selection feature. 
*   **`profile.html`**: Allows users to manage their account. They can easily update their personal information or change account details when needed.
*   **`register.html` & `login.html`**: The gateways to the application. They provide secure forms for users to create an account or access their existing dashboard.

### Design Choices

While developing the TraceDiet, I had some significant design decisions to ensure the application was both robust and user-friendly.

**1. Automated Database Initialization:**
One of the most significant choices I made was discarding the `schema.sql` file which is often used in class examples. I wanted TraceDiet to be completely "plug-and-play." To achieve this, I wrote an `init_db()` function directly within the Python code. When the application runs, it automatically checks if the database and its required tables exist. If they do not, it creates them instantly. This design choice eliminates the need for manual setup via the command line, making the application much easier to deploy and test.

**2. Mobile-Friendly Navigation Bar:**
Another major issue I disturbed was the frontend layout, specifically the mobile navigation experience. By default, Bootstrap utilizes a "hamburger" menu (navbar-toggler) for mobile screens. However, I realized that hiding the core features (Home, Calories, Progress) in a dropdown menu negatively impacted the user interface design.
Instead of the hamburger menu, I implemented a custom `flex-wrap` and grid-based approach. I utilized Bootstrap's flexbox utility classes to keep the navigation links visible at all times. On mobile devices, the "TraceDiet" brand automatically centers at the top, and the navigation links wrap symmetrically under it, creating a clean, app-like "widget" feel without any hidden menus. This required careful manipulation of classes like `w-100`, `justify-content-center`, and `d-md-none` to ensure the layout adapted perfectly from desktop to mobile screens.

**3. Scientific Method for Calorie Tracking:**
I chose to implement the Mifflin-St Jeor equation rather than a simpler, flat-rate calorie calculator. While it required more complex backend logic to parse variables like age and gender, it significantly increases the real-world utility of the app. It ensures that the target calories displayed on the user's dashboard are scientifically grounded.

### Conclusion

Building TraceDiet was a challenging but very practical experience. It allowed me to bring together everything I learned in CS50, such as database design and SQL queries, Python backend logic, and responsive frontend development. The final product is a functional, mobile-ready web application that solves a real-world problem.

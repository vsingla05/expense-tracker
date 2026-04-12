from flask import Flask, render_template, request, redirect, url_for
from database.db import get_db, init_db, seed_db
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Initialize database on startup
with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Extract form data
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Validation
        if not name:
            return render_template("register.html", error="Name is required")

        if not email or "@" not in email:
            return render_template("register.html", error="Valid email is required")

        if len(password) < 6:
            return render_template("register.html", error="Password must be at least 6 characters")

        # Hash password
        password_hash = generate_password_hash(password)

        # Insert user into database
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash)
            )
            conn.commit()
            return redirect(url_for("login"))
        except Exception:
            # Duplicate email or other database error
            return render_template("register.html", error="Email already registered")
        finally:
            conn.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Extract form data
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Validation
        if not email or "@" not in email:
            return render_template("login.html", error="Valid email is required")

        if not password:
            return render_template("login.html", error="Password is required")

        # Look up user by email
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, password_hash FROM users WHERE email = ?",
            (email,)
        )
        user = cursor.fetchone()
        conn.close()

        if not user or not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Invalid email or password")

        # Login successful - store user info in session
        # For now, just redirect to a welcome page
        return redirect(url_for("profile"))

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    return "Logout — coming in Step 3"


@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)

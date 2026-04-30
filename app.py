from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database.db import get_db, init_db, seed_db
from database.queries import get_category_breakdown, get_recent_transactions, get_summary_stats, get_user_by_id
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
app.secret_key = "spendly-dev-secret-key-change-in-production"

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
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("landing"))

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Auth helper                                                          #
# ------------------------------------------------------------------ #

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
@login_required
def profile():
    user_id = session.get("user_id")

    # Fetch user data from database
    user = get_user_by_id(user_id)
    if not user:
        # Fallback if user not found
        user = {
            "name": session.get("user_name", "User"),
            "email": "",
            "initials": "U",
            "member_since": "Unknown"
        }
    else:
        # Add initials for the avatar
        user["initials"] = "".join([word[0].upper() for word in user["name"].split()])

    # Read and validate date filter parameters
    date_from_raw = request.args.get("date_from")
    date_to_raw = request.args.get("date_to")

    date_from = None
    date_to = None

    # Validate dates
    if date_from_raw:
        try:
            date_from = datetime.strptime(date_from_raw, "%Y-%m-%d").date()
        except ValueError:
            date_from = None

    if date_to_raw:
        try:
            date_to = datetime.strptime(date_to_raw, "%Y-%m-%d").date()
        except ValueError:
            date_to = None

    # If both dates are valid but date_from > date_to, show error and fall back to unfiltered
    if date_from and date_to and date_from > date_to:
        flash("Start date must be before end date.")
        date_from = None
        date_to = None

    # Convert dates back to strings for queries and template
    date_from_str = date_from.strftime("%Y-%m-%d") if date_from else None
    date_to_str = date_to.strftime("%Y-%m-%d") if date_to else None

    # Fetch summary stats from database
    stats = get_summary_stats(user_id, date_from=date_from_str, date_to=date_to_str)

    # Fetch recent transactions from database
    transactions = get_recent_transactions(user_id, limit=10, date_from=date_from_str, date_to=date_to_str)

    # Fetch category breakdown from database
    categories = get_category_breakdown(user_id, date_from=date_from_str, date_to=date_to_str)

    # Compute preset date ranges for active state highlighting
    today = datetime.now().date()
    this_month_from = today.replace(day=1)
    last_3_months_from = today - relativedelta(months=3)
    last_6_months_from = today - relativedelta(months=6)

    # Determine which preset is active (if any)
    active_preset = None
    if date_from and date_to:
        if date_from == this_month_from and date_to == today:
            active_preset = "this_month"
        elif date_from == last_3_months_from and date_to == today:
            active_preset = "last_3_months"
        elif date_from == last_6_months_from and date_to == today:
            active_preset = "last_6_months"
        else:
            active_preset = "custom"
    elif not date_from_raw and not date_to_raw:
        active_preset = "all_time"

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
        date_from=date_from_str,
        date_to=date_to_str,
        active_preset=active_preset,
        this_month_from=this_month_from.strftime("%Y-%m-%d"),
        last_3_months_from=last_3_months_from.strftime("%Y-%m-%d"),
        last_6_months_from=last_6_months_from.strftime("%Y-%m-%d"),
        today=today.strftime("%Y-%m-%d")
    )


@app.route("/expenses/add")
@login_required
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
@login_required
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
@login_required
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5000)

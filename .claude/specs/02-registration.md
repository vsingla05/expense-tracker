# Spec: Registration

## Overview

Implement the backend functionality for user registration. The UI template (`register.html`) already exists from Step 1, but the form currently has no backend handler. This step adds the POST route to process registration submissions, validate input, hash passwords, and store new users in the database. Registration is the first half of the authentication system and enables users to create accounts in Spendly.

## Depends on

- Step 1 (Database Setup) — the `users` table and `get_db()` function must be implemented

## Routes

- `GET /register` — already exists, renders registration form
- `POST /register` — processes registration form submission — public (unauthenticated)

## Database changes

No database changes — the `users` table from Step 1 is sufficient.

## Templates

- **Modify:** `templates/register.html`
  - Add form `action="/register"` and `method="POST"`
  - Add CSRF token placeholder (if implementing CSRF later)
  - Add error message display block for validation errors
  - Add success/redirect handling

## Files to change

- `app.py` — add POST handler for `/register` route
- `templates/register.html` — wire up form to POST endpoint

## Files to create

- `database/db.py` — add `create_user(name, email, password)` helper function (optional but recommended)

## New dependencies

No new dependencies — use existing `werkzeug.security` for password hashing.

## Rules for implementation

- No SQLAlchemy or ORMs — use raw SQLite with parameterized queries only
- Passwords must be hashed using `werkzeug.security.generate_password_hash()`
- Validate all inputs server-side:
  - Email must be valid format and unique
  - Password must meet minimum length requirement (at least 6 characters)
  - Name must not be empty
- Use CSS variables for styling — never hardcode hex values
- Template must extend `base.html`
- On successful registration, redirect to login page with success message
- On error, re-render registration form with error message displayed

## Definition of done

- [ ] GET /register renders the registration form
- [ ] POST /register accepts form submission with name, email, password fields
- [ ] Empty name shows error message
- [ ] Invalid email format shows error message
- [ ] Duplicate email shows error message
- [ ] Password shorter than 6 characters shows error message
- [ ] Valid registration creates user in database with hashed password
- [ ] Successful registration redirects to /login page
- [ ] Error cases re-render form with descriptive error message
- [ ] No plaintext passwords stored in database
- [ ] All database queries use parameterized statements (no string formatting)

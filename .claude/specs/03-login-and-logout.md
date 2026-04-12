# Spec: Login and Logout

## Overview

Implement session-based authentication for Spendly. This step adds server-side session management to track logged-in users, protects authenticated routes, and provides a working logout mechanism. Building on the registration feature from Step 2, login and logout complete the core authentication flow and gate access to the expense management features in later steps.

## Depends on

- Step 1 (Database Setup) — `users` table and `get_db()` must exist
- Step 2 (Registration) — user accounts can be created

## Routes

- `POST /login` — authenticate user with email/password, create session — public
- `GET /logout` — clear session and redirect to landing — logged-in users
- `GET /profile` — placeholder profile page — logged-in users (upgrade from placeholder)
- `GET /expenses/add` — placeholder add expense — logged-in users (upgrade from placeholder)
- `GET /expenses/<int:id>/edit` — placeholder edit expense — logged-in users (upgrade from placeholder)
- `GET /expenses/<int:id>/delete` — placeholder delete expense — logged-in users (upgrade from placeholder)

## Database changes

No database changes — existing `users` table is sufficient.

## Templates

- **Modify:** `templates/base.html`
  - Conditionally show/hide nav links based on `session.get('user_id')`
  - Show "Sign out" option when logged in
  - Show "Sign in" / "Get started" when logged out

## Files to change

- `app.py` — add `session` import, configure `app.secret_key`, implement login POST handler with session, implement logout route, add login-required decorators/check on protected routes
- `templates/base.html` — update navbar to show contextual links based on auth state

## Files to create

- `tests/test_login_logout.py` — test login success, login failure, logout, and protected route access

## New dependencies

No new dependencies — Flask's built-in `session` is used for session management.

## Rules for implementation

- No SQLAlchemy or ORMs — use raw SQLite with parameterized queries only
- Use Flask's built-in `session` for storing `user_id` after successful login
- Set `app.secret_key` to a stable value (can use an environment variable pattern)
- Password verification using `werkzeug.security.check_password_hash()`
- All protected routes must check `session.get('user_id')` and redirect to `/login` if not authenticated
- After logout, clear all session data using `session.clear()`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Never store plaintext passwords (already handled in Step 2)

## Definition of done

- [ ] POST /login with valid email/password creates a session and redirects to /profile
- [ ] POST /login with invalid email/password shows error message on login page
- [ ] POST /login with non-existent email shows error message
- [ ] GET /logout clears session and redirects to landing page
- [ ] GET /profile redirects to /login when not authenticated
- [ ] GET /expenses/add redirects to /login when not authenticated
- [ ] Navbar shows "Sign out" when user is logged in
- [ ] Navbar shows "Sign in" and "Get started" when user is not logged in
- [ ] Logged-in user ID is accessible via `session.get('user_id')` in protected routes
- [ ] All database queries use parameterized statements (no string formatting)
- [ ] Tests pass for login, logout, and protected route behavior

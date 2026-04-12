# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flask-based expense tracker web application (Python 3.12). Currently in early development with landing page, authentication UI (register/login), and legal pages (terms/privacy) implemented. Core expense CRUD operations are placeholders.

## Commands

```bash
# Run the application
python app.py

# The app runs on http://localhost:5001
```

## Architecture

- **app.py**: Main Flask application with route definitions
- **database/db.py**: Database layer (students implement `get_db()`, `init_db()`, `seed_db()` for SQLite with row_factory and foreign keys)
- **templates/**: Jinja2 HTML templates (landing, register, login, terms, privacy, base)
- **static/**: CSS and JavaScript assets
- **venv/**: Python 3.12 virtual environment

## Development Notes

- Uses pytest for testing (pytest, pytest-flask in requirements.txt)
- Database layer uses SQLite with foreign key support enabled
- Follows a step-by-step curriculum (Steps 1-9) for implementing features

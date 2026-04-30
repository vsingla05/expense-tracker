"""Database query functions for the expense tracker."""

from database.db import get_db
from datetime import datetime


def get_user_by_id(user_id):
    """
    Fetch user information by ID.

    Args:
        user_id: The ID of the user to fetch

    Returns:
        Dict with keys: name, email, member_since
        Returns None if user not found
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, email, created_at FROM users WHERE id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    # Format created_at as "Month YYYY"
    created_at = row["created_at"]
    try:
        dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        member_since = dt.strftime("%B %Y")
    except (ValueError, TypeError):
        member_since = "Unknown"

    return {
        "name": row["name"],
        "email": row["email"],
        "member_since": member_since
    }


def get_recent_transactions(user_id, limit=10, date_from=None, date_to=None):
    """
    Fetch recent transactions for a user.

    Args:
        user_id: The ID of the user whose transactions to fetch
        limit: Maximum number of transactions to return (default 10)
        date_from: Optional start date (YYYY-MM-DD) for filtering
        date_to: Optional end date (YYYY-MM-DD) for filtering

    Returns:
        List of dicts with keys: date, description, category, amount
        Returns empty list if user has no expenses
    """
    conn = get_db()
    cursor = conn.cursor()

    query = """
        SELECT date, description, category, amount
        FROM expenses
        WHERE user_id = ?
    """
    params = [user_id]

    if date_from and date_to:
        query += " AND date BETWEEN ? AND ?"
        params.extend([date_from, date_to])

    query += " ORDER BY date DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)

    rows = cursor.fetchall()
    conn.close()

    transactions = []
    for row in rows:
        transactions.append({
            "date": row["date"],
            "description": row["description"],
            "category": row["category"],
            "amount": row["amount"]
        })

    return transactions


def get_summary_stats(user_id, date_from=None, date_to=None):
    """
    Get summary statistics for a user's expenses.

    Args:
        user_id: The ID of the user to get stats for.
        date_from: Optional start date (YYYY-MM-DD) for filtering
        date_to: Optional end date (YYYY-MM-DD) for filtering

    Returns:
        dict with keys: total_spent, transaction_count, top_category
        If user has no expenses, returns {"total_spent": 0, "transaction_count": 0, "top_category": "—"}
    """
    conn = get_db()
    cursor = conn.cursor()

    # Build base query with optional date filter
    base_where = "WHERE user_id = ?"
    params = [user_id]

    if date_from and date_to:
        base_where += " AND date BETWEEN ? AND ?"
        params.extend([date_from, date_to])

    # Query total spent and transaction count
    cursor.execute(
        f"SELECT SUM(amount), COUNT(*) FROM expenses {base_where}",
        params
    )
    result = cursor.fetchone()
    total_spent = result[0] if result[0] is not None else 0
    transaction_count = result[1] if result[1] is not None else 0

    # Query top category
    cursor.execute(
        f"SELECT category, SUM(amount) FROM expenses {base_where} GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
        params
    )
    top_category_result = cursor.fetchone()
    top_category = top_category_result[0] if top_category_result else "—"

    conn.close()

    # Handle case where user has no expenses
    if transaction_count == 0:
        return {
            "total_spent": 0,
            "transaction_count": 0,
            "top_category": "—"
        }

    return {
        "total_spent": total_spent,
        "transaction_count": transaction_count,
        "top_category": top_category
    }


def get_category_breakdown(user_id, date_from=None, date_to=None):
    """
    Get category breakdown of expenses for a user.

    Args:
        user_id: The ID of the user
        date_from: Optional start date (YYYY-MM-DD) for filtering
        date_to: Optional end date (YYYY-MM-DD) for filtering

    Returns:
        List of dicts with keys: name, amount, pct
        Percentages sum to exactly 100 (largest category absorbs rounding remainder)
        Returns empty list if user has no expenses
    """
    conn = get_db()
    cursor = conn.cursor()

    query = """
        SELECT category, SUM(amount) as amount
        FROM expenses
        WHERE user_id = ?
    """
    params = [user_id]

    if date_from and date_to:
        query += " AND date BETWEEN ? AND ?"
        params.extend([date_from, date_to])

    query += " GROUP BY category ORDER BY amount DESC"

    cursor.execute(query, params)

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return []

    # Calculate total
    total = sum(row["amount"] for row in rows)

    # Build result list with raw percentages
    result = []
    for row in rows:
        result.append({
            "name": row["category"],
            "amount": row["amount"],
            "pct": row["amount"] / total * 100
        })

    # Round percentages to integers
    for item in result:
        item["pct"] = round(item["pct"])

    # Adjust largest category to absorb rounding remainder
    # so percentages sum to exactly 100
    current_sum = sum(item["pct"] for item in result)
    if result:
        result[0]["pct"] += 100 - current_sum

    return result

import sqlite3
from datetime import datetime


DB_PATH = "./data/tickets.db"


# -----------------------------
# Database Setup
# -----------------------------

def init_db():
    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            issue TEXT,
            category TEXT,
            priority TEXT,
            status TEXT,
            created_at TEXT
        )
    """)

    connection.commit()
    connection.close()


# -----------------------------
# Create Ticket
# -----------------------------

def create_ticket(
    user,
    issue,
    category="General",
    priority="Medium"
):

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        INSERT INTO tickets
        (user, issue, category, priority, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user,
        issue,
        category,
        priority,
        "Open",
        created_at
    ))

    ticket_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return ticket_id


# -----------------------------
# Get All Tickets
# -----------------------------

def get_tickets():

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            user,
            issue,
            category,
            priority,
            status,
            created_at
        FROM tickets
        ORDER BY id DESC
    """)

    tickets = cursor.fetchall()

    connection.close()

    return tickets


# -----------------------------
# Update Ticket Status
# -----------------------------

def update_ticket_status(
    ticket_id,
    status
):

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE tickets
        SET status = ?
        WHERE id = ?
    """, (
        status,
        ticket_id
    ))

    connection.commit()
    connection.close()


# -----------------------------
# Delete Tickets (only RESOLVED ones can ever be deleted)
# -----------------------------

def delete_ticket(ticket_id):
    """
    Deletes ONE ticket, but only if its status is Resolved.
    Returns True if a ticket was deleted, otherwise False.
    """

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM tickets
        WHERE id = ? AND status = 'Resolved'
    """, (ticket_id,))

    deleted = cursor.rowcount

    connection.commit()
    connection.close()

    return deleted > 0


def delete_resolved_tickets():
    """
    Deletes ALL resolved tickets. Open and In Progress tickets are never touched.
    Returns how many tickets were deleted.
    """

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute("DELETE FROM tickets WHERE status = 'Resolved'")

    deleted = cursor.rowcount

    connection.commit()
    connection.close()

    return deleted
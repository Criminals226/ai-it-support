# bootstrap.py
#
# Makes the app "self-starting" on a fresh server.
#
# Free hosts can wipe local files when the app restarts. These helpers
# re-create the demo accounts and (optionally) demo tickets from SETTINGS,
# so the live app is always ready to use. The passwords live only in the
# host's secrets, never in the code.
#
# Settings (environment variables / host secrets):
#   BOOTSTRAP_ADMIN_USER, BOOTSTRAP_ADMIN_PASSWORD
#   BOOTSTRAP_EMPLOYEE_USER, BOOTSTRAP_EMPLOYEE_PASSWORD   (optional)
#   SEED_DEMO_TICKETS=true                                 (optional)

import os

from auth import create_user, list_users
from tickets import DB_PATH, create_ticket, get_tickets, update_ticket_status
from ticket_intelligence import classify_ticket


# (role, setting for the username, setting for the password)
ACCOUNT_SETTINGS = (
    ("admin", "BOOTSTRAP_ADMIN_USER", "BOOTSTRAP_ADMIN_PASSWORD"),
    ("employee", "BOOTSTRAP_EMPLOYEE_USER", "BOOTSTRAP_EMPLOYEE_PASSWORD"),
)


def ensure_bootstrap_accounts(db_path=DB_PATH):
    """
    Creates the admin/employee accounts named in the settings, if they do
    not exist yet. Returns the list of usernames that were created.
    """

    created = []

    for role, user_setting, password_setting in ACCOUNT_SETTINGS:

        username = os.getenv(user_setting, "").strip().lower()

        password = os.getenv(password_setting, "")

        if not username or not password:
            continue

        existing = [user[1] for user in list_users(db_path)]

        if username in existing:
            continue

        try:

            create_user(username, password, role, db_path)

            created.append(username)

        except ValueError as error:

            # Shows in the host's logs; the app keeps running
            print(f"[bootstrap] could not create '{username}': {error}")

    return created


# Sample tickets so the dashboard is not empty for reviewers
DEMO_TICKETS = [
    ("demo.employee", "My VPN is not connecting", "Resolved"),
    ("demo.employee", "My account is locked and I can't log in", "In Progress"),
    ("demo.employee", "The VPN server is down for everyone in my team", "Open"),
    ("demo.employee", "I can't send emails from Outlook", "Open"),
    ("demo.employee", "The printer is out of toner, not urgent", "Resolved"),
    ("demo.employee", "Wi-Fi is connected but there is no internet", "Open"),
]


def seed_demo_tickets_if_empty():
    """
    Adds sample tickets, but only when SEED_DEMO_TICKETS is switched on
    AND there are no tickets at all. Returns how many were added.
    """

    if os.getenv("SEED_DEMO_TICKETS", "").strip().lower() not in ("1", "true", "yes"):
        return 0

    if get_tickets():
        return 0

    for user, issue, status in DEMO_TICKETS:

        classification = classify_ticket(issue)

        ticket_id = create_ticket(
            user,
            issue,
            classification["category"],
            classification["priority"]
        )

        if status != "Open":
            update_ticket_status(ticket_id, status)

    return len(DEMO_TICKETS)
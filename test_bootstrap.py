# test_bootstrap.py
# Run with:  python test_bootstrap.py
#
# Uses temporary databases, so it does NOT touch your real data.

import os
import tempfile

import tickets
from auth import init_users_table, verify_login, list_users
from bootstrap import ensure_bootstrap_accounts, seed_demo_tickets_if_empty


SETTING_NAMES = [
    "BOOTSTRAP_ADMIN_USER", "BOOTSTRAP_ADMIN_PASSWORD",
    "BOOTSTRAP_EMPLOYEE_USER", "BOOTSTRAP_EMPLOYEE_PASSWORD",
    "SEED_DEMO_TICKETS",
]


def clear_settings():

    for name in SETTING_NAMES:
        os.environ.pop(name, None)


def new_users_db():

    path = os.path.join(tempfile.mkdtemp(), "test_users.db")

    init_users_table(path)

    return path


results = []


def check(description, condition):

    results.append(condition)

    status = "PASS" if condition else "FAIL"

    print(f"{status} | {description}")


# --- Accounts ---

clear_settings()

os.environ["BOOTSTRAP_ADMIN_USER"] = "DemoAdmin"
os.environ["BOOTSTRAP_ADMIN_PASSWORD"] = "DemoAdminPass1"
os.environ["BOOTSTRAP_EMPLOYEE_USER"] = "demoemployee"
os.environ["BOOTSTRAP_EMPLOYEE_PASSWORD"] = "DemoEmployeePass1"

db = new_users_db()

created = ensure_bootstrap_accounts(db)

check(
    "Admin and employee accounts are created from settings",
    created == ["demoadmin", "demoemployee"]
)

login = verify_login("demoadmin", "DemoAdminPass1", db)

check(
    "The bootstrap admin can log in with the admin role",
    login is not None and login["role"] == "admin"
)

check(
    "Running bootstrap again does not create duplicates",
    ensure_bootstrap_accounts(db) == [] and len(list_users(db)) == 2
)

clear_settings()

check(
    "Nothing is created when no settings are given",
    ensure_bootstrap_accounts(new_users_db()) == []
)

os.environ["BOOTSTRAP_ADMIN_USER"] = "weakadmin"
os.environ["BOOTSTRAP_ADMIN_PASSWORD"] = "short"

weak_db = new_users_db()

check(
    "A too-short bootstrap password is skipped, not a crash",
    ensure_bootstrap_accounts(weak_db) == [] and list_users(weak_db) == []
)

clear_settings()


# --- Demo tickets ---

tickets.DB_PATH = os.path.join(tempfile.mkdtemp(), "test_tickets.db")

tickets.init_db()

check(
    "Demo tickets stay off unless enabled",
    seed_demo_tickets_if_empty() == 0 and tickets.get_tickets() == []
)

os.environ["SEED_DEMO_TICKETS"] = "true"

check(
    "Demo tickets are added when enabled and the table is empty",
    seed_demo_tickets_if_empty() == 6 and len(tickets.get_tickets()) == 6
)

check(
    "Seeding does not run twice",
    seed_demo_tickets_if_empty() == 0 and len(tickets.get_tickets()) == 6
)

clear_settings()


print(f"\n{sum(results)}/{len(results)} checks passed")
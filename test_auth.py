# test_auth.py
# Run with:  python test_auth.py
#
# Uses a temporary database, so it does NOT touch your real tickets.db.

import os
import sqlite3
import tempfile

from auth import init_users_table, create_user, verify_login


db_file = os.path.join(tempfile.mkdtemp(), "test_users.db")

init_users_table(db_file)

create_user("Aleena", "CorrectHorse1", "admin", db_file)
create_user("sara", "AnotherPass22", "employee", db_file)
create_user("tom", "SamePassword1", "employee", db_file)
create_user("ann", "SamePassword1", "employee", db_file)


results = []


def check(description, condition):

    results.append(condition)

    status = "PASS" if condition else "FAIL"

    print(f"{status} | {description}")


def raises_value_error(function, *args):

    try:
        function(*args)
        return False
    except ValueError:
        return True


# --- Login behaviour ---

admin = verify_login("Aleena", "CorrectHorse1", db_file)

check(
    "Admin can log in with the correct password",
    admin is not None and admin["role"] == "admin"
)

check(
    "Login ignores username capitalization",
    verify_login("ALEENA", "CorrectHorse1", db_file) is not None
)

check(
    "Wrong password is rejected",
    verify_login("aleena", "WrongPassword1", db_file) is None
)

check(
    "Unknown user is rejected",
    verify_login("nobody", "CorrectHorse1", db_file) is None
)

employee = verify_login("sara", "AnotherPass22", db_file)

check(
    "Employee login returns the employee role",
    employee is not None and employee["role"] == "employee"
)


# --- Storage safety ---

connection = sqlite3.connect(db_file)

rows = connection.execute(
    "SELECT username, password_hash, salt FROM users"
).fetchall()

hashes = dict(
    (row[0], row[1])
    for row in rows
)

connection.close()

stored_text = " ".join(str(value) for row in rows for value in row)

check(
    "Password is not stored in plain text",
    "CorrectHorse1" not in stored_text
    and "AnotherPass22" not in stored_text
)

check(
    "Stored hash is 64 hex characters (SHA-256)",
    all(len(value) == 64 for value in hashes.values())
)

check(
    "Same password gives different hashes (random salts)",
    hashes["tom"] != hashes["ann"]
)


# --- Input rules ---

check(
    "Duplicate username is rejected",
    raises_value_error(
        create_user, "aleena", "DifferentPass99", "employee", db_file
    )
)

check(
    "Too-short password is rejected",
    raises_value_error(create_user, "newuser", "short", "employee", db_file)
)

check(
    "Invalid role is rejected",
    raises_value_error(
        create_user, "newuser", "LongEnough123", "superuser", db_file
    )
)


print(f"\n{sum(results)}/{len(results)} checks passed")
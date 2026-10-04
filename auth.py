# auth.py
#
# Phase 3, Step 1: users, roles, and safe password storage.
#
# Passwords are NEVER stored. We store a salted PBKDF2 hash instead.
# Uses only Python's standard library, so nothing new to install.

import hashlib
import hmac
import os
import sqlite3
from datetime import datetime

from tickets import DB_PATH

# Lets auth.py read SETUP_CODE from your .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# How many times PBKDF2 repeats the hash. Higher = slower for attackers.
# 600,000 is the current OWASP recommendation for PBKDF2-HMAC-SHA256.
ITERATIONS = 600_000

VALID_ROLES = ("employee", "admin")

MIN_PASSWORD_LENGTH = 8


# -----------------------------
# Database setup
# -----------------------------

def init_users_table(db_path=DB_PATH):

    connection = sqlite3.connect(db_path)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            iterations INTEGER NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# -----------------------------
# Hashing helper
# -----------------------------

def _hash_password(password, salt, iterations):

    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations
    )


# -----------------------------
# Create a user
# -----------------------------

def create_user(username, password, role="employee", db_path=DB_PATH):
    """
    Creates a user. Raises ValueError for bad input or a duplicate name.
    Returns the new user's id.
    """

    username = username.strip().lower()

    if not username:
        raise ValueError("Username cannot be empty.")

    if role not in VALID_ROLES:
        raise ValueError(f"Role must be one of: {', '.join(VALID_ROLES)}.")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
        )

    # A new random salt for every user, so two users with the same
    # password still get different hashes.
    salt = os.urandom(16)

    password_hash = _hash_password(password, salt, ITERATIONS)

    connection = sqlite3.connect(db_path)

    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO users
            (username, password_hash, salt, iterations, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            username,
            password_hash.hex(),
            salt.hex(),
            ITERATIONS,
            role,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        connection.commit()

        return cursor.lastrowid

    except sqlite3.IntegrityError:
        raise ValueError("That username already exists.")

    finally:
        connection.close()


# -----------------------------
# Check a login
# -----------------------------

def verify_login(username, password, db_path=DB_PATH):
    """
    Returns {"username": ..., "role": ...} if the login is correct,
    otherwise None. It never says WHICH part was wrong.
    """

    username = username.strip().lower()

    connection = sqlite3.connect(db_path)

    cursor = connection.cursor()

    cursor.execute(
        "SELECT password_hash, salt, iterations, role "
        "FROM users WHERE username = ?",
        (username,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:

        # Do the same slow hashing work anyway, so an attacker cannot tell
        # "user does not exist" from "wrong password" by measuring time.
        _hash_password(password, b"\x00" * 16, ITERATIONS)

        return None

    stored_hash, salt_hex, iterations, role = row

    computed = _hash_password(
        password,
        bytes.fromhex(salt_hex),
        iterations
    )

    # compare_digest takes the same time however many characters match
    if hmac.compare_digest(computed.hex(), stored_hash):

        return {"username": username, "role": role}

    return None


# -----------------------------
# Phase 3, Step 3: account management (used by the admin User Management page)
# -----------------------------

def list_users(db_path=DB_PATH):
    """
    Returns a list of (id, username, role, created_at).
    Password hashes are never returned.
    """

    connection = sqlite3.connect(db_path)

    try:
        return connection.execute(
            "SELECT id, username, role, created_at "
            "FROM users ORDER BY username"
        ).fetchall()

    finally:
        connection.close()


def reset_password(username, new_password, db_path=DB_PATH):
    """
    Sets a new password (new random salt, new hash).
    Raises ValueError if the password is too short or the user is unknown.
    """

    username = username.strip().lower()

    if len(new_password) < MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
        )

    salt = os.urandom(16)

    password_hash = _hash_password(new_password, salt, ITERATIONS)

    connection = sqlite3.connect(db_path)

    try:
        cursor = connection.cursor()

        cursor.execute(
            "UPDATE users "
            "SET password_hash = ?, salt = ?, iterations = ? "
            "WHERE username = ?",
            (password_hash.hex(), salt.hex(), ITERATIONS, username)
        )

        connection.commit()

        if cursor.rowcount == 0:
            raise ValueError("User not found.")

    finally:
        connection.close()


def delete_user(username, db_path=DB_PATH):
    """
    Deletes an account. The last remaining admin can never be deleted,
    so the system cannot lock itself out.
    Raises ValueError if the user is unknown or is the last admin.
    """

    username = username.strip().lower()

    connection = sqlite3.connect(db_path)

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT role FROM users WHERE username = ?",
            (username,)
        )

        row = cursor.fetchone()

        if row is None:
            raise ValueError("User not found.")

        if row[0] == "admin":

            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")

            if cursor.fetchone()[0] <= 1:
                raise ValueError("You cannot delete the last admin account.")

        cursor.execute("DELETE FROM users WHERE username = ?", (username,))

        connection.commit()

    finally:
        connection.close()


# -----------------------------
# Phase 3, Step 4: first-run setup and admin recovery (inside the app)
# -----------------------------
#
# The SETUP_CODE lives in the server's .env file. Only the person who runs
# the server knows it. Without it, anyone who found a freshly deployed app
# could make themselves the admin.

MIN_SETUP_CODE_LENGTH = 12


def admin_exists(db_path=DB_PATH):
    """True if at least one admin account exists."""

    connection = sqlite3.connect(db_path)

    try:
        count = connection.execute(
            "SELECT COUNT(*) FROM users WHERE role = 'admin'"
        ).fetchone()[0]

        return count > 0

    finally:
        connection.close()


def setup_code_configured():
    """True if a SETUP_CODE of a safe length is set on the server."""

    return len(os.getenv("SETUP_CODE", "")) >= MIN_SETUP_CODE_LENGTH


def setup_code_is_valid(entered_code):
    """Checks the entered code against SETUP_CODE in constant time."""

    if not setup_code_configured() or not entered_code:
        return False

    return hmac.compare_digest(
        entered_code.encode("utf-8"),
        os.getenv("SETUP_CODE").encode("utf-8")
    )


def create_first_admin(setup_code, username, password, db_path=DB_PATH):
    """
    Creates the very first admin. Only works while NO admin exists,
    and only with the correct setup code.
    """

    if admin_exists(db_path):
        raise ValueError("Setup is already complete. Please sign in.")

    if not setup_code_is_valid(setup_code):
        raise ValueError("Invalid setup code.")

    return create_user(username, password, "admin", db_path)


def recover_admin_password(setup_code, username, new_password, db_path=DB_PATH):
    """
    Lets someone with the setup code reset an ADMIN password.
    (Employees must ask an admin, using the User Management page.)
    """

    if not setup_code_is_valid(setup_code):
        raise ValueError("Invalid setup code.")

    username = username.strip().lower()

    connection = sqlite3.connect(db_path)

    try:
        row = connection.execute(
            "SELECT role FROM users WHERE username = ?",
            (username,)
        ).fetchone()

    finally:
        connection.close()

    if row is None or row[0] != "admin":
        raise ValueError("No admin account with that username.")

    reset_password(username, new_password, db_path)
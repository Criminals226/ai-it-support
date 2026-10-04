# app.py
#
# The main entry point.
#   - First run (no admin yet):  setup screen to create the first admin
#   - Otherwise:                 login screen (with admin password recovery)
#   - After login:               pages based on the user's role
# Run the whole project with:  streamlit run app.py

import os
import time

import streamlit as st

from rag import build_knowledge_base
from tickets import init_db
from bootstrap import ensure_bootstrap_accounts, seed_demo_tickets_if_empty
from auth import (
    init_users_table,
    verify_login,
    admin_exists,
    setup_code_configured,
    create_first_admin,
    recover_admin_password,
    MIN_PASSWORD_LENGTH,
)


# -----------------------------
# Page Configuration (must be the first Streamlit call)
# -----------------------------

st.set_page_config(
    page_title="AI IT Support",
    page_icon="🤖",
    layout="centered"
)


# -----------------------------
# Initialize Systems
# -----------------------------

# A fresh server may not have the data folder yet
os.makedirs("data", exist_ok=True)

init_db()
init_users_table()

# Re-create demo accounts / tickets from the host's settings (if provided)
ensure_bootstrap_accounts()
seed_demo_tickets_if_empty()


# Builds the knowledge base ONCE per server start, not on every login.
@st.cache_resource(show_spinner="Loading IT knowledge base...")
def load_knowledge_base():
    return build_knowledge_base()


# Everything we keep in the session for a signed-in user
SESSION_KEYS = [
    "auth_user", "answer", "question", "results", "escalation", "ticket_info"
]


# -----------------------------
# First-run setup screen
# -----------------------------

def show_setup():

    st.title("🤖 AI IT Support")

    st.subheader("First-time setup")

    st.write(
        "No administrator exists yet. "
        "Create the first admin account to get started."
    )

    if not setup_code_configured():

        st.warning(
            "For security, the person who runs the server must set a "
            "**setup code** first. Otherwise the first visitor could "
            "make themselves the admin."
        )

        st.write(
            "Add this line to the `.env` file on the server "
            "(use at least 12 random characters), then restart the app:"
        )

        st.code("SETUP_CODE=your-long-random-secret", language="text")

        return

    with st.container(border=True):

        with st.form("setup_form"):

            code = st.text_input("Setup code", type="password")

            username = st.text_input("Admin username")

            password = st.text_input(
                f"Password (at least {MIN_PASSWORD_LENGTH} characters)",
                type="password"
            )

            confirm = st.text_input("Confirm password", type="password")

            submitted = st.form_submit_button(
                "Create admin account",
                type="primary"
            )

    if submitted:

        if password != confirm:

            st.error("Passwords do not match.")

        else:

            try:

                create_first_admin(code, username, password)

                st.session_state.notice = (
                    "Admin account created. Please sign in."
                )

                st.rerun()

            except ValueError as error:

                time.sleep(1)  # slows down guessing

                st.error(str(error))


# -----------------------------
# Login screen
# -----------------------------

def show_login():

    st.title("🤖 AI IT Support")

    st.caption("Sign in to get IT help or manage support tickets.")

    notice = st.session_state.pop("notice", None)

    if notice:
        st.success(notice)

    with st.container(border=True):

        with st.form("login_form"):

            username = st.text_input("Username")

            password = st.text_input("Password", type="password")

            submitted = st.form_submit_button("Sign in", type="primary")

    if submitted:

        if not username.strip() or not password:

            st.error("Please enter your username and password.")

        else:

            user = verify_login(username, password)

            if user:

                st.session_state.auth_user = user

                st.rerun()

            else:

                # Same message for "no such user" and "wrong password"
                st.error("Invalid username or password.")

    # -----------------------------
    # Admin password recovery
    # -----------------------------

    with st.expander("Forgot your admin password?"):

        if not setup_code_configured():

            st.caption(
                "Recovery is off until a SETUP_CODE is set in the server's "
                ".env file. Employees: ask an admin to reset your password."
            )

        else:

            st.caption(
                "Admins can reset their password with the server's setup "
                "code. Employees: ask an admin to reset your password."
            )

            with st.form("recovery_form", clear_on_submit=True):

                rc_code = st.text_input("Setup code", type="password")

                rc_user = st.text_input("Admin username")

                rc_password = st.text_input(
                    f"New password (at least {MIN_PASSWORD_LENGTH} characters)",
                    type="password"
                )

                rc_confirm = st.text_input(
                    "Confirm new password",
                    type="password"
                )

                rc_submitted = st.form_submit_button("Reset admin password")

            if rc_submitted:

                if rc_password != rc_confirm:

                    st.error("Passwords do not match.")

                else:

                    try:

                        recover_admin_password(rc_code, rc_user, rc_password)

                        st.success(
                            "Password reset. You can now sign in above."
                        )

                    except ValueError as error:

                        time.sleep(1)  # slows down guessing

                        st.error(str(error))


# -----------------------------
# Gate: setup, or login
# -----------------------------

if "auth_user" not in st.session_state:

    if admin_exists():
        show_login()
    else:
        show_setup()

    st.stop()


# -----------------------------
# Signed-in: load knowledge, show sidebar, show pages
# -----------------------------

load_knowledge_base()

user = st.session_state.auth_user

with st.sidebar:

    st.markdown(f"**👤 {user['username']}**")

    st.caption(f"Role: {user['role'].title()}")

    if st.button("Sign out"):

        for key in SESSION_KEYS:
            st.session_state.pop(key, None)

        st.rerun()


pages = [
    st.Page(
        "support_page.py",
        title="IT Support",
        icon="🤖",
        default=True
    )
]

# Only admins even get these pages in their menu
if user["role"] == "admin":

    pages.append(
        st.Page(
            "admin_page.py",
            title="Admin Dashboard",
            icon="🛠️"
        )
    )

    pages.append(
        st.Page(
            "users_page.py",
            title="User Management",
            icon="👥"
        )
    )

st.navigation(pages).run()
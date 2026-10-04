# users_page.py
#
# Admin-only page: create accounts, reset passwords, delete accounts.
# It is loaded by app.py for admins only. Do not run it directly.

import streamlit as st

from auth import (
    create_user,
    list_users,
    reset_password,
    delete_user,
    VALID_ROLES,
    MIN_PASSWORD_LENGTH,
)


# Safety check: the menu hides this page from employees, but we check the
# role again here too (defense in depth).
auth_user = st.session_state.get("auth_user")

if not auth_user or auth_user["role"] != "admin":

    st.error("You do not have permission to view this page.")

    st.stop()


current_user = auth_user["username"]

ROLE_LABELS = {"admin": "🛡️ Admin", "employee": "👤 Employee"}


st.title("👥 User Management")

st.write(
    "Create accounts for your employees and IT staff. "
    "Passwords are stored as salted hashes and can never be viewed."
)


# -----------------------------
# Create account
# -----------------------------

with st.container(border=True):

    st.subheader("➕ Create account")

    with st.form("create_user_form", clear_on_submit=True):

        new_username = st.text_input("Username")

        new_role = st.selectbox(
            "Role",
            list(VALID_ROLES),
            format_func=lambda role: ROLE_LABELS[role]
        )

        new_password = st.text_input(
            f"Temporary password (at least {MIN_PASSWORD_LENGTH} characters)",
            type="password"
        )

        confirm_password = st.text_input("Confirm password", type="password")

        submitted = st.form_submit_button("Create account", type="primary")

    if submitted:

        if new_password != confirm_password:

            st.error("Passwords do not match.")

        else:

            try:

                create_user(new_username, new_password, new_role)

                st.success(
                    f"Account '{new_username.strip().lower()}' created "
                    f"as {new_role}. Give the password to the user privately."
                )

            except ValueError as error:

                st.error(str(error))


# -----------------------------
# Existing accounts
# -----------------------------

st.subheader("Accounts")

users = list_users()

st.caption(f"{len(users)} account(s)")

for user_id, username, role, created_at in users:

    with st.container(border=True):

        st.markdown(f"**{username}**  ·  {ROLE_LABELS.get(role, role)}")

        st.caption(f"Created: {created_at}")

        with st.expander("Manage"):

            new_pw = st.text_input(
                "New password",
                type="password",
                key=f"reset_pw_{user_id}"
            )

            if st.button("Reset password", key=f"reset_btn_{user_id}"):

                try:

                    reset_password(username, new_pw)

                    st.success(f"Password for '{username}' was reset.")

                except ValueError as error:

                    st.error(str(error))

            st.divider()

            if username == current_user:

                st.caption(
                    "You cannot delete the account you are signed in with."
                )

            else:

                confirm_delete = st.checkbox(
                    f"Yes, permanently delete '{username}'",
                    key=f"del_confirm_{user_id}"
                )

                if st.button(
                    "Delete account",
                    key=f"del_btn_{user_id}",
                    disabled=not confirm_delete
                ):

                    try:

                        delete_user(username)

                        st.rerun()

                    except ValueError as error:

                        st.error(str(error))
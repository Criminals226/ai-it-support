

# admin_page.py
#
# The admin ticket dashboard (the old admin.py logic).
# It is loaded by app.py for admins only. Do not run it directly.

import streamlit as st

from tickets import get_tickets, update_ticket_status


STATUSES = ["Open", "In Progress", "Resolved"]


# Safety check: only admins see this page in the menu, but we check the
# role again here too (defense in depth).
auth_user = st.session_state.get("auth_user")

if not auth_user or auth_user["role"] != "admin":

    st.error("You do not have permission to view this page.")

    st.stop()


st.title("🛠️ IT Support Admin Dashboard")

st.write("Manage and monitor support tickets.")


tickets = get_tickets()


if not tickets:

    st.info("No support tickets found.")

else:

    for ticket in tickets:

        ticket_id, user, issue, category, priority, status, created_at = ticket

        with st.container(border=True):

            st.subheader(f"IT-{ticket_id:04d}")

            st.caption(f"Created: {created_at}")

            col1, col2, col3 = st.columns(3)

            col1.write(f"**User:** {user}")
            col2.write(f"**Category:** {category}")
            col3.write(f"**Priority:** {priority}")

            st.write(f"**Issue:** {issue}")

            new_status = st.selectbox(
                "Status",
                STATUSES,
                index=STATUSES.index(status) if status in STATUSES else 0,
                key=f"status_{ticket_id}"
            )

            if new_status != status:

                if st.button("Update Status", key=f"update_{ticket_id}"):

                    update_ticket_status(ticket_id, new_status)

                    st.success(f"Ticket IT-{ticket_id:04d} updated.")

                    st.rerun()
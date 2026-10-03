import streamlit as st

from tickets import (
    get_tickets,
    update_ticket_status
)


st.title(" IT Support Admin Dashboard")

st.write("Manage and monitor support tickets.")


tickets = get_tickets()


if not tickets:

    st.info("No support tickets found.")

else:

    for ticket in tickets:

        ticket_id = ticket[0]
        user = ticket[1]
        issue = ticket[2]
        category = ticket[3]
        priority = ticket[4]
        status = ticket[5]
        created_at = ticket[6]

        st.divider()

        st.subheader(
            f"IT-{ticket_id:04d}"
        )

        st.write(f"**User:** {user}")
        st.write(f"**Issue:** {issue}")
        st.write(f"**Category:** {category}")
        st.write(f"**Priority:** {priority}")
        st.write(f"**Created:** {created_at}")

        new_status = st.selectbox(
            "Status",
            [
                "Open",
                "In Progress",
                "Resolved"
            ],
            index=[
                "Open",
                "In Progress",
                "Resolved"
            ].index(status),
            key=f"status_{ticket_id}"
        )

        if new_status != status:

            if st.button(
                "Update Status",
                key=f"update_{ticket_id}"
            ):

                update_ticket_status(
                    ticket_id,
                    new_status
                )

                st.success(
                    f"Ticket IT-{ticket_id:04d} updated."
                )

                st.rerun()
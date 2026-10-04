# admin_page.py
#
# The admin ticket dashboard: summary numbers, a category chart,
# filters, search, sorting, and status updates.
# It is loaded by app.py for admins only. Do not run it directly.

import pandas as pd
import streamlit as st

from tickets import (
    get_tickets,
    update_ticket_status,
    delete_ticket,
    delete_resolved_tickets,
)


STATUSES = ["Open", "In Progress", "Resolved"]

PRIORITIES = ["Critical", "High", "Medium", "Low"]

PRIORITY_ICONS = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}

STATUS_ICONS = {"Open": "🆕", "In Progress": "🔧", "Resolved": "✅"}


# Safety check: only admins see this page in the menu, but we check the
# role again here too (defense in depth).
auth_user = st.session_state.get("auth_user")

if not auth_user or auth_user["role"] != "admin":

    st.error("You do not have permission to view this page.")

    st.stop()


st.title("🛠️ IT Support Admin Dashboard")

st.write("Monitor and manage support tickets.")


# Message that survives the page refresh after a status update
notice = st.session_state.pop("admin_notice", None)

if notice:
    st.success(notice)


tickets = get_tickets()

if not tickets:

    st.info("No support tickets found.")

    st.stop()


# -----------------------------
# Summary numbers
# -----------------------------

# Each ticket is: (id, user, issue, category, priority, status, created_at)

total = len(tickets)

open_count = sum(1 for t in tickets if t[5] == "Open")

in_progress_count = sum(1 for t in tickets if t[5] == "In Progress")

resolved_count = sum(1 for t in tickets if t[5] == "Resolved")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total", total)
col2.metric("Open", open_count)
col3.metric("In Progress", in_progress_count)
col4.metric("Resolved", resolved_count)


# -----------------------------
# Tickets by category
# -----------------------------

category_counts = {}

for t in tickets:
    category_counts[t[3]] = category_counts.get(t[3], 0) + 1

with st.container(border=True):

    st.caption("Tickets by category")

    st.bar_chart(pd.Series(category_counts))


# -----------------------------
# Clean up resolved tickets
# -----------------------------

if resolved_count > 0:

    with st.expander(f"🧹 Clean up resolved tickets ({resolved_count})"):

        st.warning(
            "This permanently deletes every ticket whose status is Resolved. "
            "Open and In Progress tickets are never touched."
        )

        confirm_bulk = st.checkbox(
            f"Yes, permanently delete all {resolved_count} resolved ticket(s)",
            key="confirm_bulk_delete"
        )

        if st.button(
            "Delete all resolved tickets",
            key="bulk_delete_btn",
            disabled=not confirm_bulk
        ):

            deleted = delete_resolved_tickets()

            st.session_state.admin_notice = (
                f"Deleted {deleted} resolved ticket(s)."
            )

            st.rerun()


# -----------------------------
# Filters, search and sorting
# -----------------------------

st.subheader("Tickets")

categories = sorted({t[3] for t in tickets})

f1, f2, f3 = st.columns(3)

status_filter = f1.selectbox(
    "Filter by status", ["All"] + STATUSES, key="filter_status"
)

priority_filter = f2.selectbox(
    "Filter by priority", ["All"] + PRIORITIES, key="filter_priority"
)

category_filter = f3.selectbox(
    "Filter by category", ["All"] + categories, key="filter_category"
)

search = st.text_input(
    "Search",
    placeholder="Ticket number, user, category or issue text",
    key="filter_search"
)

sort_order = st.radio(
    "Sort by",
    ["Newest first", "Highest priority first"],
    horizontal=True,
    key="filter_sort"
)


def matches(ticket):

    ticket_id, user, issue, category, priority, status, created_at = ticket

    if status_filter != "All" and status != status_filter:
        return False

    if priority_filter != "All" and priority != priority_filter:
        return False

    if category_filter != "All" and category != category_filter:
        return False

    if search.strip():

        text = (
            f"it-{ticket_id:04d} {user} {category} "
            f"{priority} {status} {issue}"
        ).lower()

        if search.strip().lower() not in text:
            return False

    return True


visible = [t for t in tickets if matches(t)]

if sort_order == "Highest priority first":

    rank = {name: index for index, name in enumerate(PRIORITIES)}

    # Highest priority first; newest first inside the same priority
    visible.sort(key=lambda t: (rank.get(t[4], 99), -t[0]))

st.caption(f"Showing {len(visible)} of {total} tickets")


# -----------------------------
# Ticket cards
# -----------------------------

if not visible:

    st.info("No tickets match these filters.")

for ticket in visible:

    ticket_id, user, issue, category, priority, status, created_at = ticket

    with st.container(border=True):

        st.markdown(
            f"### {PRIORITY_ICONS.get(priority, '⚪')} "
            f"IT-{ticket_id:04d} · {category}"
        )

        st.caption(
            f"{priority} priority · "
            f"{STATUS_ICONS.get(status, '')} {status} · "
            f"Created {created_at} · by {user}"
        )

        st.write(issue)

        new_status = st.selectbox(
            "Change status",
            STATUSES,
            index=STATUSES.index(status) if status in STATUSES else 0,
            key=f"status_{ticket_id}"
        )

        if new_status != status:

            if st.button("Update Status", key=f"update_{ticket_id}"):

                update_ticket_status(ticket_id, new_status)

                st.session_state.admin_notice = (
                    f"Ticket IT-{ticket_id:04d} is now {new_status}."
                )

                st.rerun()

        if status == "Resolved":

            with st.expander("🗑️ Delete this ticket"):

                confirm_one = st.checkbox(
                    "Yes, permanently delete this resolved ticket",
                    key=f"del_confirm_{ticket_id}"
                )

                if st.button(
                    "Delete ticket",
                    key=f"del_btn_{ticket_id}",
                    disabled=not confirm_one
                ):

                    if delete_ticket(ticket_id):

                        st.session_state.admin_notice = (
                            f"Ticket IT-{ticket_id:04d} was deleted."
                        )

                        st.rerun()

                    else:

                        st.error("Only resolved tickets can be deleted.")
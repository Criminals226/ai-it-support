# support_page.py
#
# The employee support page (the old app.py logic, with a nicer layout).
# It is loaded by app.py after login. Do not run it directly.

import streamlit as st

from rag import search_knowledge, generate_answer
from tickets import create_ticket
from escalation import check_escalation
from ticket_intelligence import classify_ticket


# The logged-in user comes from the login (no more typing a name)
user = st.session_state.auth_user["username"]


# -----------------------------
# Header
# -----------------------------

st.title("🤖 AI IT Support")

st.write(
    f"Hello, **{user}**. Describe your IT problem and the assistant "
    "will guide you through troubleshooting."
)


# -----------------------------
# Problem
# -----------------------------

question = st.text_area(
    "Describe your IT problem",
    placeholder="Example: My VPN is not connecting.",
    height=120
)


# -----------------------------
# Ask AI
# -----------------------------

if st.button("🤖 Ask AI", type="primary"):

    if not question.strip():

        st.warning("Please describe your IT problem first.")

    else:

        with st.spinner("Searching IT knowledge and generating answer..."):

            results = search_knowledge(question)

            answer = generate_answer(question, results)

        st.session_state.answer = answer
        st.session_state.question = question
        st.session_state.results = results
        st.session_state.escalation = check_escalation(question, results)

        # A new question means no ticket has been created for it yet
        st.session_state.pop("ticket_info", None)


# -----------------------------
# Answer
# -----------------------------

if "answer" in st.session_state:

    st.divider()

    with st.container(border=True):

        st.subheader("🤖 AI Support")

        st.write(st.session_state.answer)

    escalation = st.session_state.get(
        "escalation",
        {"needs_escalation": False, "reasons": []}
    )

    suggestion = classify_ticket(st.session_state.question)

    # -----------------------------
    # Ticket section
    # -----------------------------

    if "ticket_info" in st.session_state:

        info = st.session_state.ticket_info

        st.success(
            f"Support ticket IT-{info['id']:04d} has been created.\n\n"
            f"**Category:** {info['category']}  \n"
            f"**Priority:** {info['priority']}"
        )

    else:

        if escalation["needs_escalation"]:

            st.warning("**This issue may require IT assistance.**")

            for reason in escalation["reasons"]:
                st.write(f"- {reason}")

            st.write("Would you like to create a support ticket?")

        else:

            st.subheader("Need further help?")

            st.write(
                "If the troubleshooting steps did not solve your problem, "
                "you can create an IT support ticket."
            )

        st.caption(
            f"This ticket would be filed as: {suggestion['category']} · "
            f"{suggestion['priority']} priority"
        )

        if st.button("🎫 Create Support Ticket"):

            ticket_id = create_ticket(
                user=user,
                issue=st.session_state.question,
                category=suggestion["category"],
                priority=suggestion["priority"]
            )

            st.session_state.ticket_info = {
                "id": ticket_id,
                "category": suggestion["category"],
                "priority": suggestion["priority"]
            }

            st.rerun()

    # -----------------------------
    # Knowledge used
    # -----------------------------

    with st.expander("🔎 View knowledge used by AI"):

        for result in st.session_state.results:

            st.markdown("---")

            st.write(result)
import streamlit as st

from rag import (build_knowledge_base, search_knowledge, generate_answer)

from tickets import (
    init_db,
    create_ticket
)

from escalation import check_escalation

from ticket_intelligence import classify_ticket


# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="AI IT Support",
    page_icon="🤖",
    layout="centered"
)


# -----------------------------
# Initialize Systems
# -----------------------------

init_db()


if "knowledge_loaded" not in st.session_state:

    with st.spinner("Loading IT knowledge base..."):

        build_knowledge_base()

    st.session_state.knowledge_loaded = True


# -----------------------------
# Title
# -----------------------------

st.title("🤖 AI IT Support")

st.write(
    "Describe your IT problem and the AI support assistant "
    "will provide troubleshooting assistance."
)


# -----------------------------
# User Information
# -----------------------------

user = st.text_input(
    "Your name:",
    placeholder="Example: Aleena"
)


# -----------------------------
# Problem
# -----------------------------

question = st.text_area(
    "Describe your IT problem:",
    placeholder="Example: My VPN is not connecting.",
    height=120
)


# -----------------------------
# Ask AI
# -----------------------------

if st.button("🤖 Ask AI", type="primary"):

    if not question.strip():

        st.warning(
            "Please describe your IT problem first."
        )

    else:

        with st.spinner(
            "Searching IT knowledge and generating answer..."
        ):

            results = search_knowledge(
                question
            )

            answer = generate_answer(
                question,
                results
            )


        # Store results for ticket creation
        st.session_state.answer = answer
        st.session_state.question = question
        st.session_state.results = results
        st.session_state.user = user if user else "Anonymous"
        st.session_state.escalation = check_escalation(question, results)


# -----------------------------
# Display AI Answer
# -----------------------------

if "answer" in st.session_state:

    st.subheader("🤖 AI Support")

    st.write(
        st.session_state.answer
    )


    # -----------------------------
    # Ticket Section
    # -----------------------------

    st.divider()

    escalation = st.session_state.get(
        "escalation",
        {"needs_escalation": False, "reasons": []}
    )

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


    if st.button(
        "🎫 Create Support Ticket"
    ):

        classification = classify_ticket(
            st.session_state.question
        )

        ticket_id = create_ticket(

            user=st.session_state.user,

            issue=st.session_state.question,

            category=classification["category"],

            priority=classification["priority"]
        )


        st.success(
            f"Support ticket IT-{ticket_id:04d} "
            "has been created successfully.\n\n"
            f"**Category:** {classification['category']}  \n"
            f"**Priority:** {classification['priority']}"
        )


    # -----------------------------
    # Knowledge Used
    # -----------------------------

    with st.expander(
        "🔎 View knowledge used by AI"
    ):

        for result in st.session_state.results:

            st.markdown("---")

            st.write(result)
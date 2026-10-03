# ticket_intelligence.py
#
# Phase 2, Step 1: decide a ticket's category and priority.
#
# Same idea as escalation.py: simple, readable rules, no LLM.
# Easy to explain, easy to test, and a user cannot talk it into a
# lower priority with a clever prompt.

from escalation import check_escalation


# -----------------------------
# Categories
# -----------------------------

# Security is handled separately (it comes from the escalation check).
# For the rest, the category with the MOST matching keywords wins.
# On a tie, the category listed first wins.

CATEGORY_KEYWORDS = {
    "VPN": ["vpn"],
    "Wi-Fi": ["wi-fi", "wifi", "wireless", "router", "no internet"],
    "Password": [
        "password", "login", "log in", "sign in", "mfa",
        "locked out", "account locked", "account is locked",
    ],
    "Email": ["email", "e-mail", "outlook", "mailbox", "inbox"],
    "Printer": ["printer", "print", "scanner", "toner"],
}


# Phrases where the employee says it is not urgent
LOW_PRIORITY_PHRASES = [
    "not urgent", "no rush", "when you have time", "minor", "whenever",
]


def classify_category(question, codes):

    # A suspected security incident always becomes a Security ticket
    if "security_incident" in codes:
        return "Security"

    text = question.lower().replace("\u2019", "'")

    best_category = "General IT"
    best_score = 0

    for category, keywords in CATEGORY_KEYWORDS.items():

        score = sum(1 for keyword in keywords if keyword in text)

        if score > best_score:
            best_category = category
            best_score = score

    return best_category


# -----------------------------
# Priorities
# -----------------------------

def classify_priority(question, codes):

    text = question.lower().replace("\u2019", "'")

    # Critical: a security incident, or a service that is down for many people
    if "security_incident" in codes:
        return "Critical"

    if "multiple_users" in codes and "service_down" in codes:
        return "Critical"

    # High: many people affected, locked account, or service down
    if any(c in codes for c in ("multiple_users", "service_down", "account_locked")):
        return "High"

    # Low: the employee says it is not urgent
    if any(phrase in text for phrase in LOW_PRIORITY_PHRASES):
        return "Low"

    # Medium: everything else (including "troubleshooting already failed")
    return "Medium"


# -----------------------------
# Main function
# -----------------------------

def classify_ticket(question):
    """
    Returns {"category": "...", "priority": "..."}
    """

    # Reuse the escalation signals (locked account, multiple users, ...)
    codes = check_escalation(question)["codes"]

    return {
        "category": classify_category(question, codes),
        "priority": classify_priority(question, codes),
    }
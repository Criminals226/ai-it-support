# escalation.py
#
# Phase 1, Step 1: decide whether an issue needs IT escalation.
#
# This is deliberately simple and rule-based (no LLM). The rules mirror the
# "Escalation" sections in your knowledge files (locked account, multiple
# users affected, server unavailable, ...). Because there is no LLM involved,
# a user cannot talk this check into hiding an escalation (prompt injection).


# Each rule: (short code, reason shown to the user, phrases to look for)
ESCALATION_RULES = [
    (
        "security_incident",
        "Possible security incident",
        [
            "hacked", "compromised", "phishing", "suspicious",
            "malware", "virus", "ransomware", "stolen", "unauthorized",
        ],
    ),
    (
        "account_locked",
        "Account appears to be locked",
        [
            "locked out", "account locked", "account is locked",
            "account has been locked", "account got locked",
        ],
    ),
    (
        "multiple_users",
        "Multiple employees may be affected",
        [
            "everyone", "everybody", "whole office", "entire office",
            "my team", "all of us", "other people", "colleagues",
            "coworkers", "multiple users", "multiple employees",
        ],
    ),
    (
        "service_down",
        "A service or server may be unavailable",
        [
            "server is down", "server down", "service is down",
            "service down", "outage",
        ],
    ),
    (
        "troubleshooting_failed",
        "Basic troubleshooting has already been tried",
        [
            "already tried", "already checked", "already restarted",
            "still not working", "still doesn't work", "still does not work",
            "still failing", "didn't work", "did not work", "nothing works",
            "tried everything", "still can't", "still cannot",
        ],
    ),
    (
        "admin_required",
        "May need administrator access",
        [
            "administrator", "admin rights", "admin access", "hardware error",
        ],
    ),
]


def check_escalation(question, relevant_chunks=None):
    """
    Returns a dictionary:
        {
            "needs_escalation": True or False,
            "reasons": ["reason 1", "reason 2", ...]
        }

    question:        the employee's text
    relevant_chunks: the list returned by search_knowledge().
                     If it is an empty list, no knowledge matched,
                     so we suggest escalation.
                     Pass None to skip this check.
    """

    # Lowercase, and turn curly apostrophes into normal ones
    text = question.lower().replace("\u2019", "'")

    reasons = []
    codes = []

    if relevant_chunks is not None and len(relevant_chunks) == 0:
        reasons.append("No relevant knowledge found")
        codes.append("no_knowledge")

    for code, reason, phrases in ESCALATION_RULES:

        if any(phrase in text for phrase in phrases):
            reasons.append(reason)
            codes.append(code)

    # "reasons" is text for people to read.
    # "codes" is short labels for code to use (Phase 2 uses these).
    return {
        "needs_escalation": len(reasons) > 0,
        "reasons": reasons,
        "codes": codes,
    }
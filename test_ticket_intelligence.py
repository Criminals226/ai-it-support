# test_ticket_intelligence.py
# Run with:  python test_ticket_intelligence.py

from ticket_intelligence import classify_ticket


# (question, expected category, expected priority)
tests = [
    ("My VPN is not connecting", "VPN", "Medium"),
    ("Wi-Fi is not working", "Wi-Fi", "Medium"),
    ("I forgot my password", "Password", "Medium"),
    ("My account is locked and I can't log in", "Password", "High"),
    ("The VPN server is down for everyone in my team", "VPN", "Critical"),
    ("I think my laptop got hacked", "Security", "Critical"),
    ("I can't send emails", "Email", "Medium"),
    ("The printer is out of toner, not urgent", "Printer", "Low"),
    ("My monitor is flickering", "General IT", "Medium"),
    ("I clicked a suspicious link in an email", "Security", "Critical"),
    ("Everyone in the office can't print", "Printer", "High"),
]


passed = 0

for question, expected_category, expected_priority in tests:

    result = classify_ticket(question)

    ok = (
        result["category"] == expected_category
        and result["priority"] == expected_priority
    )

    if ok:
        passed += 1

    status = "PASS" if ok else "FAIL"

    print(f"{status} | {question}")
    print(
        f"     category={result['category']}  "
        f"priority={result['priority']}"
    )


print(f"\n{passed}/{len(tests)} tests passed")
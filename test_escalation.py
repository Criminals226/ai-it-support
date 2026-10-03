# test_escalation.py
# Run with:  python test_escalation.py

from escalation import check_escalation


# (question, chunks returned by search, should it escalate?)
# ["chunk"] means "the knowledge base found something relevant"
# []        means "nothing relevant was found"
tests = [
    ("My VPN is not connecting", ["chunk"], False),
    ("My account is locked and I can't log in", ["chunk"], True),
    ("The VPN server is down for everyone in my team", ["chunk"], True),
    ("I think my laptop got hacked", ["chunk"], True),
    ("I already restarted it and it's still not working", ["chunk"], True),
    ("How do I bake a chocolate cake?", [], True),
    ("Wi-Fi is not working", ["chunk"], False),
]


passed = 0

for question, chunks, expected in tests:

    result = check_escalation(question, chunks)

    ok = result["needs_escalation"] == expected

    if ok:
        passed += 1

    status = "PASS" if ok else "FAIL"

    print(f"{status} | {question}")
    print(
        f"     needs_escalation={result['needs_escalation']}  "
        f"reasons={result['reasons']}"
    )


print(f"\n{passed}/{len(tests)} tests passed")
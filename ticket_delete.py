# test_ticket_delete.py
# Run with:  python test_ticket_delete.py
#
# Uses a temporary database, so it does NOT touch your real tickets.

import os
import tempfile

import tickets


# Point the tickets module at a temporary database for this test only
tickets.DB_PATH = os.path.join(tempfile.mkdtemp(), "test_tickets.db")

tickets.init_db()


open_id = tickets.create_ticket("u1", "open issue", "VPN", "Medium")
resolved_a = tickets.create_ticket("u2", "resolved issue 1", "Wi-Fi", "Low")
resolved_b = tickets.create_ticket("u3", "resolved issue 2", "Email", "Low")

tickets.update_ticket_status(resolved_a, "Resolved")
tickets.update_ticket_status(resolved_b, "Resolved")


results = []


def check(description, condition):

    results.append(condition)

    status = "PASS" if condition else "FAIL"

    print(f"{status} | {description}")


def ids():

    return [ticket[0] for ticket in tickets.get_tickets()]


check(
    "An open ticket cannot be deleted",
    tickets.delete_ticket(open_id) is False and open_id in ids()
)

check(
    "A resolved ticket can be deleted",
    tickets.delete_ticket(resolved_a) is True and resolved_a not in ids()
)

check(
    "Deleting an unknown ticket returns False",
    tickets.delete_ticket(9999) is False
)

check(
    "Bulk delete removes only resolved tickets and returns the count",
    tickets.delete_resolved_tickets() == 1 and ids() == [open_id]
)

check(
    "Bulk delete with nothing resolved deletes nothing",
    tickets.delete_resolved_tickets() == 0 and ids() == [open_id]
)


print(f"\n{sum(results)}/{len(results)} checks passed")
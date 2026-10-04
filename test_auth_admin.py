# test_auth_admin.py
# Run with:  python test_auth_admin.py
#
# Tests the account-management functions on a temporary database.
# It does NOT touch your real tickets.db.

import os
import tempfile

from auth import (
    init_users_table,
    create_user,
    verify_login,
    list_users,
    reset_password,
    delete_user,
)


db_file = os.path.join(tempfile.mkdtemp(), "test_users.db")

init_users_table(db_file)

create_user("boss", "AdminPass123", "admin", db_file)
create_user("sam", "EmployeePass1", "employee", db_file)


results = []


def check(description, condition):

    results.append(condition)

    status = "PASS" if condition else "FAIL"

    print(f"{status} | {description}")


def raises_value_error(function, *args):

    try:
        function(*args)
        return False
    except ValueError:
        return True


def usernames():

    return [user[1] for user in list_users(db_file)]


check("User list shows both accounts", usernames() == ["boss", "sam"])


reset_password("sam", "NewPassword99", db_file)

check(
    "Old password stops working after reset",
    verify_login("sam", "EmployeePass1", db_file) is None
)

check(
    "New password works after reset",
    verify_login("sam", "NewPassword99", db_file) is not None
)

check(
    "Too-short new password is rejected",
    raises_value_error(reset_password, "sam", "short", db_file)
)

check(
    "Resetting an unknown user is rejected",
    raises_value_error(reset_password, "nobody", "LongEnough123", db_file)
)


delete_user("sam", db_file)

check("Deleted user disappears from the list", usernames() == ["boss"])

check(
    "Deleted user can no longer log in",
    verify_login("sam", "NewPassword99", db_file) is None
)

check(
    "Last admin cannot be deleted",
    raises_value_error(delete_user, "boss", db_file)
    and usernames() == ["boss"]
)


create_user("boss2", "AdminPass456", "admin", db_file)

delete_user("boss", db_file)

check(
    "An admin can be deleted when another admin exists",
    usernames() == ["boss2"]
)

check(
    "Deleting an unknown user is rejected",
    raises_value_error(delete_user, "nobody", db_file)
)


print(f"\n{sum(results)}/{len(results)} checks passed")
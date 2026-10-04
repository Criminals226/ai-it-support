# test_setup.py
# Run with:  python test_setup.py
#
# Tests first-run setup and admin recovery on temporary databases.
# It does NOT touch your real tickets.db or your real .env.

import os
import tempfile

from auth import (
    init_users_table,
    create_user,
    verify_login,
    admin_exists,
    setup_code_configured,
    create_first_admin,
    recover_admin_password,
)


GOOD_CODE = "test-setup-code-12345"

os.environ["SETUP_CODE"] = GOOD_CODE


def new_db():

    path = os.path.join(tempfile.mkdtemp(), "test_users.db")

    init_users_table(path)

    return path


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


db = new_db()

check("A new database has no admin", admin_exists(db) is False)

check(
    "Wrong setup code cannot create the first admin",
    raises_value_error(
        create_first_admin, "wrong-code-123456", "boss", "AdminPass123", db
    )
    and admin_exists(db) is False
)

create_first_admin(GOOD_CODE, "boss", "AdminPass123", db)

check(
    "Correct setup code creates the first admin, who can log in",
    admin_exists(db) is True
    and verify_login("boss", "AdminPass123", db)["role"] == "admin"
)

check(
    "Setup is refused once an admin exists, even with the right code",
    raises_value_error(
        create_first_admin, GOOD_CODE, "intruder", "AdminPass123", db
    )
)

db_employee_only = new_db()

create_user("sam", "EmployeePass1", "employee", db_employee_only)

check(
    "An employee account does not count as an admin",
    admin_exists(db_employee_only) is False
)

check(
    "Recovery with a wrong code is rejected and the password is unchanged",
    raises_value_error(
        recover_admin_password, "wrong-code-123456", "boss", "BrandNew1234", db
    )
    and verify_login("boss", "AdminPass123", db) is not None
)

recover_admin_password(GOOD_CODE, "boss", "BrandNew1234", db)

check(
    "Recovery with the right code sets a new admin password",
    verify_login("boss", "AdminPass123", db) is None
    and verify_login("boss", "BrandNew1234", db) is not None
)

create_user("sam", "EmployeePass1", "employee", db)

check(
    "Recovery cannot be used on an employee account",
    raises_value_error(
        recover_admin_password, GOOD_CODE, "sam", "BrandNew1234", db
    )
)

os.environ["SETUP_CODE"] = "short"

check(
    "A too-short SETUP_CODE counts as not configured",
    setup_code_configured() is False
    and raises_value_error(
        create_first_admin, "short", "boss2", "AdminPass123", new_db()
    )
)


print(f"\n{sum(results)}/{len(results)} checks passed")
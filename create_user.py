# create_user.py
# Run with:  python create_user.py
#
# Creates an employee or admin account.
# The password is typed hidden (nothing shows on screen), so it never
# appears in your code, your terminal history, or this chat.

import getpass

from auth import init_users_table, create_user, VALID_ROLES


init_users_table()

username = input("Username: ").strip()

role = input(f"Role ({'/'.join(VALID_ROLES)}): ").strip().lower()

password = getpass.getpass("Password (hidden): ")

confirm = getpass.getpass("Confirm password: ")


if password != confirm:

    print("Passwords do not match. No user was created.")

    raise SystemExit(1)


try:

    create_user(username, password, role)

    print(f"User '{username.lower()}' created with role '{role}'.")

except ValueError as error:

    print(f"Could not create user: {error}")
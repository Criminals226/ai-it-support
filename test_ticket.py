from tickets import (
    init_db,
    create_ticket,
    get_tickets
)


# Create database
init_db()


# Create a test ticket
ticket_id = create_ticket(
    user="Test User",
    issue="VPN is not connecting",
    category="VPN",
    priority="Medium"
)


print(f"Created ticket: IT-{ticket_id:04d}")


# Get all tickets
tickets = get_tickets()


print("\nAll Tickets:\n")


for ticket in tickets:

    print(ticket)
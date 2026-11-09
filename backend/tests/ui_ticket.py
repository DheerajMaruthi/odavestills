"""Print a Clerk sign-in ticket for UI tests: python ui_ticket.py <email>"""
import sys

from conftest import sign_in_ticket

print(sign_in_ticket(sys.argv[1]))

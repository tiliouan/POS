"""
Test Cash Drawer Dialog Fix
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.user_manager import user_manager
from utils.session_manager import SessionManager

def test_login_flow():
    """Test the login flow to see if cash drawer is triggered multiple times."""
    
    # Setup
    session_manager = SessionManager()
    
    # Simulate login
    print("Testing login flow...")
    
    # Check initial state
    print(f"User logged in: {user_manager.is_logged_in()}")
    print(f"Needs cash drawer: {session_manager.needs_cash_drawer_opening()}")
    
    # This simulates what happens during login
    if user_manager.is_logged_in() and session_manager:
        needs_drawer = session_manager.needs_cash_drawer_opening()
        if needs_drawer:
            print("TRIGGER 1: Cash drawer opening needed (initial check)")
    
    # This simulates what happens in on_login_success
    if session_manager:
        needs_drawer = session_manager.needs_cash_drawer_opening()
        if needs_drawer:
            print("TRIGGER 2: Cash drawer opening needed (after login)")
    
    print("Test completed - should only see ONE trigger now")

if __name__ == "__main__":
    test_login_flow()

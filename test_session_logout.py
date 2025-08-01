#!/usr/bin/env python3
"""
Test script to verify session manager and logout flag logic
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.session_manager import SessionManager
    
    print("Testing session manager logout flow...")
    
    # Create session manager
    session_manager = SessionManager()
    
    # Check initial state
    print(f"Needs cash drawer opening initially: {session_manager.needs_cash_drawer_opening()}")
    print(f"Logout flag file exists: {os.path.exists('logout_flag.txt')}")
    
    # Simulate ending a session (logout)
    print("\nSimulating logout...")
    session_manager.end_session("Test logout")
    
    # Check state after logout
    print(f"After logout - logout flag exists: {os.path.exists('logout_flag.txt')}")
    if os.path.exists('logout_flag.txt'):
        with open('logout_flag.txt', 'r') as f:
            print(f"Logout flag content: {f.read()}")
    
    # Check if cash drawer would be needed
    session_manager_new = SessionManager()
    print(f"New session manager - needs cash drawer: {session_manager_new.needs_cash_drawer_opening()}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

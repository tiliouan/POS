#!/usr/bin/env python3
"""
Test script to verify login cancel behavior
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dialogs.login_dialog import LoginDialog
    from database.user_manager import user_manager
    
    print("Testing login cancel behavior...")
    
    # Check initial state
    print(f"Is logged in initially: {user_manager.is_logged_in()}")
    print(f"Current user: {user_manager.current_user}")
    
    # Create a test login dialog
    def test_callback(user):
        print(f"Callback called with user: {user}")
    
    print("\nCreating login dialog...")
    login_dialog = LoginDialog(None, test_callback)
    
    # This would show the dialog in real usage, but for testing we'll simulate cancel
    print("Simulating cancel action...")
    login_dialog._cancel()
    
    print(f"After cancel - user is: {login_dialog.user}")
    print(f"User manager state - logged in: {user_manager.is_logged_in()}")
    print(f"User manager current user: {user_manager.current_user}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

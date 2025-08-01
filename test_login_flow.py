#!/usr/bin/env python3
"""
Test script to verify login flow
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database.user_manager import user_manager
    
    print("Testing login flow...")
    
    # Check initial state (should be logged out)
    print(f"Is logged in initially: {user_manager.is_logged_in()}")
    print(f"Current user: {user_manager.current_user}")
    
    # This should be None/False when application starts fresh
    if not user_manager.is_logged_in():
        print("✅ Login dialog should appear on startup")
    else:
        print("❌ Login dialog may not appear - user seems logged in")
        
    # Test manual logout
    if user_manager.current_user:
        print(f"Logging out user: {user_manager.current_user.name}")
        user_manager.logout()
        print(f"After logout - Is logged in: {user_manager.is_logged_in()}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

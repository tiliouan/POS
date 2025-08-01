#!/usr/bin/env python3
"""
Quick test to check existing users in the database
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database.user_manager import UserManager
    
    print("Checking users in database...")
    um = UserManager()
    users = um.get_all_users()
    
    if users:
        print(f"\nFound {len(users)} users:")
        print("-" * 50)
        for user in users:
            print(f"Username: {user.username}")
            print(f"Name: {user.name}")
            print(f"Role: {user.role.value}")
            print(f"Status: {user.status.value}")
            print("-" * 30)
    else:
        print("No users found in database.")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

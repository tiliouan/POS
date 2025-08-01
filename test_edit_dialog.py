"""
Test Edit User Dialog
====================

Test script to verify the Edit User dialog shows the Apply button.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.user_manager import user_manager
from models.user import User, UserRole, UserStatus
from dialogs.login_dialog import EditUserDialog

def test_edit_dialog():
    """Test the edit user dialog."""
    print("🧪 Testing Edit User Dialog")
    print("=" * 40)
    
    # Login as admin
    if user_manager.login("admin", "admin123"):
        print("✅ Admin login successful")
    else:
        print("❌ Admin login failed")
        return
    
    # Get a user to edit
    users = user_manager.get_all_users()
    test_user = None
    for user in users:
        if user.username != "admin":  # Don't edit admin
            test_user = user
            break
    
    if not test_user:
        print("❌ No test user found")
        return
    
    print(f"📝 Testing edit dialog for user: {test_user.username} ({test_user.name})")
    
    # Create root window
    root = tk.Tk()
    root.withdraw()  # Hide root window
    
    # Create and show edit dialog
    edit_dialog = EditUserDialog(root, test_user)
    print("🖥️ Opening Edit User Dialog...")
    print("   Check if you can see the 'Apply' button!")
    print("   Dialog size should be 400x350")
    
    result = edit_dialog.show()
    
    if result:
        print("✅ User was updated")
    else:
        print("ℹ️ Dialog was cancelled")
    
    root.destroy()
    print("🎉 Edit Dialog Test Complete!")

if __name__ == "__main__":
    test_edit_dialog()

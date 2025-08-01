"""
Simple Edit User Dialog Test
============================

Simplified test to verify button visibility.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.user_manager import user_manager
from models.user import User, UserRole, UserStatus

def test_simple_dialog():
    """Test a simple edit dialog."""
    
    # Login as admin
    if not user_manager.login("admin", "admin123"):
        print("❌ Login failed")
        return
    
    # Get a test user
    users = user_manager.get_all_users()
    test_user = users[0] if users else None
    
    if not test_user:
        print("❌ No users found")
        return
    
    # Create a simple dialog
    root = tk.Tk()
    root.title("Test Edit Dialog")
    root.geometry("450x400")
    
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    ttk.Label(main_frame, text=f"Edit User: {test_user.username}", 
             font=("Arial", 12, "bold")).pack(pady=(0, 20))
    
    # Username field
    ttk.Label(main_frame, text="Username:").pack(anchor=tk.W, pady=(0, 5))
    username_entry = ttk.Entry(main_frame)
    username_entry.pack(fill=tk.X, pady=(0, 10))
    username_entry.insert(0, test_user.username)
    username_entry.config(state="disabled")
    
    # Name field
    ttk.Label(main_frame, text="Full Name:").pack(anchor=tk.W, pady=(0, 5))
    name_entry = ttk.Entry(main_frame)
    name_entry.pack(fill=tk.X, pady=(0, 10))
    name_entry.insert(0, test_user.name)
    
    # Role field
    ttk.Label(main_frame, text="Role:").pack(anchor=tk.W, pady=(0, 5))
    role_combo = ttk.Combobox(main_frame, values=["Cashier", "Manager", "Admin"], state="readonly")
    role_combo.set(test_user.role.value.title())
    role_combo.pack(fill=tk.X, pady=(0, 10))
    
    # Status field
    ttk.Label(main_frame, text="Status:").pack(anchor=tk.W, pady=(0, 5))
    status_combo = ttk.Combobox(main_frame, values=["Active", "Inactive", "Suspended"], state="readonly")
    status_combo.set(test_user.status.value.title())
    status_combo.pack(fill=tk.X, pady=(0, 20))
    
    # Note
    ttk.Label(main_frame, text="Note: Use 'Change Password' to update user password",
             font=("Arial", 9), foreground="#666").pack(pady=(0, 10))
    
    # Buttons frame
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(fill=tk.X)
    
    def apply_changes():
        print(f"✅ Apply button clicked!")
        print(f"   Name: {name_entry.get()}")
        print(f"   Role: {role_combo.get()}")
        print(f"   Status: {status_combo.get()}")
        root.destroy()
    
    def cancel_changes():
        print("❌ Cancel button clicked!")
        root.destroy()
    
    # Apply button
    apply_btn = ttk.Button(buttons_frame, text="Apply", command=apply_changes)
    apply_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    # Cancel button  
    cancel_btn = ttk.Button(buttons_frame, text="Cancel", command=cancel_changes)
    cancel_btn.pack(side=tk.LEFT)
    
    print("🖥️ Dialog opened - Check if you can see both Apply and Cancel buttons!")
    print("   Window size: 450x400")
    print("   Try changing values and clicking Apply")
    
    root.mainloop()

if __name__ == "__main__":
    test_simple_dialog()

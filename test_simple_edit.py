"""
Test Edit Dialog Without Virtual Keyboard
==========================================

Test the edit dialog without virtual keyboard to see if that's causing issues.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.user_manager import user_manager
from models.user import User, UserRole, UserStatus

class SimpleEditUserDialog:
    """Simplified edit user dialog without virtual keyboard."""
    
    def __init__(self, parent, user: User):
        self.parent = parent
        self.user = user
        self.root = None
        self.result = False
        
    def show(self) -> bool:
        """Show the dialog."""
        self.root = tk.Toplevel(self.parent)
        self.root.title("Edit User (Simple)")
        self.root.geometry("450x500")
        self.root.resizable(True, True)
        
        self._create_widgets()
        
        self.root.transient(self.parent)
        self.root.grab_set()
        self.root.wait_window()
        
        return self.result
    
    def _create_widgets(self):
        """Create widgets."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text=f"Edit User: {self.user.username}",
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        # Username
        ttk.Label(main_frame, text="Username:").pack(anchor=tk.W, pady=(0, 5))
        self.username_entry = ttk.Entry(main_frame)
        self.username_entry.pack(fill=tk.X, pady=(0, 10))
        self.username_entry.insert(0, self.user.username)
        self.username_entry.config(state="disabled")
        
        # Name
        ttk.Label(main_frame, text="Full Name:").pack(anchor=tk.W, pady=(0, 5))
        self.name_entry = ttk.Entry(main_frame)
        self.name_entry.pack(fill=tk.X, pady=(0, 10))
        self.name_entry.insert(0, self.user.name)
        
        # Role
        ttk.Label(main_frame, text="Role:").pack(anchor=tk.W, pady=(0, 5))
        self.role_combo = ttk.Combobox(main_frame, values=["Cashier", "Manager", "Admin"], state="readonly")
        if self.user.role == UserRole.ADMIN:
            self.role_combo.set("Admin")
        elif self.user.role == UserRole.MANAGER:
            self.role_combo.set("Manager")
        else:
            self.role_combo.set("Cashier")
        self.role_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Status
        ttk.Label(main_frame, text="Status:").pack(anchor=tk.W, pady=(0, 5))
        self.status_combo = ttk.Combobox(main_frame, values=["Active", "Inactive", "Suspended"], state="readonly")
        if self.user.status == UserStatus.ACTIVE:
            self.status_combo.set("Active")
        elif self.user.status == UserStatus.INACTIVE:
            self.status_combo.set("Inactive")
        else:
            self.status_combo.set("Suspended")
        self.status_combo.pack(fill=tk.X, pady=(0, 20))
        
        # Note
        ttk.Label(main_frame, text="Note: Use 'Change Password' to update user password",
                 font=("Arial", 9), foreground="#666").pack(pady=(0, 20))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Apply", command=self._apply).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT)
        
        self.name_entry.focus()
    
    def _apply(self):
        """Apply changes."""
        name = self.name_entry.get().strip()
        role = self.role_combo.get()
        status = self.status_combo.get()
        
        if not name:
            messagebox.showerror("Error", "Please enter a full name")
            return
        
        # Convert role and status
        if role == "Admin":
            user_role = UserRole.ADMIN
        elif role == "Manager":
            user_role = UserRole.MANAGER
        else:
            user_role = UserRole.CASHIER
        
        if status == "Active":
            user_status = UserStatus.ACTIVE
        elif status == "Inactive":
            user_status = UserStatus.INACTIVE
        else:
            user_status = UserStatus.SUSPENDED
        
        # Update user
        self.user.name = name
        self.user.role = user_role
        self.user.status = user_status
        
        if user_manager.update_user(self.user):
            messagebox.showinfo("Success", f"User '{self.user.username}' updated successfully")
            self.result = True
            self.root.destroy()
        else:
            messagebox.showerror("Error", "Failed to update user")
    
    def _cancel(self):
        """Cancel."""
        self.result = False
        self.root.destroy()

def test_simple_edit():
    """Test simple edit dialog."""
    # Login
    if not user_manager.login("admin", "admin123"):
        print("❌ Login failed")
        return
    
    # Get user
    users = user_manager.get_all_users()
    test_user = None
    for user in users:
        if user.username != "admin":
            test_user = user
            break
    
    if not test_user:
        print("❌ No test user found")
        return
    
    # Create dialog
    root = tk.Tk()
    root.withdraw()
    
    dialog = SimpleEditUserDialog(root, test_user)
    print("🖥️ Opening Simple Edit Dialog...")
    print("   This version should definitely show Apply and Cancel buttons!")
    
    result = dialog.show()
    
    if result:
        print("✅ User was updated")
    else:
        print("ℹ️ Dialog was cancelled")
    
    root.destroy()

if __name__ == "__main__":
    test_simple_edit()

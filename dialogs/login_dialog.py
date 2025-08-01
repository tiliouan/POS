"""
Login Dialog
============

This module provides a login interface for user authentication.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

from database.user_manager import user_manager, User
from models.user import UserRole, UserStatus
from config.language_settings import get_text, language_manager

class LoginDialog:
    """Login dialog for user authentication."""
    
    def __init__(self, parent=None, on_login_success: Callable = None):
        """Initialize the login dialog."""
        self.parent = parent
        self.on_login_success = on_login_success
        self.user: Optional[User] = None
        self.root = None
        
    def show(self) -> Optional[User]:
        """Show the login dialog and return the authenticated user."""
        self.root = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.root.title(get_text("login_title"))
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Center the window
        self.root.transient(self.parent)
        self.root.grab_set()
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        self._create_widgets()
        self._setup_bindings()
        
        # Focus on username field
        self.username_entry.focus()
        
        # Wait for dialog to close
        self.root.wait_window()
        
        return self.user
    
    def _create_widgets(self):
        """Create the login interface widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text=get_text("pos_login"),
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Login form frame
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Username
        ttk.Label(form_frame, text=get_text("username")).pack(anchor=tk.W, pady=(0, 5))
        username_frame = ttk.Frame(form_frame)
        username_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.username_entry = ttk.Entry(username_frame, font=("Arial", 12))
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Keyboard button for username
        from utils.virtual_keyboard import KeyboardButton
        username_keyboard = KeyboardButton(username_frame, self.username_entry)
        username_keyboard.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Password
        ttk.Label(form_frame, text=get_text("password")).pack(anchor=tk.W, pady=(0, 5))
        password_frame = ttk.Frame(form_frame)
        password_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.password_entry = ttk.Entry(password_frame, show="*", font=("Arial", 12))
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Keyboard button for password
        password_keyboard = KeyboardButton(password_frame, self.password_entry)
        password_keyboard.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Buttons frame
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.pack(fill=tk.X)
        
        # Login button
        self.login_btn = ttk.Button(
            buttons_frame,
            text=get_text("login"),
            command=self._login,
            style="Accent.TButton"
        )
        self.login_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_btn = ttk.Button(
            buttons_frame,
            text=get_text("cancel"),
            command=self._cancel
        )
        cancel_btn.pack(side=tk.LEFT)
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="",
            foreground="red",
            font=("Arial", 10)
        )
        self.status_label.pack(pady=(10, 0))
        
        # Default credentials info (for demo)
        info_frame = ttk.LabelFrame(main_frame, text=get_text("default_accounts"), padding="10")
        info_frame.pack(fill=tk.X, pady=(20, 0))
        
        info_text = """Admin Account:
Username: admin
Password: admin123

You can create up to 2 additional accounts from the admin panel."""
        
        ttk.Label(info_frame, text=info_text, font=("Arial", 9)).pack()
    
    def _setup_bindings(self):
        """Setup keyboard bindings."""
        self.root.bind('<Return>', lambda e: self._login())
        self.root.bind('<Escape>', lambda e: self._cancel())
        
        # Prevent closing with X button
        self.root.protocol("WM_DELETE_WINDOW", self._cancel)
    
    def _login(self):
        """Handle login attempt."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.status_label.config(text=get_text("enter_credentials"))
            return
        
        # Disable login button during authentication
        self.login_btn.config(state="disabled")
        self.status_label.config(text=get_text("authenticating"))
        self.root.update()
        
        try:
            # Attempt login
            if user_manager.login(username, password):
                self.user = user_manager.get_current_user()
                
                # Call success callback if provided
                if self.on_login_success:
                    self.on_login_success(self.user)
                
                self.root.destroy()
            else:
                self.status_label.config(text=get_text("invalid_credentials"))
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus()
        
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
        
        finally:
            # Check if widget still exists before trying to configure it
            if self.login_btn.winfo_exists():
                self.login_btn.config(state="normal")
    
    def _cancel(self):
        """Handle cancel/close."""
        self.user = None
        self.root.destroy()

class UserManagementDialog:
    """Dialog for managing user accounts (admin only)."""
    
    def __init__(self, parent):
        """Initialize the user management dialog."""
        self.parent = parent
        self.root = None
        
    def show(self):
        """Show the user management dialog."""
        if not user_manager.is_admin():
            messagebox.showerror("Access Denied", "Only administrators can manage users")
            return
        
        self.root = tk.Toplevel(self.parent)
        self.root.title(get_text("user_management"))
        self.root.geometry("800x600")
        
        self._create_widgets()
        self._load_users()
        
        # Center and show
        self.root.transient(self.parent)
        self.root.grab_set()
    
    def _create_widgets(self):
        """Create the user management interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text=get_text("user_management"),
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            buttons_frame,
            text=get_text("add_user"),
            command=self._add_user
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            buttons_frame,
            text=get_text("edit_user"),
            command=self._edit_user
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            buttons_frame,
            text=get_text("change_password"),
            command=self._change_password
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            buttons_frame,
            text=get_text("remove_user"),
            command=self._remove_user
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            buttons_frame,
            text=get_text("refresh"),
            command=self._load_users
        ).pack(side=tk.RIGHT)
        
        # Users tree
        self.users_tree = ttk.Treeview(
            main_frame,
            columns=("name", "role", "status", "last_login"),
            show="tree headings"
        )
        
        self.users_tree.heading("#0", text="Username")
        self.users_tree.heading("name", text="Name")
        self.users_tree.heading("role", text="Role")
        self.users_tree.heading("status", text="Status")
        self.users_tree.heading("last_login", text="Last Login")
        
        self.users_tree.column("#0", width=120)
        self.users_tree.column("name", width=150)
        self.users_tree.column("role", width=100)
        self.users_tree.column("status", width=100)
        self.users_tree.column("last_login", width=150)
        
        # Scrollbar for tree
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _load_users(self):
        """Load and display users."""
        # Clear existing items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        # Load users from database
        users = user_manager.get_all_users()
        
        for user in users:
            last_login = user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Never"
            
            self.users_tree.insert(
                "",
                tk.END,
                iid=user.id,
                text=user.username,
                values=(user.name, user.role.value.title(), user.status.value.title(), last_login)
            )
    
    def _add_user(self):
        """Show dialog to add new user."""
        # Check if we can add more users (limit to 10 total)
        users = user_manager.get_all_users()
        if len(users) >= 10:
            messagebox.showwarning(
                "User Limit",
                "Maximum of 10 user accounts allowed"
            )
            return
        
        dialog = AddUserDialog(self.root)
        if dialog.show():
            self._load_users()
    
    def _edit_user(self):
        """Edit selected user."""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a user to edit")
            return
        
        user_id = int(selection[0])
        
        # Get the user data
        users = user_manager.get_all_users()
        user_to_edit = None
        for user in users:
            if user.id == user_id:
                user_to_edit = user
                break
        
        if not user_to_edit:
            messagebox.showerror("Error", "User not found")
            return
        
        dialog = EditUserDialog(self.root, user_to_edit)
        if dialog.show():
            self._load_users()
    
    def _change_password(self):
        """Change password for selected user."""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a user to change password")
            return
        
        user_id = int(selection[0])
        dialog = ChangePasswordDialog(self.root, user_id)
        dialog.show()
    
    def _remove_user(self):
        """Remove selected user."""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a user to remove")
            return
        
        user_id = int(selection[0])
        
        # Get the user data to check if it's the current user or default admin
        users = user_manager.get_all_users()
        user_to_remove = None
        for user in users:
            if user.id == user_id:
                user_to_remove = user
                break
        
        if not user_to_remove:
            messagebox.showerror("Error", "User not found")
            return
        
        # Prevent removing the current logged-in user
        current_user = user_manager.get_current_user()
        if current_user and current_user.id == user_id:
            messagebox.showerror("Error", "Cannot remove the currently logged-in user")
            return
        
        # Prevent removing the default admin if it's the only admin
        admin_users = [u for u in users if u.role == UserRole.ADMIN]
        if user_to_remove.role == UserRole.ADMIN and len(admin_users) <= 1:
            messagebox.showerror("Error", "Cannot remove the last admin user")
            return
        
        # Confirm removal
        confirm = messagebox.askyesno(
            "Confirm Removal",
            f"Are you sure you want to remove user '{user_to_remove.username}' ({user_to_remove.name})?\n\nThis action cannot be undone."
        )
        
        if not confirm:
            return
        
        # Remove the user
        if user_manager.remove_user(user_id):
            messagebox.showinfo("Success", f"User '{user_to_remove.username}' removed successfully")
            self._load_users()
        else:
            messagebox.showerror("Error", "Failed to remove user")

class AddUserDialog:
    """Dialog for adding new users."""
    
    def __init__(self, parent):
        """Initialize the add user dialog."""
        self.parent = parent
        self.root = None
        self.result = False
        
    def show(self) -> bool:
        """Show the dialog and return True if user was created."""
        self.root = tk.Toplevel(self.parent)
        self.root.title(get_text("add_user"))
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        
        self._create_widgets()
        
        # Center and show
        self.root.transient(self.parent)
        self.root.grab_set()
        self.root.wait_window()
        
        return self.result
    
    def _create_widgets(self):
        """Create the add user interface."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Form fields
        ttk.Label(main_frame, text="Username:").pack(anchor=tk.W, pady=(0, 5))
        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill=tk.X, pady=(0, 10))
        self.username_entry = ttk.Entry(username_frame)
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        from utils.virtual_keyboard import KeyboardButton
        KeyboardButton(username_frame, self.username_entry).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Label(main_frame, text="Full Name:").pack(anchor=tk.W, pady=(0, 5))
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=(0, 10))
        self.name_entry = ttk.Entry(name_frame)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        KeyboardButton(name_frame, self.name_entry).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Label(main_frame, text="Password:").pack(anchor=tk.W, pady=(0, 5))
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=(0, 10))
        self.password_entry = ttk.Entry(password_frame, show="*")
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        KeyboardButton(password_frame, self.password_entry).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Label(main_frame, text="Confirm Password:").pack(anchor=tk.W, pady=(0, 5))
        confirm_frame = ttk.Frame(main_frame)
        confirm_frame.pack(fill=tk.X, pady=(0, 10))
        self.confirm_password_entry = ttk.Entry(confirm_frame, show="*")
        self.confirm_password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        KeyboardButton(confirm_frame, self.confirm_password_entry).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Label(main_frame, text="Role:").pack(anchor=tk.W, pady=(0, 5))
        self.role_combo = ttk.Combobox(main_frame, values=["Cashier", "Manager", "Admin"], state="readonly")
        self.role_combo.set("Cashier")
        self.role_combo.pack(fill=tk.X, pady=(0, 20))
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(
            buttons_frame,
            text="Create User",
            command=self._create_user
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            buttons_frame,
            text="Cancel",
            command=self._cancel
        ).pack(side=tk.LEFT)
        
        # Focus on username
        self.username_entry.focus()
    
    def _create_user(self):
        """Create the new user."""
        username = self.username_entry.get().strip()
        name = self.name_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        role = self.role_combo.get()
        
        # Validation
        if not all([username, name, password]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        
        # Create user
        from models.user import UserRole, UserStatus
        
        if role == "Admin":
            user_role = UserRole.ADMIN
        elif role == "Manager":
            user_role = UserRole.MANAGER
        else:
            user_role = UserRole.CASHIER
        
        new_user = User(
            username=username,
            password_hash=user_manager._hash_password(password),
            name=name,
            role=user_role,
            status=UserStatus.ACTIVE
        )
        
        if user_manager.create_user(new_user, user_manager.current_user.id):
            messagebox.showinfo("Success", f"User '{username}' created successfully")
            self.result = True
            self.root.destroy()
        else:
            messagebox.showerror("Error", "Failed to create user. Username may already exist.")
    
    def _cancel(self):
        """Cancel user creation."""
        self.result = False
        self.root.destroy()

class EditUserDialog:
    """Dialog for editing existing users."""
    
    def __init__(self, parent, user: User):
        """Initialize the edit user dialog."""
        self.parent = parent
        self.user = user
        self.root = None
        self.result = False
        
    def show(self) -> bool:
        """Show the dialog and return True if user was updated."""
        self.root = tk.Toplevel(self.parent)
        self.root.title("Edit User")
        self.root.geometry("450x500")
        self.root.resizable(True, True)
        
        self._create_widgets()
        
        # Center and show
        self.root.transient(self.parent)
        self.root.grab_set()
        self.root.wait_window()
        
        return self.result
    
    def _create_widgets(self):
        """Create the edit user interface."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text=f"Edit User: {self.user.username}",
            font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Form fields
        ttk.Label(main_frame, text="Username:").pack(anchor=tk.W, pady=(0, 5))
        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill=tk.X, pady=(0, 10))
        self.username_entry = ttk.Entry(username_frame)
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.username_entry.insert(0, self.user.username)
        self.username_entry.config(state="disabled")  # Username should not be editable
        from utils.virtual_keyboard import KeyboardButton
        KeyboardButton(username_frame, self.username_entry).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Label(main_frame, text="Full Name:").pack(anchor=tk.W, pady=(0, 5))
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=(0, 10))
        self.name_entry = ttk.Entry(name_frame)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.name_entry.insert(0, self.user.name)
        KeyboardButton(name_frame, self.name_entry).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Label(main_frame, text="Role:").pack(anchor=tk.W, pady=(0, 5))
        self.role_combo = ttk.Combobox(main_frame, values=["Cashier", "Manager", "Admin"], state="readonly")
        
        # Set current role
        if self.user.role == UserRole.ADMIN:
            self.role_combo.set("Admin")
        elif self.user.role == UserRole.MANAGER:
            self.role_combo.set("Manager")
        else:
            self.role_combo.set("Cashier")
        
        self.role_combo.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Status:").pack(anchor=tk.W, pady=(0, 5))
        self.status_combo = ttk.Combobox(main_frame, values=["Active", "Inactive", "Suspended"], state="readonly")
        
        # Set current status
        if self.user.status == UserStatus.ACTIVE:
            self.status_combo.set("Active")
        elif self.user.status == UserStatus.INACTIVE:
            self.status_combo.set("Inactive")
        else:
            self.status_combo.set("Suspended")
        
        self.status_combo.pack(fill=tk.X, pady=(0, 20))
        
        # Note about password
        note_label = ttk.Label(
            main_frame,
            text="Note: Use 'Change Password' to update user password",
            font=("Arial", 9),
            foreground="#666"
        )
        note_label.pack(pady=(0, 10))
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(
            buttons_frame,
            text="Apply",
            command=self._update_user
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            buttons_frame,
            text="Cancel",
            command=self._cancel
        ).pack(side=tk.LEFT)
        
        # Focus on name field
        self.name_entry.focus()
    
    def _update_user(self):
        """Update the user."""
        name = self.name_entry.get().strip()
        role = self.role_combo.get()
        status = self.status_combo.get()
        
        # Validation
        if not name:
            messagebox.showerror("Error", "Please enter a full name")
            return
        
        # Convert role and status
        from models.user import UserRole, UserStatus
        
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
        
        # Update user object
        self.user.name = name
        self.user.role = user_role
        self.user.status = user_status
        
        # Save changes
        if user_manager.update_user(self.user):
            messagebox.showinfo("Success", f"User '{self.user.username}' updated successfully")
            self.result = True
            self.root.destroy()
        else:
            messagebox.showerror("Error", "Failed to update user")
    
    def _cancel(self):
        """Cancel user editing."""
        self.result = False
        self.root.destroy()

class ChangePasswordDialog:
    """Dialog for changing user passwords."""
    
    def __init__(self, parent, user_id: int):
        """Initialize the change password dialog."""
        self.parent = parent
        self.user_id = user_id
        self.root = None
        
    def show(self):
        """Show the change password dialog."""
        self.root = tk.Toplevel(self.parent)
        self.root.title("Change Password")
        self.root.geometry("350x250")
        self.root.resizable(False, False)
        
        self._create_widgets()
        
        # Center and show
        self.root.transient(self.parent)
        self.root.grab_set()
    
    def _create_widgets(self):
        """Create the change password interface."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="New Password:").pack(anchor=tk.W, pady=(0, 5))
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=(0, 10))
        self.password_entry = ttk.Entry(password_frame, show="*")
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        from utils.virtual_keyboard import KeyboardButton
        KeyboardButton(password_frame, self.password_entry).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Label(main_frame, text="Confirm Password:").pack(anchor=tk.W, pady=(0, 5))
        confirm_frame = ttk.Frame(main_frame)
        confirm_frame.pack(fill=tk.X, pady=(0, 20))
        self.confirm_password_entry = ttk.Entry(confirm_frame, show="*")
        self.confirm_password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        KeyboardButton(confirm_frame, self.confirm_password_entry).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(
            buttons_frame,
            text="Change Password",
            command=self._change_password
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            buttons_frame,
            text="Cancel",
            command=self.root.destroy
        ).pack(side=tk.LEFT)
        
        self.password_entry.focus()
    
    def _change_password(self):
        """Change the user password."""
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        if not password:
            messagebox.showerror("Error", "Please enter a password")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        
        if user_manager.change_password(self.user_id, password):
            messagebox.showinfo("Success", "Password changed successfully")
            self.root.destroy()
        else:
            messagebox.showerror("Error", "Failed to change password")

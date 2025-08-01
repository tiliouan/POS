#!/usr/bin/env python3
"""
Test logout functionality specifically
"""

import tkinter as tk
from tkinter import messagebox
from utils.session_manager import SessionManager

def test_logout_flow():
    """Test the logout flow."""
    print("=== Testing Logout Flow ===")
    
    # Create a simple window to test logout
    root = tk.Tk()
    root.title("Logout Test")
    root.geometry("300x200")
    
    sm = SessionManager()
    
    def test_logout():
        """Test logout function."""
        print("Logout button clicked!")
        if messagebox.askyesno("Déconnexion", "Êtes-vous sûr de vouloir vous déconnecter?"):
            print("User confirmed logout")
            # End session (this will require cash drawer opening on next login)
            if sm.current_session or sm.get_current_session():
                sm.end_session("Test logout from button")
                print("Session ended successfully")
            else:
                print("No active session found")
            
            # Check if cash drawer will be needed
            needs_drawer = sm.needs_cash_drawer_opening()
            print(f"After logout - will need cash drawer on next start: {needs_drawer}")
            
            root.destroy()
        else:
            print("User cancelled logout")
    
    # Check initial state
    print(f"Initial state - needs cash drawer: {sm.needs_cash_drawer_opening()}")
    
    # Start a session if needed
    if sm.needs_cash_drawer_opening():
        print("Starting test session...")
        sm.start_session(1000.0, "Test session for logout")
    
    print(f"After session start - needs cash drawer: {sm.needs_cash_drawer_opening()}")
    
    # Create logout button
    logout_btn = tk.Button(root, text="DÉCONNEXION", 
                          command=test_logout,
                          bg="#d9534f", fg="white",
                          font=("Arial", 12, "bold"),
                          padx=20, pady=10)
    logout_btn.pack(pady=50)
    
    info_label = tk.Label(root, text="Click the logout button to test", 
                         font=("Arial", 10))
    info_label.pack()
    
    root.mainloop()
    print("=== Test completed ===")

if __name__ == "__main__":
    test_logout_flow()

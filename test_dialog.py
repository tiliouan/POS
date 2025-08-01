#!/usr/bin/env python3
"""
Test cash drawer dialog in isolation
"""

import tkinter as tk
from utils.session_manager import SessionManager

class TestDialog:
    """Simple test dialog."""
    
    def __init__(self, parent, session_manager):
        self.session_manager = session_manager
        self.result = None
        
        # Create dialog window
        self.window = tk.Toplevel(parent)
        self.window.title("Test Dialog")
        self.window.geometry("300x200")
        self.window.grab_set()
        
        # Simple content
        frame = tk.Frame(self.window, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        
        tk.Label(frame, text="Test Cash Drawer Dialog").pack(pady=10)
        
        tk.Button(frame, text="OK", command=self.ok_clicked).pack(pady=5)
        tk.Button(frame, text="Cancel", command=self.cancel_clicked).pack(pady=5)
        
    def ok_clicked(self):
        """Handle OK click."""
        self.result = True
        self.window.destroy()
        
    def cancel_clicked(self):
        """Handle Cancel click."""
        self.result = False
        self.window.destroy()

def test_dialog():
    """Test the dialog."""
    root = tk.Tk()
    root.title("Main Window")
    root.geometry("400x300")
    
    session_manager = SessionManager()
    
    # Show main window
    root.update()
    
    def show_dialog():
        """Show the test dialog."""
        dialog = TestDialog(root, session_manager)
        root.wait_window(dialog.window)
        print(f"Dialog result: {dialog.result}")
        
    # Button to show dialog
    tk.Button(root, text="Show Dialog", command=show_dialog).pack(pady=50)
    
    # Auto-show dialog after a delay
    root.after(1000, show_dialog)
    
    root.mainloop()

if __name__ == "__main__":
    test_dialog()

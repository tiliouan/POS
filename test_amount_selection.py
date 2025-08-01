#!/usr/bin/env python3
"""
Test enhanced amount selection in cash management
"""

import tkinter as tk
from tkinter import ttk
from utils.session_manager import SessionManager

class TestAmountSelection:
    """Test the amount selection dialog."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Amount Selection")
        self.root.geometry("400x300")
        
        # Initialize session manager
        self.session_manager = SessionManager()
        
        # Start a test session if needed
        if self.session_manager.needs_cash_drawer_opening():
            self.session_manager.start_session(1000.0, "Test session")
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create test widgets."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        title_label = ttk.Label(main_frame, text="Test Cash Management", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        current_cash = self.session_manager.get_today_cash_amount()
        cash_label = ttk.Label(main_frame, 
                              text=f"Current Cash: {current_cash:.2f} د.م",
                              font=("Arial", 14))
        cash_label.pack(pady=(0, 20))
        
        test_btn = tk.Button(main_frame, text="OUVRIR GESTION DES ESPÈCES",
                            command=self.open_cash_management,
                            bg="#20B2AA", fg="white",
                            font=("Arial", 12, "bold"),
                            padx=20, pady=10)
        test_btn.pack(pady=20)
        
        instruction_label = ttk.Label(main_frame, 
                                     text="Click the button above to test\nthe enhanced amount selection",
                                     font=("Arial", 10),
                                     justify="center")
        instruction_label.pack(pady=(20, 0))
        
    def open_cash_management(self):
        """Open the cash management dialog."""
        try:
            from pos_system import CashManagementDialog
            dialog = CashManagementDialog(self.root, self.session_manager)
            self.root.wait_window(dialog.window)
            
            # Update display after dialog closes
            current_cash = self.session_manager.get_today_cash_amount()
            print(f"Updated cash amount: {current_cash:.2f} د.م")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Run the test application."""
        self.root.mainloop()

if __name__ == "__main__":
    test_app = TestAmountSelection()
    test_app.run()

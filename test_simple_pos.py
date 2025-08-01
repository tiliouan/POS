#!/usr/bin/env python3
"""
Simplified POS test without session management
"""

import tkinter as tk
from tkinter import ttk
from models.product import Product
from models.sale import Sale
from models.payment import Payment, PaymentMethod
from database.db_manager import DatabaseManager

class SimplePOSTest:
    """Simplified POS for testing."""
    
    def __init__(self):
        """Initialize the simplified POS."""
        print("Creating main window...")
        self.root = tk.Tk()
        self.root.title("POS Test")
        self.root.geometry("800x600")
        
        print("Initializing database...")
        self.db_manager = DatabaseManager()
        
        print("Creating widgets...")
        self.create_widgets()
        
        print("Setup complete, ready to show window...")
        
    def create_widgets(self):
        """Create basic widgets."""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        title_label = ttk.Label(main_frame, text="POS System Test", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        test_button = ttk.Button(main_frame, text="Test Button",
                                command=self.test_action)
        test_button.pack(pady=10)
        
        close_button = ttk.Button(main_frame, text="Fermer",
                                 command=self.root.quit)
        close_button.pack(pady=10)
        
    def test_action(self):
        """Test action."""
        print("Test button clicked!")
        
    def run(self):
        """Run the application."""
        print("Starting mainloop...")
        self.root.mainloop()
        print("Application closed.")

def main():
    """Main function."""
    try:
        print("Starting simplified POS test...")
        app = SimplePOSTest()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

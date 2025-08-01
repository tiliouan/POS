"""
Main POS Application Entry Point
===============================

This is the main entry point for the POS application with user authentication.
"""

import tkinter as tk
from pos_system import POSApplication

def main():
    """Main application entry point."""
    # Create and run the POS application
    try:
        app = POSApplication()
        app.root.mainloop()
    except Exception as e:
        print(f"Error starting POS application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

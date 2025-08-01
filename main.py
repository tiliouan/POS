"""
Point of Sale System
===================

A comprehensive Point of Sale system with GUI interface supporting:
- Product management and scanning
- Shopping cart functionality
- Multiple payment methods
- Receipt generation
- Inventory management

Requirements:
- Python 3.8+
- tkinter (usually included with Python)
- sqlite3 (included with Python)

Usage:
    python main.py

Author: GitHub Copilot
License: MIT
"""

import sys
import os
from pos_system import POSApplication

def main():
    """Main entry point for the POS system."""
    try:
        # Create and run the POS application
        app = POSApplication()
        app.run()
    except Exception as e:
        print(f"Erreur lors du démarrage de l'application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

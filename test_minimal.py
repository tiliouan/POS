#!/usr/bin/env python3
"""
Minimal POS test - just create and show the window
"""

import sys
import os

def main():
    """Test POS creation without full initialization."""
    try:
        print("Importing POS system...")
        from pos_system import POSApplication
        
        print("Creating POS application...")
        app = POSApplication()
        
        print("About to start mainloop...")
        app.root.mainloop()
        
        print("Mainloop ended.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

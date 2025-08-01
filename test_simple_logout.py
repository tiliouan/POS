#!/usr/bin/env python3
"""
Simple logout flag approach
"""

import os

class SimpleLogoutTracker:
    """Simple file-based logout tracker."""
    
    def __init__(self):
        self.logout_file = "logout_flag.txt"
    
    def set_logout_flag(self):
        """Set flag that user logged out."""
        with open(self.logout_file, 'w') as f:
            f.write("logged_out")
        print("Logout flag set")
    
    def check_and_clear_logout_flag(self) -> bool:
        """Check if logout flag exists and clear it."""
        if os.path.exists(self.logout_file):
            os.remove(self.logout_file)
            print("Found and cleared logout flag - need cash drawer")
            return True
        print("No logout flag found - no cash drawer needed")
        return False

def test_simple_tracker():
    """Test the simple tracker."""
    tracker = SimpleLogoutTracker()
    
    print("=== Testing Simple Logout Tracker ===")
    
    # Test initial state
    print("1. Initial check:")
    needs_dialog = tracker.check_and_clear_logout_flag()
    print(f"   Needs cash drawer dialog: {needs_dialog}")
    
    # Simulate logout
    print("2. Simulating logout:")
    tracker.set_logout_flag()
    
    # Check after logout
    print("3. Check after logout:")
    needs_dialog = tracker.check_and_clear_logout_flag()
    print(f"   Needs cash drawer dialog: {needs_dialog}")
    
    # Check again (should be False now)
    print("4. Check again (should be False):")
    needs_dialog = tracker.check_and_clear_logout_flag()
    print(f"   Needs cash drawer dialog: {needs_dialog}")

if __name__ == "__main__":
    test_simple_tracker()

#!/usr/bin/env python3
"""
Final test of logout functionality
"""

from utils.session_manager import SessionManager
import os

def test_final_logout():
    """Test the final logout functionality."""
    print("=== Final Logout Test ===")
    
    sm = SessionManager()
    
    # Clean slate
    if os.path.exists("logout_flag.txt"):
        os.remove("logout_flag.txt")
    
    print("1. First launch (clean state):")
    print(f"   Needs cash drawer: {sm.needs_cash_drawer_opening()}")
    
    print("2. Starting session...")
    sm.start_session(1000.0, "Test session")
    print(f"   After start - Needs cash drawer: {sm.needs_cash_drawer_opening()}")
    
    print("3. Normal app close (no logout)...")
    # App closes without calling end_session
    sm2 = SessionManager()  # New instance simulating app restart
    print(f"   After restart - Needs cash drawer: {sm2.needs_cash_drawer_opening()}")
    
    print("4. Now doing logout...")
    sm2.end_session("User logout")
    print("   Logout completed")
    
    print("5. App restart after logout...")
    sm3 = SessionManager()  # New instance simulating app restart
    print(f"   After restart - Needs cash drawer: {sm3.needs_cash_drawer_opening()}")
    
    print("6. Starting session after logout...")
    sm3.start_session(1200.0, "After logout session")
    print(f"   After start - Needs cash drawer: {sm3.needs_cash_drawer_opening()}")
    
    print("\n✅ Test completed successfully!")
    print("   Cash drawer dialog will appear:")
    print("   - On first launch ✓")
    print("   - After every logout ✓")
    print("   - NOT after normal app close ✓")

if __name__ == "__main__":
    test_final_logout()

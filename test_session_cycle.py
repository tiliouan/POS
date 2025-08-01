#!/usr/bin/env python3
"""
Test script to verify logout and login cycle
"""

from utils.session_manager import SessionManager
from datetime import datetime

def test_session_cycle():
    """Test the complete session cycle."""
    print("=== Testing Session Management Cycle ===")
    
    sm = SessionManager()
    
    # Test 1: Check initial state
    print(f"1. Initial state - Needs cash drawer opening: {sm.needs_cash_drawer_opening()}")
    
    # Test 2: Start session
    if sm.needs_cash_drawer_opening():
        print("2. Starting new session...")
        session_info = sm.start_session(1000.0, "Test session start")
        print(f"   Session started: {session_info['start_time']}")
    
    # Test 3: Check after session start
    print(f"3. After session start - Needs cash drawer opening: {sm.needs_cash_drawer_opening()}")
    
    # Test 4: Simulate logout
    print("4. Simulating logout...")
    sm.end_session("Test logout")
    print("   Session ended")
    
    # Test 5: Check after logout
    print(f"5. After logout - Needs cash drawer opening: {sm.needs_cash_drawer_opening()}")
    
    # Test 6: Start session again (simulating next login)
    if sm.needs_cash_drawer_opening():
        print("6. Starting session after logout...")
        session_info = sm.start_session(1200.0, "Session after logout")
        print(f"   New session started: {session_info['start_time']}")
    
    # Test 7: Final check
    print(f"7. Final state - Needs cash drawer opening: {sm.needs_cash_drawer_opening()}")
    
    print("\n=== Test completed successfully! ===")

if __name__ == "__main__":
    test_session_cycle()

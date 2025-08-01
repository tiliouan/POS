#!/usr/bin/env python3
"""
Test script for session management functionality
"""

from utils.session_manager import SessionManager
from datetime import datetime

def test_session_manager():
    """Test the session manager functionality."""
    print("=== Test Session Manager ===")
    
    # Create session manager
    sm = SessionManager()
    
    # Test if cash drawer opening is needed
    print(f"Needs cash drawer opening: {sm.needs_cash_drawer_opening()}")
    
    # Start a new session
    session_info = sm.start_session(500.0, "Test session")
    print(f"Session started: {session_info}")
    
    # Check if it's needed again (should be False now)
    print(f"Needs cash drawer opening after start: {sm.needs_cash_drawer_opening()}")
    
    # End session
    sm.end_session()
    print("Session ended")
    
    # Check if it's needed again (should be True now)
    print(f"Needs cash drawer opening after end: {sm.needs_cash_drawer_opening()}")

if __name__ == "__main__":
    test_session_manager()

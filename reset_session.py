#!/usr/bin/env python3
"""
Reset session to test logout functionality
"""

from utils.session_manager import SessionManager

def reset_session():
    """Reset session to allow testing logout."""
    sm = SessionManager()
    
    # Start a fresh session
    session_info = sm.start_session(500.0, "Fresh session for testing")
    print(f"Session reset and started: {session_info}")
    print("Now you can test the logout functionality!")

if __name__ == "__main__":
    reset_session()

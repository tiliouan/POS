#!/usr/bin/env python3
"""
Comprehensive test of cash management features
"""

from utils.session_manager import SessionManager
import json

def test_complete_cash_management():
    """Test all cash management features."""
    print("=== Complete Cash Management Test ===")
    
    sm = SessionManager()
    
    # Start session
    print("1. Starting session...")
    sm.start_session(1000.0, "Opening for test")
    print(f"   Initial cash: {sm.get_today_cash_amount():.2f} د.م")
    
    # Add some transactions
    print("\n2. Adding transactions...")
    
    transactions = [
        (1250.0, "Ajout", "Customer payment #1", 250.0),
        (1400.0, "Ajout", "Customer payment #2", 150.0),
        (1200.0, "Retrait", "Bank deposit", 200.0),
        (1300.0, "Ajout", "Customer payment #3", 100.0),
        (1250.0, "Retrait", "Change fund", 50.0)
    ]
    
    for new_amount, op_type, reason, trans_amount in transactions:
        sm.update_cash_amount(new_amount, op_type, reason, trans_amount)
        print(f"   {op_type}: {trans_amount:.2f} د.م - {reason}")
        print(f"   New balance: {new_amount:.2f} د.م")
    
    print(f"\n3. Final cash amount: {sm.get_today_cash_amount():.2f} د.م")
    
    # Show session data
    print("\n4. Session data:")
    session_data = sm.load_session_data()
    today = sm.get_today_date()
    
    if today in session_data:
        session = session_data[today]
        print(f"   Opening amount: {session.get('cash_drawer_amount', 0):.2f} د.م")
        print(f"   Total transactions: {len(session.get('cash_transactions', []))}")
        
        print("\n   Transaction Summary:")
        for trans in session.get('cash_transactions', []):
            print(f"   - {trans['type']}: {trans['amount']:.2f} د.م ({trans['reason']})")
    
    print("\n✅ Complete cash management test finished!")
    print("You can now test the 'GÉRER ESPÈCES' button in the application.")

if __name__ == "__main__":
    test_complete_cash_management()

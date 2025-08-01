#!/usr/bin/env python3
"""
Test cash management functionality
"""

from utils.session_manager import SessionManager

def test_cash_management():
    """Test the cash management functionality."""
    print("=== Testing Cash Management ===")
    
    sm = SessionManager()
    
    # Start a session
    print("1. Starting session with 1000 د.م")
    sm.start_session(1000.0, "Initial test session")
    
    session = sm.get_current_session()
    print(f"   Initial cash: {session['cash_drawer_amount']:.2f} د.م")
    
    # Add cash
    print("2. Adding 500 د.م (customer payment)")
    sm.update_cash_amount(1500.0, "Ajout", "Paiement client", 500.0)
    
    session = sm.get_current_session()
    print(f"   After addition: {session['cash_drawer_amount']:.2f} د.م")
    
    # Remove cash
    print("3. Removing 200 د.م (bank deposit)")
    sm.update_cash_amount(1300.0, "Retrait", "Dépôt banque", 200.0)
    
    session = sm.get_current_session()
    print(f"   After removal: {session['cash_drawer_amount']:.2f} د.م")
    
    # Show transaction history
    print("\n4. Transaction History:")
    if 'cash_transactions' in session:
        for i, trans in enumerate(session['cash_transactions'], 1):
            print(f"   {i}. {trans['type']}: {trans['amount']:.2f} د.م")
            print(f"      Nouveau solde: {trans['new_balance']:.2f} د.م")
            print(f"      Motif: {trans['reason']}")
            print(f"      Heure: {trans['timestamp']}")
            print()
    
    print("✅ Cash management test completed successfully!")

if __name__ == "__main__":
    test_cash_management()

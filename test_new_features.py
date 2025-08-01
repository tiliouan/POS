"""
Test script for new POS features
=================================

This script tests the new features added to the POS system:
1. Sidebar navigation
2. Order history screen
3. Daily profit screen
4. Enhanced cash management
"""

import tkinter as tk
from pos_system import POSApplication

def test_pos_features():
    """Test the new POS features."""
    print("🧪 Testing new POS features...")
    
    try:
        # Create the application
        app = POSApplication()
        
        print("✅ Application created successfully")
        print("✅ Sidebar with navigation buttons should be visible")
        print("✅ Default register screen should be loaded")
        
        # Test navigation methods exist
        assert hasattr(app, 'show_order_history'), "Order history method missing"
        assert hasattr(app, 'show_daily_profit'), "Daily profit method missing"
        assert hasattr(app, 'show_register_screen'), "Register screen method missing"
        assert hasattr(app, 'manage_cash'), "Cash management method missing"
        
        print("✅ All navigation methods available")
        
        # Test database methods
        sales = app.db_manager.get_all_sales()
        print(f"✅ Found {len(sales)} sales in database")
        
        print("\n🎯 New features to test manually:")
        print("1. Click 'ÉCRAN DU REGISTRE' - should show main POS interface")
        print("2. Click 'HISTORIQUE DES COMMANDES' - should show order history")
        print("3. Click 'PROFIT DU JOUR' - should show daily profit report")
        print("4. Click 'GÉRER L'ESPÈCE' - should show enhanced cash management")
        print("5. Click 'FERMER LE REGISTRE' - should logout")
        
        print("\n🚀 Starting application...")
        app.run()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pos_features()

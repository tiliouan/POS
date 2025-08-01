#!/usr/bin/env python3
"""
Test script to verify the settings dialog works correctly
"""

import tkinter as tk
import sys
import os

# Add the POS directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from dialogs.settings_dialog import SettingsDialog
    from config.language_settings import language_manager
    
    print("✓ Successfully imported required modules")
    
    # Create a test root window
    root = tk.Tk()
    root.title("Settings Dialog Test")
    root.geometry("300x200")
    
    # Create a mock POS app object with required methods
    class MockPOSApp:
        def __init__(self):
            self.root = root
            
        def open_receipt_settings(self):
            print("Receipt settings would open here")
            
        def manage_cash(self):
            print("Cash management would open here")
            
        def show_register_screen(self):
            print("Register screen would show here")
            
        def show_order_history(self):
            print("Order history would show here")
            
        def show_daily_profit(self):
            print("Daily profit would show here")
            
        def open_backup_settings(self):
            print("Backup settings would open here")
            
        def close_register(self):
            print("Register would close here")
            
        def open_language_settings(self):
            print("Language settings would open here")
    
    mock_app = MockPOSApp()
    
    # Test current language access
    current_lang = language_manager.settings.current_language
    print(f"✓ Current language: {current_lang}")
    
    # Create a button to test the settings dialog
    def test_settings():
        try:
            dialog = SettingsDialog(root, mock_app)
            dialog.show()
            print("✓ Settings dialog opened successfully")
        except Exception as e:
            print(f"❌ Error opening settings dialog: {e}")
            import traceback
            traceback.print_exc()
    
    btn = tk.Button(root, text="Test Settings Dialog", command=test_settings)
    btn.pack(pady=50)
    
    info_label = tk.Label(root, text="Click the button to test the settings dialog")
    info_label.pack()
    
    print("\n🎉 Test window created successfully!")
    print("Click the 'Test Settings Dialog' button to verify the settings dialog works.")
    
    root.mainloop()
    
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()

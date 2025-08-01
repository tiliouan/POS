#!/usr/bin/env python3
"""
Debug Print Logic
================

Test to debug the exact print logic flow in complete_sale.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.receipt_settings import ReceiptSettingsManager

def debug_print_logic():
    """Debug the print logic that runs after payment."""
    print("🔍 Debugging print logic...")
    
    try:
        # Load receipt settings
        settings_manager = ReceiptSettingsManager()
        settings = settings_manager.load_settings()
        
        if settings is None:
            print("❌ Settings is None!")
            return
            
        print(f"📋 Settings loaded:")
        print(f"   auto_print: {settings.auto_print}")
        print(f"   default_printer: {settings.default_printer}")
        print(f"   printer_name: {settings.printer_name}")
        
        # Simulate the complete_sale print logic
        print("\n🔍 Simulating complete_sale print logic:")
        
        # This is the exact logic from complete_sale method lines 562-571
        if settings.auto_print and settings.default_printer:
            print(f"   ✅ AUTO PRINT: Would auto-print to {settings.default_printer}")
        else:
            print(f"   📝 SHOW DIALOG: auto_print={settings.auto_print}, default_printer='{settings.default_printer}'")
            print(f"   📝 DIALOG SHOULD SHOW because:")
            if not settings.auto_print:
                print(f"      - auto_print is False")
            if not settings.default_printer:
                print(f"      - default_printer is empty")
            
            # This is where show_print_dialog would be called
            print(f"   📝 show_print_dialog() would be called here")
        
        print("\n✅ Print logic simulation complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_print_logic()

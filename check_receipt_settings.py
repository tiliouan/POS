#!/usr/bin/env python3
"""
Check current receipt settings
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.receipt_settings import ReceiptSettingsManager

def check_settings():
    """Check current receipt settings."""
    try:
        manager = ReceiptSettingsManager()
        settings = manager.get_settings()
        
        print('📋 Current Receipt Settings:')
        print(f'   Auto Print: {settings.auto_print}')
        print(f'   Default Printer: "{settings.default_printer}"')
        print(f'   Store Name: "{settings.store_name}"')
        print(f'   Paper Size: "{settings.paper_size}"')
        
        print('\n🔍 Print Dialog Logic:')
        if settings.auto_print and settings.default_printer:
            print('   ❌ Print dialog will NOT show (auto_print=True AND default_printer is set)')
            print('   📤 Will automatically print to:', settings.default_printer)
        else:
            print('   ✅ Print dialog WILL show')
            if not settings.auto_print:
                print('   📝 Reason: auto_print is False')
            if not settings.default_printer:
                print('   📝 Reason: no default_printer set')
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_settings()

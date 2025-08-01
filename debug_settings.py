#!/usr/bin/env python3
"""
Debug settings loading issue
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.receipt_settings import ReceiptSettingsManager

def debug_settings_loading():
    """Debug the settings loading issue."""
    print("🔍 Debugging settings loading...")
    
    try:
        # First, save some test data
        print("✅ Step 1: Save test data...")
        manager1 = ReceiptSettingsManager()
        settings1 = manager1.get_settings()
        
        test_name = "DEBUG TEST STORE"
        test_address = "Debug Street 123"
        
        settings1.store_name = test_name
        settings1.store_address_line1 = test_address
        
        manager1.settings = settings1
        manager1.save_settings()
        print(f"   Saved: '{test_name}'")
        
        # Check the actual file content
        config_file = "config/receipt_settings.json"
        if os.path.exists(config_file):
            print("✅ Step 2: Check file content...")
            with open(config_file, 'r', encoding='utf-8') as f:
                import json
                data = json.load(f)
                print(f"   File store_name: '{data.get('store_name', 'NOT_FOUND')}'")
        else:
            print("❌ Config file not found!")
            return False
        
        # Create a new manager instance
        print("✅ Step 3: Create new manager instance...")
        manager2 = ReceiptSettingsManager()
        settings2 = manager2.get_settings()
        
        print(f"   New manager store_name: '{settings2.store_name}'")
        print(f"   New manager address: '{settings2.store_address_line1}'")
        
        if settings2.store_name == test_name:
            print("✅ Settings loaded correctly by new manager!")
        else:
            print("❌ Settings NOT loaded correctly by new manager!")
            
            # Debug the load_settings method
            print("🔍 Debugging load_settings method...")
            manager3 = ReceiptSettingsManager()
            print(f"   Manager3 settings_file: '{manager3.settings_file}'")
            print(f"   File exists: {os.path.exists(manager3.settings_file)}")
            
            # Try loading manually
            if os.path.exists(manager3.settings_file):
                with open(manager3.settings_file, 'r', encoding='utf-8') as f:
                    import json
                    data = json.load(f)
                    print(f"   Manual load store_name: '{data.get('store_name', 'NOT_FOUND')}'")
                    
                    # Check if attributes are being set
                    print("   Checking attribute setting...")
                    for key, value in data.items():
                        if hasattr(manager3.settings, key):
                            print(f"     Setting {key} = {value}")
                            setattr(manager3.settings, key, value)
                        else:
                            print(f"     No attribute {key}")
                    
                    print(f"   After manual setting: '{manager3.settings.store_name}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_settings_loading()

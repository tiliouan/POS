#!/usr/bin/env python3
"""
Deep debug of ReceiptSettingsManager loading
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.receipt_settings import ReceiptSettingsManager, ReceiptSettings
import json

def deep_debug():
    """Deep debug of the loading issue."""
    print("🔍 Deep debugging ReceiptSettingsManager...")
    
    try:
        # Check file content first
        config_file = "config/receipt_settings.json"
        print(f"✅ Checking file: {config_file}")
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"   File contains store_name: '{data.get('store_name', 'NOT_FOUND')}'")
            print(f"   File keys: {list(data.keys())}")
        else:
            print("   File does not exist!")
            return False
        
        # Create manager step by step
        print("✅ Creating ReceiptSettingsManager...")
        manager = ReceiptSettingsManager()
        
        print(f"   Settings file path: '{manager.settings_file}'")
        print(f"   Initial settings store_name: '{manager.settings.store_name}'")
        
        # Check if load_settings was called in __init__
        print("✅ Checking load_settings call...")
        
        # Create fresh settings and manually load
        print("✅ Manual loading test...")
        fresh_settings = ReceiptSettings()
        print(f"   Fresh settings store_name: '{fresh_settings.store_name}'")
        
        # Apply data manually
        for key, value in data.items():
            if hasattr(fresh_settings, key):
                print(f"   Setting {key} = '{value}'")
                setattr(fresh_settings, key, value)
            else:
                print(f"   ⚠️  No attribute {key}")
        
        print(f"   After manual setting store_name: '{fresh_settings.store_name}'")
        
        # Test the actual load_settings method
        print("✅ Testing load_settings method...")
        test_manager = ReceiptSettingsManager()
        print(f"   Before load_settings: '{test_manager.settings.store_name}'")
        
        # Manually call load_settings
        test_manager.load_settings()
        print(f"   After load_settings: '{test_manager.settings.store_name}'")
        
        # Check if there's an encoding issue
        print("✅ Checking for encoding issues...")
        with open(config_file, 'r', encoding='utf-8') as f:
            raw_content = f.read()
            print(f"   Raw content length: {len(raw_content)}")
            print(f"   Raw content preview: {repr(raw_content[:100])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Deep debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    deep_debug()

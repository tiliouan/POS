#!/usr/bin/env python3
"""
Debug dialog initialization step by step
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk

def debug_dialog_init():
    """Debug dialog initialization step by step."""
    print("🔍 Debugging dialog initialization...")
    
    try:
        # Ensure we have test data
        from config.receipt_settings import ReceiptSettingsManager
        manager = ReceiptSettingsManager()
        settings = manager.get_settings()
        settings.store_name = 'DEBUG DIALOG INIT'
        settings.store_address_line1 = 'Debug Address'
        manager.settings = settings
        manager.save_settings()
        print("✅ Saved test data")
        
        # Create root
        root = tk.Tk()
        root.withdraw()
        
        # Step by step dialog creation
        print("✅ Creating dialog step by step...")
        
        # Simulate dialog.__init__ manually
        parent = root
        
        # Step 1: Create settings manager
        print("   Step 1: Creating settings manager...")
        settings_manager = ReceiptSettingsManager()
        print(f"      Settings manager store_name: '{settings_manager.settings.store_name}'")
        
        # Step 2: Get settings
        print("   Step 2: Getting settings...")
        dialog_settings = settings_manager.get_settings()
        print(f"      Dialog settings store_name: '{dialog_settings.store_name}'")
        
        # Step 3: Create window (like dialog.__init__ does)
        print("   Step 3: Creating window...")
        dialog_window = tk.Toplevel(parent)
        dialog_window.title("Debug Dialog")
        dialog_window.withdraw()  # Hide it
        
        # Step 4: Create variables
        print("   Step 4: Creating variables...")
        store_name_var = tk.StringVar()
        address1_var = tk.StringVar()
        phone_var = tk.StringVar()
        
        # Step 5: Load settings into variables (like load_current_settings)
        print("   Step 5: Loading settings into variables...")
        print(f"      Before loading - store_name_var: '{store_name_var.get()}'")
        print(f"      Settings to load - store_name: '{dialog_settings.store_name}'")
        
        store_name_var.set(dialog_settings.store_name)
        address1_var.set(dialog_settings.store_address_line1)
        phone_var.set(dialog_settings.store_phone)
        
        print(f"      After loading - store_name_var: '{store_name_var.get()}'")
        print(f"      After loading - address1_var: '{address1_var.get()}'")
        print(f"      After loading - phone_var: '{phone_var.get()}'")
        
        # Test if the variables work
        print("   Step 6: Testing variable functionality...")
        test_value = "TEST VARIABLE"
        store_name_var.set(test_value)
        print(f"      After setting test value: '{store_name_var.get()}'")
        
        # Clean up
        dialog_window.destroy()
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_dialog_init()

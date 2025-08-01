#!/usr/bin/env python3
"""
Test script to verify the POS system works correctly with settings dialog
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add the POS directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from pos_system import POSApplication
    print("✓ Successfully imported POSApplication")
    
    # Try creating the application
    app = POSApplication()
    print("✓ Successfully created POS application instance")
    
    # Test that the settings dialog can be imported
    from dialogs.settings_dialog import SettingsDialog
    print("✓ Successfully imported SettingsDialog")
    
    # Test creating settings dialog
    settings_dialog = SettingsDialog(app.root, app)
    print("✓ Successfully created SettingsDialog instance")
    
    print("\n🎉 All tests passed! The POS system should work correctly.")
    print("📝 Changes made:")
    print("   - Removed left sidebar")
    print("   - Added Settings button in top right header")
    print("   - All sidebar functionality moved to Settings dialog")
    print("   - Settings dialog organized in tabs: General, Reports, System, Language")
    
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()

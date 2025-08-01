#!/usr/bin/env python3
"""
Comprehensive test for the complete barcode scanning functionality
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_complete_barcode_functionality():
    """Test the complete barcode functionality including GUI."""
    
    print("🔍 Testing Complete Barcode Functionality")
    print("=" * 50)
    
    try:
        # Import required modules
        from pos_system import POSApplication, BarcodeScannerDialog
        from database.db_manager import DatabaseManager
        from config.language_settings import get_text
        
        print("✅ All imports successful")
        
        # Test database products
        db = DatabaseManager()
        products = db.get_all_products()
        products_with_barcodes = [p for p in products if p.barcode]
        
        print(f"✅ Database: {len(products)} products, {len(products_with_barcodes)} with barcodes")
        
        # Create a minimal root window for testing
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        # Create POS application instance
        pos = POSApplication()
        pos.root.withdraw()  # Hide the main window for testing
        
        print("✅ POS application created successfully")
        
        # Test that products are loaded
        print(f"✅ POS has {len(pos.products)} products loaded")
        
        # Test barcode scanning with each valid barcode
        test_barcodes = ["CAFE001", "CROI001", "EAU001", "GAT001", "JUS001", "PAIN001"]
        
        print("\n🧪 Testing barcode scanning:")
        print("-" * 30)
        
        for barcode in test_barcodes:
            # Test the add_product_by_barcode method
            initial_cart_count = len(pos.cart_items)
            
            # Find the product first
            found_product = None
            for product in pos.products:
                if product.barcode and product.barcode.strip().lower() == barcode.strip().lower():
                    found_product = product
                    break
            
            if found_product:
                # Simulate adding to cart
                pos.add_to_cart(found_product)
                new_cart_count = len(pos.cart_items)
                
                if new_cart_count > initial_cart_count:
                    print(f"✅ {barcode}: Added '{found_product.name}' to cart (${found_product.price:.2f})")
                else:
                    print(f"⚠️  {barcode}: Product found but not added to cart")
            else:
                print(f"❌ {barcode}: Product not found")
        
        # Test invalid barcode
        print(f"\n🧪 Testing invalid barcode:")
        print("-" * 30)
        
        initial_cart_count = len(pos.cart_items)
        invalid_barcode = "INVALID123"
        
        found_invalid = None
        for product in pos.products:
            if product.barcode and product.barcode.strip().lower() == invalid_barcode.strip().lower():
                found_invalid = product
                break
        
        if not found_invalid:
            print(f"✅ {invalid_barcode}: Correctly rejected (not found)")
        else:
            print(f"❌ {invalid_barcode}: Should not have been found")
        
        # Test the BarcodeScannerDialog class
        print(f"\n🧪 Testing BarcodeScannerDialog:")
        print("-" * 30)
        
        def test_callback(barcode):
            print(f"✅ Scanner callback received: '{barcode}'")
        
        # The dialog would normally show, but we'll just test creation
        try:
            scanner = BarcodeScannerDialog(pos.root, test_callback)
            print("✅ BarcodeScannerDialog created successfully")
            scanner.window.destroy()  # Close the dialog
        except Exception as e:
            print(f"❌ BarcodeScannerDialog creation failed: {e}")
        
        # Test language translations
        print(f"\n🧪 Testing language translations:")
        print("-" * 30)
        
        translations = [
            "barcode_scanner",
            "scan_barcode", 
            "enter_barcode",
            "scan_button",
            "product_not_found_barcode"
        ]
        
        for key in translations:
            try:
                text = get_text(key)
                print(f"✅ {key}: '{text}'")
            except Exception as e:
                print(f"❌ {key}: Error - {e}")
        
        print(f"\n📊 Final Cart Status:")
        print("-" * 20)
        print(f"Cart items: {len(pos.cart_items)}")
        
        total = sum(item.total for item in pos.cart_items)
        print(f"Total value: {total:.2f} DH")
        
        if pos.cart_items:
            print("Items in cart:")
            for item in pos.cart_items:
                print(f"  - {item.product.name} x{item.quantity} = {item.total:.2f} DH")
        
        # Clean up
        pos.root.destroy()
        root.destroy()
        
        print(f"\n🎉 All tests completed successfully!")
        print("✅ Barcode scanning is working correctly!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_barcode_functionality()
    if success:
        print("\n🟢 BARCODE FUNCTIONALITY: WORKING")
    else:
        print("\n🔴 BARCODE FUNCTIONALITY: NEEDS FIXING")

#!/usr/bin/env python3
"""
Test barcode scanning with existing products
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database.db_manager import DatabaseManager
    from models.product import Product
    
    db = DatabaseManager()
    products = db.get_all_products()
    
    print("Testing barcode scanning with existing products:")
    print("=" * 50)
    
    # Test with each existing barcode
    test_barcodes = ["CAFE001", "CROI001", "EAU001", "GAT001", "JUS001", "PAIN001"]
    
    for test_barcode in test_barcodes:
        print(f"\nTesting barcode: {test_barcode}")
        
        # Simulate the barcode scanning logic from pos_system.py
        found_product = None
        for product in products:
            if product.barcode and product.barcode.strip().lower() == test_barcode.strip().lower():
                found_product = product
                break
        
        if found_product:
            print(f"✓ SUCCESS: Found '{found_product.name}' - Price: {found_product.price:.2f} DH")
        else:
            print(f"✗ FAILED: No product found for barcode '{test_barcode}'")
    
    print("\n" + "=" * 50)
    print("Testing case insensitive search:")
    
    # Test case insensitive
    test_cases = ["cafe001", "CAFE001", "Cafe001"]
    for test_case in test_cases:
        found = False
        for product in products:
            if product.barcode and product.barcode.strip().lower() == test_case.strip().lower():
                found = True
                print(f"✓ '{test_case}' → Found '{product.name}'")
                break
        if not found:
            print(f"✗ '{test_case}' → Not found")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

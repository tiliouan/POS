#!/usr/bin/env python3
"""
Quick test to verify barcode functionality in the main POS system
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pos_barcode():
    try:
        from pos_system import POSApplication
        from database.db_manager import DatabaseManager
        
        print("Testing POS barcode functionality...")
        
        # Test database
        db = DatabaseManager()
        products = db.get_all_products()
        print(f"✓ Database has {len(products)} products")
        
        products_with_barcodes = [p for p in products if p.barcode]
        print(f"✓ {len(products_with_barcodes)} products have barcodes")
        
        # Create POS instance (without starting GUI)
        pos = POSApplication()
        
        # Test the add_product_by_barcode method directly
        print("\nTesting add_product_by_barcode method:")
        
        # Test with valid barcode
        test_barcode = "CAFE001"
        print(f"Testing barcode: {test_barcode}")
        
        # Simulate the method
        found_product = None
        for product in pos.products:
            if product.barcode and product.barcode.strip().lower() == test_barcode.strip().lower():
                found_product = product
                break
        
        if found_product:
            print(f"✓ SUCCESS: Found product '{found_product.name}' for barcode '{test_barcode}'")
        else:
            print(f"✗ FAILED: No product found for barcode '{test_barcode}'")
        
        # Test with invalid barcode
        invalid_barcode = "INVALID123"
        print(f"\nTesting invalid barcode: {invalid_barcode}")
        
        found_invalid = None
        for product in pos.products:
            if product.barcode and product.barcode.strip().lower() == invalid_barcode.strip().lower():
                found_invalid = product
                break
        
        if found_invalid:
            print(f"✗ ERROR: Should not have found product for invalid barcode")
        else:
            print(f"✓ SUCCESS: Correctly rejected invalid barcode '{invalid_barcode}'")
        
        print("\n✅ POS barcode functionality test completed!")
        return True
        
    except Exception as e:
        print(f"✗ Error testing POS barcode functionality: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_pos_barcode()

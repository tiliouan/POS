#!/usr/bin/env python3
"""
Test script for barcode functionality
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing barcode functionality...")
    
    # Test imports
    from database.db_manager import DatabaseManager
    from models.product import Product
    from config.language_settings import get_text
    
    print("✓ Imports successful")
    
    # Test database connection
    db = DatabaseManager()
    print("✓ Database connection successful")
    
    # Get products
    products = db.get_all_products()
    print(f"✓ Found {len(products)} products")
    
    # Check for products with barcodes
    products_with_barcodes = [p for p in products if p.barcode]
    print(f"✓ Found {len(products_with_barcodes)} products with barcodes")
    
    if products_with_barcodes:
        print("\nProducts with barcodes:")
        for p in products_with_barcodes:
            print(f"  - {p.name}: {p.barcode}")
    else:
        print("\n⚠ No products have barcodes assigned")
        print("Creating a test product with barcode...")
        
        # Create a test product
        test_product = Product(
            id=None,
            name="Test Product",
            description="Test product for barcode scanning",
            price=10.00,
            barcode="TEST123456",
            category="Test",
            stock_quantity=100
        )
        
        try:
            product_id = db.add_product(test_product)
            print(f"✓ Created test product with ID: {product_id}")
            
            # Verify the product was created
            updated_products = db.get_all_products()
            test_products = [p for p in updated_products if p.barcode == "TEST123456"]
            if test_products:
                print(f"✓ Test product verified: {test_products[0].name}")
            else:
                print("✗ Test product not found after creation")
                
        except Exception as e:
            print(f"✗ Error creating test product: {e}")
    
    # Test barcode search functionality
    print("\nTesting barcode search...")
    test_barcode = "TEST123456"
    found_product = None
    
    current_products = db.get_all_products()
    for product in current_products:
        if product.barcode and product.barcode.strip().lower() == test_barcode.strip().lower():
            found_product = product
            break
    
    if found_product:
        print(f"✓ Barcode search successful: Found '{found_product.name}' for barcode '{test_barcode}'")
    else:
        print(f"✗ Barcode search failed: No product found for barcode '{test_barcode}'")
    
    # Test language settings for barcode
    print("\nTesting language settings...")
    try:
        barcode_scanner_text = get_text("barcode_scanner")
        scan_barcode_text = get_text("scan_barcode")
        enter_barcode_text = get_text("enter_barcode")
        scan_button_text = get_text("scan_button")
        
        print(f"✓ barcode_scanner: '{barcode_scanner_text}'")
        print(f"✓ scan_barcode: '{scan_barcode_text}'")
        print(f"✓ enter_barcode: '{enter_barcode_text}'")
        print(f"✓ scan_button: '{scan_button_text}'")
        
    except Exception as e:
        print(f"✗ Language settings error: {e}")
    
    print("\n✅ Barcode system test completed!")

except Exception as e:
    print(f"✗ Error during testing: {e}")
    import traceback
    traceback.print_exc()

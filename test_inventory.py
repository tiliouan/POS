"""
Test script for advanced inventory management
============================================

This script tests the new inventory management features:
1. Enhanced Product model with new fields
2. Database schema updates
3. Inventory management window
"""

import tkinter as tk
from pos_system import POSApplication, InventoryManagementWindow
from database.db_manager import DatabaseManager
from models.product import Product

def test_inventory_features():
    """Test the inventory management features."""
    print("🧪 Testing Advanced Inventory Management...")
    
    try:
        # Test database manager
        db_manager = DatabaseManager()
        print("✅ Database manager initialized")
        
        # Test enhanced product model
        test_product = Product(
            id=None,
            name="Test Product",
            description="Test Description",
            price=25.99,
            cost_price=15.50,
            supplier="Test Supplier",
            category="Test Category",
            qr_code="QR123456",
            barcode="BAR123456",
            stock_quantity=100
        )
        print("✅ Enhanced Product model works")
        
        # Test saving product with new fields
        product_id = db_manager.save_product(test_product)
        print(f"✅ Product saved with ID: {product_id}")
        
        # Test loading products for inventory
        products = db_manager.get_all_products_for_inventory()
        print(f"✅ Loaded {len(products)} products from database")
        
        # Test creating main app
        app = POSApplication()
        print("✅ POS Application created")
        
        print("\n🎯 New Inventory Features to test manually:")
        print("1. Click '📦 Inventory' button in the main interface")
        print("2. Inventory window should open with:")
        print("   - Product list with all fields (ID, Name, Category, Supplier, Cost Price, Selling Price, Stock, Status)")
        print("   - Search functionality")
        print("   - Category filtering")
        print("   - Product details form on the right with:")
        print("     • Item Name")
        print("     • Category")
        print("     • Supplier")
        print("     • QR Code")
        print("     • Barcode")
        print("     • Cost Price (Without Tax)")
        print("     • Selling Price")
        print("     • Stock Quantity")
        print("     • Description")
        print("     • Active status checkbox")
        print("3. Try editing a product")
        print("4. Try adding a new product")
        print("5. Try deleting a product")
        
        print("\n🚀 Starting application...")
        app.run()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_inventory_features()

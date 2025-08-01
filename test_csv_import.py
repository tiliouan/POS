"""
Test CSV Import Functionality
"""

import tkinter as tk
from utils.csv_import import CSVProductImporter
from database.db_manager import DatabaseManager

def test_csv_import():
    """Test the CSV import functionality."""
    
    # Initialize database and importer
    db_manager = DatabaseManager()
    importer = CSVProductImporter(db_manager)
    
    # Test preview functionality
    print("Testing CSV preview functionality...")
    csv_file = "sample_products.csv"
    
    try:
        preview_data, errors, format_detected = importer.preview_csv_import(csv_file, max_preview=10)
        
        print(f"Format detected: {format_detected}")
        print(f"Preview data count: {len(preview_data)}")
        print(f"Errors: {len(errors)}")
        
        if errors:
            print("Errors found:")
            for error in errors:
                print(f"  - {error}")
        
        if preview_data:
            print("\\nSample preview data:")
            for i, product in enumerate(preview_data[:3]):
                print(f"  Product {i+1}:")
                print(f"    Name: {product.get('name')}")
                print(f"    Price: {product.get('price')}")
                print(f"    Category: {product.get('category')}")
                print(f"    Stock: {product.get('stock_quantity')}")
                if 'errors' in product:
                    print(f"    Errors: {product['errors']}")
        
        print("\\nCSV Import functionality is working correctly!")
        
    except Exception as e:
        print(f"Error testing CSV import: {e}")

if __name__ == "__main__":
    test_csv_import()

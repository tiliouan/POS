"""
Test get_sale_by_id function directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager

def test_get_sale_by_id():
    """Test the get_sale_by_id function."""
    try:
        db_manager = DatabaseManager()
        
        # Get all sales first
        all_sales = db_manager.get_all_sales()
        print(f"Total sales: {len(all_sales)}")
        
        if all_sales:
            test_sale_id = all_sales[0].id
            print(f"Testing with sale ID: {test_sale_id}")
            
            # Test get_sale_by_id
            sale = db_manager.get_sale_by_id(test_sale_id)
            
            if sale:
                print(f"✓ Retrieved sale {sale.id} successfully")
                print(f"  - Total: {sale.total:.2f} DH")
                print(f"  - Items: {len(sale.items)}")
                print(f"  - Timestamp: {sale.timestamp}")
                print(f"  - Payment: {sale.payment is not None}")
            else:
                print(f"✗ Failed to retrieve sale {test_sale_id}")
                
            # Test with non-existent ID
            non_existent = db_manager.get_sale_by_id(99999)
            if non_existent is None:
                print("✓ Correctly returned None for non-existent sale")
            else:
                print("✗ Should have returned None for non-existent sale")
        else:
            print("No sales found in database")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_get_sale_by_id()

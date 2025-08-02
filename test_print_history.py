"""
Test script for printing orders from history
"""

from database.db_manager import DatabaseManager
from utils.advanced_receipt_printer import AdvancedReceiptPrinter

def test_print_from_history():
    """Test printing an order from history."""
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Get all sales
    sales = db_manager.get_all_sales()
    print(f"Found {len(sales)} sales in database")
    
    if sales:
        # Get the first sale
        sale = sales[0]
        print(f"Testing with sale ID: {sale.id}")
        print(f"Sale total: {sale.total:.2f} DH")
        print(f"Sale timestamp: {sale.timestamp}")
        print(f"Number of items: {len(sale.items)}")
        
        # Test getting sale by ID
        retrieved_sale = db_manager.get_sale_by_id(sale.id)
        if retrieved_sale:
            print(f"Successfully retrieved sale by ID: {retrieved_sale.id}")
            
            # Test printing
            printer = AdvancedReceiptPrinter()
            result = printer.print_receipt(retrieved_sale)
            print(f"Print result: {result}")
        else:
            print("Failed to retrieve sale by ID")
    else:
        print("No sales found in database")

if __name__ == "__main__":
    test_print_from_history()

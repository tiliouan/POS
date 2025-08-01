#!/usr/bin/env python3
"""
Test PDF Receipt Generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from models.sale import Sale, SaleItem
from models.product import Product
from models.payment import Payment, PaymentMethod, PaymentStatus
from utils.advanced_receipt_printer import AdvancedReceiptPrinter

def create_test_sale():
    """Create a test sale for PDF generation."""
    # Create test products
    product1 = Product(
        id=1,
        name="Café",
        description="Café noir traditionnel",
        price=15.00,
        barcode="CAFE001",
        category="Boissons",
        stock_quantity=50
    )
    
    product2 = Product(
        id=2,
        name="Croissant",
        description="Croissant au beurre frais",
        price=8.00,
        barcode="CROI001",
        category="Pâtisserie",
        stock_quantity=20
    )
    
    # Create sale items
    item1 = SaleItem(product=product1, quantity=2, unit_price=15.00)
    item2 = SaleItem(product=product2, quantity=1, unit_price=8.00)
    
    # Create payment
    payment = Payment(
        method=PaymentMethod.CASH,
        amount=40.00,
        status=PaymentStatus.COMPLETED,
        change_amount=2.00
    )
    
    # Create sale
    sale = Sale(
        id=999,
        items=[item1, item2],
        timestamp=datetime.now(),
        cashier_id="Test User",
        payment=payment
    )
    
    return sale

def test_pdf_generation():
    """Test PDF receipt generation."""
    print("🧪 Testing PDF receipt generation...")
    
    try:
        # Create test sale
        sale = create_test_sale()
        
        # Initialize printer
        printer = AdvancedReceiptPrinter()
        
        # Test thermal PDF
        print("📄 Generating thermal PDF...")
        thermal_path = printer.generate_and_open_pdf_receipt(sale, "thermal")
        print(f"✅ Thermal PDF: {thermal_path}")
        
        # Test A4 PDF
        print("📄 Generating A4 PDF...")
        a4_path = printer.generate_and_open_pdf_receipt(sale, "a4")
        print(f"✅ A4 PDF: {a4_path}")
        
        print("\n🎉 PDF generation test completed successfully!")
        print(f"📁 Check the 'receipts' folder for generated PDFs")
        
    except Exception as e:
        print(f"❌ Error during PDF generation test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation()

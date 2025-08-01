"""
POS System Demo
===============

This script demonstrates the POS system functionality programmatically.
"""

from models.product import Product
from models.sale import Sale, SaleItem
from models.payment import Payment, PaymentMethod
from database.db_manager import DatabaseManager
from utils.receipt_printer import ReceiptPrinter
from datetime import datetime

def demo_pos_system():
    """Demonstrate POS system functionality."""
    print("=" * 60)
    print("DEMONSTRATION DU SYSTÈME DE CAISSE")
    print("=" * 60)
    
    # Initialize components
    db = DatabaseManager()
    receipt_printer = ReceiptPrinter("Point of Sale Demo", "123 Rue Example, Casablanca")
    
    print("\n1. Chargement des produits...")
    products = db.get_all_products()
    print(f"   Produits disponibles: {len(products)}")
    for product in products[:5]:  # Show first 5 products
        print(f"   - {product.name}: {product.price:.2f} د.م")
    
    print("\n2. Création d'une vente...")
    sale = Sale()
    sale.cashier_id = "demo_user"
    
    # Add some items to the sale
    if len(products) >= 3:
        sale.add_item(products[0], 2)  # 2x first product
        sale.add_item(products[1], 1)  # 1x second product
        sale.add_item(products[2], 3)  # 3x third product
        
        print(f"   Articles ajoutés au panier:")
        for item in sale.items:
            print(f"   - {item.quantity}x {item.product.name} = {item.total:.2f} د.م")
    
    print(f"\n3. Calcul du total...")
    print(f"   Sous-total: {sale.subtotal:.2f} د.م")
    print(f"   Total: {sale.total:.2f} د.م")
    
    print("\n4. Traitement du paiement...")
    # Create cash payment
    payment_amount = sale.total + 10.0  # Pay with extra for change
    payment = Payment(PaymentMethod.CASH, payment_amount)
    payment.calculate_change(sale.total)
    payment.mark_completed()
    
    sale.payment = payment
    
    print(f"   Montant payé: {payment.amount:.2f} د.م")
    print(f"   Monnaie: {payment.change_amount:.2f} د.م")
    
    print("\n5. Sauvegarde de la vente...")
    sale_id = db.save_sale(sale)
    print(f"   Vente #{sale_id} sauvegardée")
    
    print("\n6. Génération du reçu...")
    receipt_printer.print_receipt(sale)
    
    print("\n7. Rapport quotidien...")
    today = datetime.now()
    summary = db.get_daily_sales_summary(today)
    receipt_printer.print_daily_report(summary)
    
    print("\n" + "=" * 60)
    print("DÉMONSTRATION TERMINÉE AVEC SUCCÈS!")
    print("Lancez 'python main.py' pour utiliser l'interface graphique.")
    print("=" * 60)

if __name__ == "__main__":
    demo_pos_system()

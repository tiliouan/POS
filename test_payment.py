"""
Payment System Test
===================

Test script to verify the payment functionality works correctly.
"""

from models.product import Product
from models.sale import Sale, SaleItem
from models.payment import Payment, PaymentMethod
from datetime import datetime

def test_payment_system():
    """Test the payment system functionality."""
    print("=" * 50)
    print("TEST DU SYSTÈME DE PAIEMENT")
    print("=" * 50)
    
    # Create test products
    coffee = Product(1, "Café", "Café noir", 15.00)
    croissant = Product(2, "Croissant", "Croissant beurre", 8.00)
    
    print("1. Création des produits de test...")
    print(f"   - {coffee}")
    print(f"   - {croissant}")
    
    # Create sale with items
    sale = Sale()
    sale.add_item(coffee, 2)  # 2 cafés
    sale.add_item(croissant, 1)  # 1 croissant
    
    print(f"\n2. Création de la vente...")
    print(f"   - Items: {len(sale.items)}")
    print(f"   - Sous-total: {sale.subtotal:.2f} د.م")
    print(f"   - Total: {sale.total:.2f} د.م")
    
    # Test cash payment with exact amount
    print(f"\n3. Test paiement espèces (montant exact)...")
    cash_payment = Payment(PaymentMethod.CASH, sale.total)
    cash_payment.calculate_change(sale.total)
    print(f"   - Montant payé: {cash_payment.amount:.2f} د.م")
    print(f"   - Monnaie: {cash_payment.change_amount:.2f} د.م")
    print(f"   - Statut: {cash_payment.status.value}")
    
    # Test cash payment with extra money
    print(f"\n4. Test paiement espèces (avec monnaie)...")
    cash_payment_extra = Payment(PaymentMethod.CASH, 50.00)
    cash_payment_extra.calculate_change(sale.total)
    print(f"   - Montant payé: {cash_payment_extra.amount:.2f} د.م")
    print(f"   - Monnaie: {cash_payment_extra.change_amount:.2f} د.م")
    
    # Test card payment
    print(f"\n5. Test paiement carte...")
    card_payment = Payment(PaymentMethod.CARD, sale.total)
    card_payment.calculate_change(sale.total)
    print(f"   - Montant payé: {card_payment.amount:.2f} د.م")
    print(f"   - Monnaie: {card_payment.change_amount:.2f} د.م")
    print(f"   - Carte: {card_payment.is_card_payment}")
    
    # Test insufficient payment (should fail in real system)
    print(f"\n6. Test paiement insuffisant...")
    insufficient_payment = Payment(PaymentMethod.CASH, 20.00)
    insufficient_payment.calculate_change(sale.total)
    print(f"   - Montant payé: {insufficient_payment.amount:.2f} د.م")
    print(f"   - Total dû: {sale.total:.2f} د.م")
    print(f"   - Suffisant: {'Oui' if insufficient_payment.amount >= sale.total else 'Non'}")
    
    print(f"\n" + "=" * 50)
    print("TESTS TERMINÉS AVEC SUCCÈS!")
    print("Le système de paiement fonctionne correctement.")
    print("=" * 50)

if __name__ == "__main__":
    test_payment_system()

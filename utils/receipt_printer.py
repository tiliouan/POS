"""
Receipt Printer
===============

This module handles receipt generation and printing for the POS system.
"""

from typing import TextIO
from datetime import datetime
from models.sale import Sale
from models.payment import PaymentMethod

class ReceiptPrinter:
    """Handles receipt printing and generation."""
    
    def __init__(self, store_name: str = "Point of Sale", store_address: str = ""):
        """Initialize receipt printer."""
        self.store_name = store_name
        self.store_address = store_address
    
    def print_receipt(self, sale: Sale, print_to_file: bool = True) -> str:
        """Print receipt for a sale."""
        receipt_text = self.generate_receipt_text(sale)
        
        if print_to_file:
            filename = f"receipt_{sale.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(receipt_text)
            print(f"Reçu sauvegardé: {filename}")
        
        # Print to console for demonstration
        print("\\n" + "="*50)
        print("REÇU IMPRIMÉ:")
        print("="*50)
        print(receipt_text)
        print("="*50)
        
        return receipt_text
    
    def generate_receipt_text(self, sale: Sale) -> str:
        """Generate receipt text."""
        lines = []
        
        # Header
        lines.append(self._center_text(self.store_name, 40))
        if self.store_address:
            lines.append(self._center_text(self.store_address, 40))
        lines.append("-" * 40)
        
        # Sale info
        lines.append(f"Commande #{sale.id or 'N/A'}")
        lines.append(f"Date: {sale.timestamp.strftime('%d/%m/%Y %H:%M') if sale.timestamp else 'N/A'}")
        lines.append(f"Caissier: {sale.cashier_id or 'Admin'}")
        lines.append("-" * 40)
        
        # Items
        lines.append("ARTICLES:")
        for item in sale.items:
            lines.append(f"{item.product.name}")
            lines.append(f"  {item.quantity} x {item.unit_price:.2f} د.م = {item.total:.2f} د.م")
            if item.discount > 0:
                lines.append(f"  Remise: -{item.discount:.2f} د.م")
        
        lines.append("-" * 40)
        
        # Totals
        lines.append(f"Sous-total:     {sale.subtotal:.2f} د.م")
        
        if sale.tax_amount > 0:
            lines.append(f"TVA ({sale.tax_rate*100:.1f}%):        {sale.tax_amount:.2f} د.م")
        
        if sale.discount > 0:
            lines.append(f"Remise:        -{sale.discount:.2f} د.م")
        
        lines.append("=" * 40)
        lines.append(f"TOTAL:          {sale.total:.2f} د.م")
        lines.append("=" * 40)
        
        # Payment info
        if sale.payment:
            payment_method = self._get_payment_method_text(sale.payment.method)
            lines.append(f"Mode de paiement: {payment_method}")
            lines.append(f"Montant payé:     {sale.payment.amount:.2f} د.م")
            
            if sale.payment.change_amount > 0:
                lines.append(f"Monnaie:          {sale.payment.change_amount:.2f} د.م")
        
        lines.append("-" * 40)
        
        # Footer
        lines.append(self._center_text("Merci de votre visite!", 40))
        lines.append(self._center_text("À bientôt!", 40))
        
        if sale.notes:
            lines.append("-" * 40)
            lines.append(f"Note: {sale.notes}")
        
        return "\\n".join(lines)
    
    def _center_text(self, text: str, width: int) -> str:
        """Center text within given width."""
        return text.center(width)
    
    def _get_payment_method_text(self, method: PaymentMethod) -> str:
        """Get human-readable payment method text."""
        method_map = {
            PaymentMethod.CASH: "Espèces",
            PaymentMethod.CARD: "Carte bancaire",
            PaymentMethod.MOBILE: "Paiement mobile",
            PaymentMethod.CHECK: "Chèque",
            PaymentMethod.STORE_CREDIT: "Crédit magasin"
        }
        return method_map.get(method, method.value)
    
    def print_daily_report(self, sales_summary: dict) -> str:
        """Print daily sales report."""
        lines = []
        
        # Header
        lines.append(self._center_text("RAPPORT QUOTIDIEN", 40))
        lines.append(self._center_text(self.store_name, 40))
        lines.append("-" * 40)
        
        # Date
        lines.append(f"Date: {sales_summary.get('date', 'N/A')}")
        lines.append("-" * 40)
        
        # Statistics
        lines.append(f"Nombre de ventes:   {sales_summary.get('total_sales', 0)}")
        lines.append(f"Articles vendus:    {sales_summary.get('total_items', 0)}")
        lines.append(f"Vente moyenne:      {sales_summary.get('average_sale', 0.0):.2f} د.م")
        lines.append("=" * 40)
        lines.append(f"TOTAL DU JOUR:      {sales_summary.get('total_revenue', 0.0):.2f} د.م")
        lines.append("=" * 40)
        
        report_text = "\\n".join(lines)
        
        # Print to console
        print("\\n" + "="*50)
        print("RAPPORT QUOTIDIEN:")
        print("="*50)
        print(report_text)
        print("="*50)
        
        return report_text

"""
Enhanced Receipt Printer
=========================

This module handles advanced receipt generation and printing with customizable templates.
"""

import os
import sys
import subprocess
import webbrowser
from typing import TextIO, Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect
from io import BytesIO
import tempfile

from models.sale import Sale
from models.payment import PaymentMethod
from config.receipt_settings import ReceiptSettingsManager, get_available_printers
from config.language_settings import get_text, language_manager

class AdvancedReceiptPrinter:
    """Advanced receipt printer with template support and multiple output formats."""
    
    def __init__(self):
        """Initialize the advanced receipt printer."""
        self.settings_manager = ReceiptSettingsManager()
        self.settings = self.settings_manager.get_settings()
    
    def print_receipt(self, sale: Sale, printer_name: str = None, format_type: str = "pdf") -> str:
        """Print receipt in the specified format."""
        try:
            if format_type == "pdf" or printer_name == "Save as PDF" or not printer_name:
                return self.generate_and_open_pdf_receipt(sale)
            else:
                return self.print_thermal_receipt(sale, printer_name)
        except Exception as e:
            print(f"Error printing receipt: {e}")
            return f"Error: {e}"
    
    def generate_and_open_pdf_receipt(self, sale: Sale, size: str = "58mm") -> str:
        """Generate 58mm PDF receipt and open it in default PDF viewer."""
        try:
            # Create receipts directory if it doesn't exist
            receipts_dir = "receipts"
            if not os.path.exists(receipts_dir):
                os.makedirs(receipts_dir)
            
            # Generate PDF filename (58mm is default)
            timestamp = sale.timestamp.strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"receipt_{sale.id}_{timestamp}.pdf"
            pdf_path = os.path.join(receipts_dir, pdf_filename)
            
            # Generate 58mm PDF receipt
            self.create_58mm_pdf_receipt(sale, pdf_path)
            
            # Open PDF in default application
            self.open_pdf_file(pdf_path)
            
            return f"Receipt saved as PDF: {pdf_path}"
            
        except Exception as e:
            print(f"Error generating PDF receipt: {e}")
            import traceback
            traceback.print_exc()
            return f"Error generating PDF: {e}"
    
    def create_58mm_pdf_receipt(self, sale: Sale, pdf_path: str):
        """Create a professional 58mm PDF receipt with proper formatting and print capability."""
        # Create PDF document with metadata for 58mm thermal size
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=(58*mm, 150*mm),  # 58mm width, variable height
            rightMargin=2*mm,
            leftMargin=2*mm,
            topMargin=5*mm,
            bottomMargin=5*mm,
            title=f"Receipt #{sale.id}",
            author=self.settings.store_name or "POS System",
            subject=f"Sales Receipt {sale.id}",
            creator="POS System",
            keywords="receipt,sale,invoice"
        )
        
        # Get styles optimized for 58mm
        styles = getSampleStyleSheet()
        
        # Custom styles for 58mm thermal receipt
        title_style = ParagraphStyle(
            'ThermalTitle',
            parent=styles['Heading1'],
            fontSize=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=3
        )
        
        header_style = ParagraphStyle(
            'ThermalHeader',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            fontName='Helvetica',
            spaceAfter=2
        )
        
        normal_style = ParagraphStyle(
            'ThermalNormal',
            parent=styles['Normal'],
            fontSize=7,
            fontName='Helvetica',
            spaceAfter=1
        )
        
        total_style = ParagraphStyle(
            'ThermalTotal',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Bold',
            spaceAfter=2
        )
        
        # Build content
        story = []
        
        # Logo and store info (smaller for 58mm)
        if self.settings.logo_enabled and self.settings.logo_path:
            if os.path.exists(self.settings.logo_path):
                try:
                    logo = Image(self.settings.logo_path, width=25*mm, height=12*mm)
                    logo.hAlign = 'CENTER'
                    story.append(logo)
                    story.append(Spacer(1, 2*mm))
                except:
                    pass
        
        # Store name
        if self.settings.store_name:
            story.append(Paragraph(self.settings.store_name, title_style))
        
        # Store details (compact for 58mm)
        if hasattr(self.settings, 'store_address_line1') and self.settings.store_address_line1:
            story.append(Paragraph(self.settings.store_address_line1, header_style))
        if hasattr(self.settings, 'store_address_line2') and self.settings.store_address_line2:
            story.append(Paragraph(self.settings.store_address_line2, header_style))
        if hasattr(self.settings, 'store_phone') and self.settings.store_phone:
            story.append(Paragraph(self.settings.store_phone, header_style))
        
        story.append(Spacer(1, 2*mm))
        
        # Separator line (shorter for 58mm)
        story.append(Paragraph("=" * 24, normal_style))
        
        # Receipt info
        receipt_date = sale.timestamp.strftime("%d/%m/%Y %H:%M")
        story.append(Paragraph(f"<b>{get_text('receipt_no')}:</b> {sale.id}", normal_style))
        story.append(Paragraph(f"<b>{get_text('date')}:</b> {receipt_date}", normal_style))
        if sale.cashier_id:
            story.append(Paragraph(f"<b>Cashier:</b> {sale.cashier_id}", normal_style))
        
        story.append(Spacer(1, 2*mm))
        story.append(Paragraph("-" * 24, normal_style))
        
        # Items (optimized for 58mm width)
        for item in sale.items:
            item_total = item.quantity * item.unit_price
            
            # Product name
            story.append(Paragraph(f"<b>{item.product.name}</b>", normal_style))
            
            # Quantity and price on one line
            qty_price = f"{item.quantity} x {item.unit_price:.2f} = {item_total:.2f} DH"
            story.append(Paragraph(qty_price, normal_style))
            story.append(Spacer(1, 1*mm))
        
        story.append(Paragraph("-" * 24, normal_style))
        
        # Totals (compact)
        story.append(Paragraph(f"<b>{get_text('subtotal_label')}:</b> {sale.subtotal:.2f} DH", normal_style))
        
        if sale.tax_amount > 0:
            story.append(Paragraph(f"<b>{get_text('tax')}:</b> {sale.tax_amount:.2f} DH", normal_style))
        
        if sale.discount > 0:
            story.append(Paragraph(f"<b>{get_text('discount')}:</b> -{sale.discount:.2f} DH", normal_style))
        
        story.append(Spacer(1, 1*mm))
        story.append(Paragraph("=" * 24, normal_style))
        story.append(Paragraph(f"<b>{get_text('total_label')}:</b> {sale.total:.2f} DH", total_style))
        
        # Payment info
        if sale.payment:
            payment_method = self._get_payment_method_text(sale.payment.method)
            story.append(Paragraph(f"<b>{payment_method}:</b> {sale.payment.amount:.2f} DH", normal_style))
            
            if sale.payment.change_amount > 0:
                story.append(Paragraph(f"<b>{get_text('change')}:</b> {sale.payment.change_amount:.2f} DH", normal_style))
        
        story.append(Spacer(1, 3*mm))
        story.append(Paragraph("=" * 24, normal_style))
        
        # Footer
        footer_text = self.settings.footer_message if self.settings.footer_message else get_text("thank_you")
        story.append(Paragraph(footer_text, header_style))
        
        if self.settings.show_tax_number and self.settings.tax_number:
            story.append(Spacer(1, 1*mm))
            story.append(Paragraph(f"Tax ID: {self.settings.tax_number}", normal_style))
        
        # Build PDF
        doc.build(story)
        
    def open_pdf_file(self, pdf_path: str):
        """Open PDF file in default application (SumatraPDF or other)."""
        try:
            # Convert to absolute path
            abs_path = os.path.abspath(pdf_path)
            
            if sys.platform.startswith('win'):
                # Windows - use os.startfile for better compatibility
                print(f"Opening PDF: {abs_path}")
                os.startfile(abs_path)
                
                # Give it a moment to open
                import time
                time.sleep(0.5)
                
            elif sys.platform.startswith('darwin'):
                # macOS
                subprocess.call(['open', abs_path])
            else:
                # Linux
                subprocess.call(['xdg-open', abs_path])
                
        except Exception as e:
            print(f"Could not open PDF automatically: {e}")
            # Fallback: try subprocess with explicit command
            try:
                if sys.platform.startswith('win'):
                    # Try with cmd /c start for Windows
                    subprocess.run(['cmd', '/c', 'start', '', abs_path], shell=True, check=True)
                else:
                    # For other systems, try webbrowser
                    webbrowser.open(f'file://{abs_path}')
            except Exception as e2:
                print(f"Could not open PDF with fallback method: {e2}")
                print(f"PDF saved at: {abs_path}")
                print("Please open the file manually.")
    
    def generate_pdf_receipt(self, sale: Sale) -> str:
        """Generate PDF receipt and return the file path."""
        receipts_dir = "receipts"
        if not os.path.exists(receipts_dir):
            os.makedirs(receipts_dir)
        
        timestamp = sale.timestamp.strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"receipt_{sale.id}_{timestamp}.pdf"
        pdf_path = os.path.join(receipts_dir, pdf_filename)
        
        self.create_professional_pdf_receipt(sale, pdf_path)
        return pdf_path
    
    def print_thermal_receipt(self, sale: Sale, printer_name: str = None) -> str:
        """Print thermal receipt (80mm)."""
        receipt_text = self.generate_thermal_receipt_text(sale)
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"receipts/receipt_{sale.id}_{timestamp}.txt"
        os.makedirs("receipts", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(receipt_text)
        
        # Print to printer if specified
        if printer_name and printer_name != "Save as PDF":
            self.send_to_printer(filename, printer_name)
        
        print(f"Reçu sauvegardé: {filename}")
        return receipt_text
    
    def generate_thermal_receipt_text(self, sale: Sale, paper_size: str = "80mm") -> str:
        """Generate thermal receipt text with specified paper size."""
        lines = []
        
        # Set width based on paper size
        if paper_size == "58mm":
            width = 32  # 58mm paper width
        else:  # 80mm default
            width = 48  # 80mm paper width
        
        # Logo/Header
        if self.settings.logo_enabled:
            if self.settings.logo_path and os.path.exists(self.settings.logo_path):
                # For thermal printing, we'll add a special marker for logo processing
                lines.append("**LOGO_IMAGE**")
                lines.append(f"**LOGO_PATH:{self.settings.logo_path}**")
            else:
                lines.append(self._center_text(self.settings.logo_text or "POS SYSTEM", width))
        
        lines.append("")
        
        # Store Information
        lines.append(self._center_text(self.settings.store_name, width))
        if self.settings.store_address_line1:
            lines.append(self._center_text(self.settings.store_address_line1, width))
        if self.settings.store_address_line2:
            lines.append(self._center_text(self.settings.store_address_line2, width))
        if self.settings.store_phone:
            lines.append(self._center_text(self.settings.store_phone, width))
        
        lines.append("=" * width)
        
        # Order Information
        lines.append(f"{get_text('receipt')}: {sale.id or 'N/A'}")
        lines.append(f"{get_text('date')}: {sale.timestamp.strftime('%d/%m/%Y %H:%M') if sale.timestamp else datetime.now().strftime('%d/%m/%Y %H:%M')}")
        if sale.cashier_id:
            lines.append(f"Cashier: {sale.cashier_id}")
        
        lines.append("-" * width)
        
        # Items
        for item in sale.items:
            # Product name
            lines.append(f"{item.product.name}")
            
            # Quantity and price line
            qty_price = f"{item.quantity} x {item.unit_price:.2f}"
            total_price = f"{item.total:.2f} DH"
            spaces_needed = width - len(qty_price) - len(total_price)
            lines.append(f"{qty_price}{' ' * max(1, spaces_needed)}{total_price}")
            
            if item.discount > 0:
                lines.append(f"  Discount: -{item.discount:.2f} DH")
        
        lines.append("-" * width)
        
        # Totals
        lines.append(self._format_total_line(get_text("total").upper(), sale.total, width))
        
        # Payment Information
        if sale.payment:
            payment_method = self._get_payment_method_text(sale.payment.method)
            lines.append(self._format_total_line(payment_method, sale.payment.amount, width))
            
            if sale.payment.change_amount > 0:
                lines.append(self._format_total_line(get_text("change"), sale.payment.change_amount, width))
        
        lines.append("=" * width)
        
        # Footer
        if self.settings.show_footer and self.settings.footer_message:
            lines.append("")
            footer_text = self.settings.footer_message if self.settings.footer_message else get_text("thank_you")
            lines.append(self._center_text(footer_text, width))
        
        # Tax number if enabled
        if self.settings.show_tax_number and self.settings.tax_number:
            lines.append("")
            lines.append(self._center_text(f"Tax ID: {self.settings.tax_number}", width))
        
        lines.append("")
        
        return "\n".join(lines)
    
    def generate_pdf_receipt(self, sale: Sale) -> str:
        """Generate PDF receipt."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"receipts/receipt_{sale.id}_{timestamp}.pdf"
        os.makedirs("receipts", exist_ok=True)
        
        # Create PDF
        doc = SimpleDocTemplate(filename, pagesize=(80*mm, 200*mm), 
                              leftMargin=5*mm, rightMargin=5*mm,
                              topMargin=5*mm, bottomMargin=5*mm)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=3*mm
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_LEFT,
            spaceAfter=1*mm
        )
        
        center_style = ParagraphStyle(
            'CustomCenter',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            spaceAfter=1*mm
        )
        
        # Logo
        if self.settings.logo_enabled and self.settings.logo_path and os.path.exists(self.settings.logo_path):
            try:
                logo = Image(self.settings.logo_path, width=20*mm, height=20*mm)
                story.append(logo)
            except:
                story.append(Paragraph(self.settings.logo_text, center_style))
        elif self.settings.logo_enabled:
            story.append(Paragraph(self.settings.logo_text, center_style))
        
        # Store info
        story.append(Paragraph(self.settings.store_name, title_style))
        if self.settings.store_address_line1:
            story.append(Paragraph(self.settings.store_address_line1, center_style))
        if self.settings.store_address_line2:
            story.append(Paragraph(self.settings.store_address_line2, center_style))
        
        story.append(Spacer(1, 3*mm))
        
        # Order info
        story.append(Paragraph(f"Order: {sale.id or 'N/A'}", normal_style))
        story.append(Paragraph(f"Date: {sale.timestamp.strftime('%d/%m/%Y %H:%M') if sale.timestamp else datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
        if sale.cashier_id:
            story.append(Paragraph(f"Cashier: {sale.cashier_id}", normal_style))
        
        story.append(Spacer(1, 2*mm))
        
        # Items table
        items_data = [["Item", "Qty", "Price", "Total"]]
        for item in sale.items:
            items_data.append([
                item.product.name,
                str(item.quantity),
                f"{item.unit_price:.2f}",
                f"{item.total:.2f} DH"
            ])
        
        items_table = Table(items_data, colWidths=[30*mm, 10*mm, 15*mm, 15*mm])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 3*mm))
        
        # Total
        total_data = [["TOTAL", f"{sale.total:.2f} DH"]]
        if sale.payment:
            payment_method = self._get_payment_method_text(sale.payment.method)
            total_data.append([payment_method, f"{sale.payment.amount:.2f} DH"])
            if sale.payment.change_amount > 0:
                total_data.append(["Change", f"{sale.payment.change_amount:.2f} DH"])
        
        total_table = Table(total_data, colWidths=[40*mm, 30*mm])
        total_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        story.append(total_table)
        
        # Footer
        if self.settings.show_footer and self.settings.footer_message:
            story.append(Spacer(1, 5*mm))
            story.append(Paragraph(self.settings.footer_message, center_style))
        
        doc.build(story)
        print(f"PDF receipt saved: {filename}")
        return filename
    
    def send_to_printer(self, filename: str, printer_name: str) -> bool:
        """Send file to printer."""
        try:
            if sys.platform == "win32":
                # Windows printing
                if filename.endswith('.pdf'):
                    # Print PDF
                    subprocess.run([
                        'powershell', '-Command',
                        f'Start-Process -FilePath "{filename}" -Verb Print -WindowStyle Hidden'
                    ], check=True)
                else:
                    # Print text file
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create temporary file for printing
                    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
                    temp_file.write(content)
                    temp_file.close()
                    
                    subprocess.run(['notepad', '/p', temp_file.name], check=True)
                    os.unlink(temp_file.name)
                
                print(f"Sent to printer: {printer_name}")
                return True
                
        except Exception as e:
            print(f"Error printing to {printer_name}: {e}")
            return False
    
    def _center_text(self, text: str, width: int) -> str:
        """Center text within given width."""
        return text.center(width)
    
    def _format_total_line(self, label: str, amount: float, width: int) -> str:
        """Format a total line with right-aligned amount."""
        amount_str = f"{amount:.2f} DH"
        spaces_needed = width - len(label) - len(amount_str)
        return f"{label}{' ' * max(1, spaces_needed)}{amount_str}"
    
    def _get_payment_method_text(self, method: PaymentMethod) -> str:
        """Get human-readable payment method text."""
        method_map = {
            PaymentMethod.CASH: "Espèce",
            PaymentMethod.CARD: "Card"
        }
        return method_map.get(method, method.value)
    
    def get_available_printers(self) -> list:
        """Get list of available printers."""
        return get_available_printers()
    
    def update_settings(self, **kwargs):
        """Update receipt settings."""
        self.settings_manager.update_settings(**kwargs)
        self.settings = self.settings_manager.get_settings()

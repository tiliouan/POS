"""
CSV Product Import Utility
==========================

This module handles importing products from CSV files.
"""

import csv
import os
import re
from typing import List, Dict, Tuple, Optional
from tkinter import messagebox
from models.product import Product
from database.db_manager import DatabaseManager
from config.language_settings import get_text

class CSVProductImporter:
    """Handles importing products from CSV files."""
    
    def __init__(self, db_manager: DatabaseManager = None):
        """Initialize the CSV importer."""
        self.db_manager = db_manager or DatabaseManager()
        
        # CSV column mappings - you can customize these based on your CSV format
        self.column_mappings = {
            # WooCommerce CSV format (as shown in your example)
            'woocommerce': {
                'name': ['Nom', 'Name', 'nom', 'name'],
                'description': ['Description', 'Description courte', 'description'],
                'price': ['Tarif régulier', 'Regular price', 'Prix', 'Price', 'price'],
                'barcode': ['UGS', 'SKU', 'GTIN, UPC, EAN ou ISBN', 'Barcode', 'barcode'],
                'category': ['Catégories', 'Categories', 'Category', 'category'],
                'stock': ['Stock', 'stock', 'Stock quantity', 'Quantité en stock'],
                'cost_price': ['Cost', 'cout', 'Cost price', 'Prix de revient']
            },
            # Generic CSV format
            'generic': {
                'name': ['name', 'nom', 'product_name', 'produit'],
                'description': ['description', 'desc'],
                'price': ['price', 'prix', 'selling_price'],
                'barcode': ['barcode', 'sku', 'code'],
                'category': ['category', 'categorie'],
                'stock': ['stock', 'quantity', 'qty'],
                'cost_price': ['cost', 'cost_price', 'prix_achat']
            }
        }
    
    def detect_csv_format(self, headers: List[str]) -> str:
        """Detect the CSV format based on headers."""
        # Check for WooCommerce format
        woo_indicators = ['UGS', 'Nom', 'Tarif régulier', 'Catégories']
        if any(indicator in headers for indicator in woo_indicators):
            return 'woocommerce'
        
        return 'generic'
    
    def find_column_index(self, headers: List[str], field_mappings: List[str]) -> Optional[int]:
        """Find the index of a column based on possible field names."""
        headers_lower = [h.lower().strip() for h in headers]
        
        for mapping in field_mappings:
            mapping_lower = mapping.lower().strip()
            for i, header in enumerate(headers_lower):
                if mapping_lower == header or mapping_lower in header:
                    return i
        return None
    
    def clean_price_value(self, value: str) -> float:
        """Clean and convert price value to float."""
        if not value or value.strip() == '':
            return 0.0
        
        # Remove currency symbols and spaces
        cleaned = re.sub(r'[^\d.,]', '', str(value))
        
        # Handle decimal separators
        if ',' in cleaned and '.' in cleaned:
            # Both comma and dot present - assume dot is decimal
            cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            # Only comma - could be thousands separator or decimal
            parts = cleaned.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                # Likely decimal separator
                cleaned = cleaned.replace(',', '.')
            else:
                # Likely thousands separator
                cleaned = cleaned.replace(',', '')
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def clean_stock_value(self, value: str) -> int:
        """Clean and convert stock value to integer."""
        if not value or value.strip() == '':
            return 0
        
        # Extract only digits
        cleaned = re.sub(r'[^\d]', '', str(value))
        
        try:
            return int(cleaned) if cleaned else 0
        except ValueError:
            return 0
    
    def clean_barcode_value(self, value: str) -> Optional[str]:
        """Clean barcode value - accepts WooCommerce style barcodes with special characters."""
        if not value or value.strip() == '':
            return None
        
        original_value = str(value).strip()
        
        # Skip if too short
        if len(original_value) < 2:
            return None
        
        # Accept WooCommerce barcodes as-is (they can contain special characters)
        # Just remove leading/trailing whitespace and return the original value
        # This preserves barcodes like '-&&&é'é-_à-"à exactly as they are
        
        return original_value
    
    def validate_product_data(self, product_data: Dict) -> Tuple[bool, List[str]]:
        """Validate product data before import."""
        errors = []
        
        # Required fields
        if not product_data.get('name', '').strip():
            errors.append("Product name is required")
        
        # Price validation
        if product_data.get('price', 0) <= 0:
            errors.append("Price must be greater than 0")
        
        # Name length validation
        if len(product_data.get('name', '')) > 255:
            errors.append("Product name is too long (max 255 characters)")
        
        return len(errors) == 0, errors
    
    def preview_csv_import(self, csv_file_path: str, max_preview: int = 10) -> Tuple[List[Dict], List[str], str]:
        """Preview CSV import without actually importing."""
        preview_data = []
        errors = []
        format_detected = 'generic'
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8', newline='') as file:
                # Try to detect encoding
                sample = file.read(1024)
                file.seek(0)
                
                # Read CSV
                csv_reader = csv.reader(file)
                headers = next(csv_reader)
                
                # Detect format
                format_detected = self.detect_csv_format(headers)
                mappings = self.column_mappings[format_detected]
                
                # Find column indices
                name_idx = self.find_column_index(headers, mappings['name'])
                price_idx = self.find_column_index(headers, mappings['price'])
                desc_idx = self.find_column_index(headers, mappings['description'])
                barcode_idx = self.find_column_index(headers, mappings['barcode'])
                category_idx = self.find_column_index(headers, mappings['category'])
                stock_idx = self.find_column_index(headers, mappings['stock'])
                cost_idx = self.find_column_index(headers, mappings['cost_price'])
                
                if name_idx is None:
                    errors.append("Could not find product name column")
                    return preview_data, errors, format_detected
                
                # Process rows
                row_count = 0
                for row_num, row in enumerate(csv_reader, 2):  # Start from 2 (header is 1)
                    if row_count >= max_preview:
                        break
                    
                    if len(row) <= max(idx for idx in [name_idx, price_idx, desc_idx, barcode_idx, category_idx, stock_idx, cost_idx] if idx is not None):
                        continue
                    
                    # Extract data
                    product_data = {
                        'row_number': row_num,
                        'name': row[name_idx].strip() if name_idx is not None else '',
                        'description': row[desc_idx].strip() if desc_idx is not None and desc_idx < len(row) else '',
                        'price': self.clean_price_value(row[price_idx]) if price_idx is not None and price_idx < len(row) else 0.0,
                        'original_barcode': row[barcode_idx] if barcode_idx is not None and barcode_idx < len(row) else '',
                        'barcode': self.clean_barcode_value(row[barcode_idx]) if barcode_idx is not None and barcode_idx < len(row) else None,
                        'category': row[category_idx].strip() if category_idx is not None and category_idx < len(row) else 'Uncategorized',
                        'stock_quantity': self.clean_stock_value(row[stock_idx]) if stock_idx is not None and stock_idx < len(row) else 0,
                        'cost_price': self.clean_price_value(row[cost_idx]) if cost_idx is not None and cost_idx < len(row) else 0.0
                    }
                    
                    # Skip empty rows
                    if not product_data['name']:
                        continue
                    
                    # Validate
                    is_valid, validation_errors = self.validate_product_data(product_data)
                    if not is_valid:
                        product_data['errors'] = validation_errors
                    
                    preview_data.append(product_data)
                    row_count += 1
                
        except Exception as e:
            errors.append(f"Error reading CSV file: {str(e)}")
        
        return preview_data, errors, format_detected
    
    def import_csv_products(self, csv_file_path: str, update_existing: bool = False) -> Tuple[int, int, List[str]]:
        """Import products from CSV file."""
        imported_count = 0
        updated_count = 0
        errors = []
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8', newline='') as file:
                csv_reader = csv.reader(file)
                headers = next(csv_reader)
                
                # Detect format and get mappings
                format_detected = self.detect_csv_format(headers)
                mappings = self.column_mappings[format_detected]
                
                # Find column indices
                name_idx = self.find_column_index(headers, mappings['name'])
                price_idx = self.find_column_index(headers, mappings['price'])
                desc_idx = self.find_column_index(headers, mappings['description'])
                barcode_idx = self.find_column_index(headers, mappings['barcode'])
                category_idx = self.find_column_index(headers, mappings['category'])
                stock_idx = self.find_column_index(headers, mappings['stock'])
                cost_idx = self.find_column_index(headers, mappings['cost_price'])
                
                if name_idx is None:
                    errors.append("Could not find product name column")
                    return 0, 0, errors
                
                # Process each row
                for row_num, row in enumerate(csv_reader, 2):
                    try:
                        if len(row) <= max(idx for idx in [name_idx, price_idx, desc_idx, barcode_idx, category_idx, stock_idx, cost_idx] if idx is not None):
                            continue
                        
                        # Extract product data
                        name = row[name_idx].strip() if name_idx is not None else ''
                        if not name:
                            continue
                        
                        description = row[desc_idx].strip() if desc_idx is not None and desc_idx < len(row) else ''
                        price = self.clean_price_value(row[price_idx]) if price_idx is not None and price_idx < len(row) else 0.0
                        barcode = self.clean_barcode_value(row[barcode_idx]) if barcode_idx is not None and barcode_idx < len(row) else None
                        category = row[category_idx].strip() if category_idx is not None and category_idx < len(row) else 'Uncategorized'
                        stock_quantity = self.clean_stock_value(row[stock_idx]) if stock_idx is not None and stock_idx < len(row) else 0
                        cost_price = self.clean_price_value(row[cost_idx]) if cost_idx is not None and cost_idx < len(row) else 0.0
                        
                        # Create product object
                        product_data = {
                            'name': name,
                            'description': description,
                            'price': price,
                            'barcode': barcode,
                            'category': category,
                            'stock_quantity': stock_quantity,
                            'cost_price': cost_price
                        }
                        
                        # Validate
                        is_valid, validation_errors = self.validate_product_data(product_data)
                        if not is_valid:
                            errors.extend([f"Row {row_num}: {error}" for error in validation_errors])
                            continue
                        
                        # Check if product exists (by barcode or name)
                        existing_product = None
                        if barcode:
                            existing_product = self.db_manager.get_product_by_barcode(barcode)
                        
                        if not existing_product:
                            # Check by name
                            all_products = self.db_manager.get_all_products()
                            for prod in all_products:
                                if prod.name.lower().strip() == name.lower().strip():
                                    existing_product = prod
                                    break
                        
                        if existing_product and update_existing:
                            # Update existing product
                            existing_product.name = name
                            existing_product.description = description
                            existing_product.price = price
                            if barcode:
                                existing_product.barcode = barcode
                            existing_product.category = category
                            existing_product.stock_quantity = stock_quantity
                            existing_product.cost_price = cost_price
                            
                            self.db_manager.save_product(existing_product)
                            updated_count += 1
                            
                        elif not existing_product:
                            # Create new product
                            new_product = Product(
                                id=None,
                                name=name,
                                description=description,
                                price=price,
                                barcode=barcode,
                                category=category,
                                stock_quantity=stock_quantity,
                                cost_price=cost_price
                            )
                            
                            self.db_manager.save_product(new_product)
                            imported_count += 1
                        
                        # If product exists but update_existing is False, skip silently
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: Error processing - {str(e)}")
                        continue
                
        except Exception as e:
            errors.append(f"Error reading CSV file: {str(e)}")
        
        return imported_count, updated_count, errors
    
    def export_products_to_csv(self, output_path: str, include_inactive: bool = False) -> bool:
        """Export products to CSV file."""
        try:
            products = self.db_manager.get_all_products()
            
            if not include_inactive:
                products = [p for p in products if p.is_active]
            
            with open(output_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Write headers
                headers = [
                    'ID', 'Name', 'Description', 'Price', 'Barcode', 
                    'Category', 'Stock', 'Cost Price', 'Supplier', 'Active'
                ]
                writer.writerow(headers)
                
                # Write product data
                for product in products:
                    row = [
                        product.id,
                        product.name,
                        product.description,
                        product.price,
                        product.barcode or '',
                        product.category or '',
                        product.stock_quantity,
                        product.cost_price,
                        product.supplier or '',
                        'Yes' if product.is_active else 'No'
                    ]
                    writer.writerow(row)
            
            return True
            
        except Exception as e:
            print(f"Error exporting products: {e}")
            return False

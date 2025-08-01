"""
Database Manager
================

This module handles all database operations for the POS system with optimizations.
"""

import sqlite3
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from functools import lru_cache
import threading
from models.product import Product
from models.sale import Sale, SaleItem
from models.payment import Payment, PaymentMethod, PaymentStatus

class DatabaseManager:
    """Manages database operations for the POS system with optimizations."""
    
    def __init__(self, db_path: str = "pos_database.db"):
        """Initialize database manager with connection pooling."""
        self.db_path = db_path
        self._local = threading.local()  # Thread-local storage for connections
        self._product_cache = {}  # Cache for frequently accessed products
        self._cache_timeout = 300  # 5 minutes cache timeout
        self._last_cache_update = datetime.now()
        self.init_database()
    
    def _get_connection(self):
        """Get a thread-local database connection."""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                self.db_path,
                timeout=30.0,  # 30 second timeout
                check_same_thread=False
            )
            # Enable WAL mode for better concurrency
            self._local.connection.execute("PRAGMA journal_mode=WAL")
            self._local.connection.execute("PRAGMA synchronous=NORMAL")
            self._local.connection.execute("PRAGMA cache_size=10000")
            self._local.connection.execute("PRAGMA temp_store=MEMORY")
        return self._local.connection
    
    def _clear_cache(self):
        """Clear the product cache."""
        self._product_cache.clear()
        self._last_cache_update = datetime.now()
    
    def init_database(self):
        """Initialize database tables with optimizations."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Enable foreign keys for data integrity
            cursor.execute("PRAGMA foreign_keys=ON")
            
            # Create products table with indexes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    barcode TEXT UNIQUE,
                    category TEXT,
                    stock_quantity INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    supplier TEXT,
                    cost_price REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)")
            
            # Add new columns if they don't exist (for existing databases)
            try:
                cursor.execute("ALTER TABLE products ADD COLUMN supplier TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists
                
            try:
                cursor.execute("ALTER TABLE products ADD COLUMN cost_price REAL DEFAULT 0.0")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            # Create sales table with indexes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    subtotal REAL NOT NULL,
                    tax_rate REAL DEFAULT 0.0,
                    tax_amount REAL DEFAULT 0.0,
                    discount REAL DEFAULT 0.0,
                    total REAL NOT NULL,
                    item_count INTEGER DEFAULT 0,
                    notes TEXT,
                    cashier_id TEXT,
                    customer_id TEXT,
                    status TEXT DEFAULT 'completed'
                )
            ''')
            
            # Create indexes for sales
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_timestamp ON sales(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_cashier ON sales(cashier_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_status ON sales(status)")
            
            # Create sale_items table with indexes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sale_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    discount REAL DEFAULT 0.0,
                    subtotal REAL NOT NULL,
                    total REAL NOT NULL,
                    FOREIGN KEY (sale_id) REFERENCES sales (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            # Create indexes for sale_items
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sale_items_sale_id ON sale_items(sale_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sale_items_product_id ON sale_items(product_id)")
            
            # Create payments table with indexes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    method TEXT NOT NULL,
                    amount REAL NOT NULL,
                    status TEXT DEFAULT 'completed',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    transaction_id TEXT,
                    reference_number TEXT,
                    change_amount REAL DEFAULT 0.0,
                    notes TEXT,
                    FOREIGN KEY (sale_id) REFERENCES sales (id)
                )
            ''')
            
            # Create indexes for payments
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_sale_id ON payments(sale_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_method ON payments(method)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_timestamp ON payments(timestamp)")
            
            conn.commit()
            
            # Insert sample products if table is empty
            cursor.execute("SELECT COUNT(*) FROM products")
            if cursor.fetchone()[0] == 0:
                self._insert_sample_products(cursor)
                conn.commit()
            
            # Clear cache after database initialization
            self._clear_cache()
    
    def _insert_sample_products(self, cursor):
        """Insert sample products for demonstration."""
        sample_products = [
            ("Café", "Café noir traditionnel", 15.00, "CAFE001", "Boissons"),
            ("Thé", "Thé vert à la menthe", 12.00, "THE001", "Boissons"),
            ("Croissant", "Croissant au beurre frais", 8.00, "CROI001", "Pâtisserie"),
            ("Pain", "Pain traditionnel marocain", 3.00, "PAIN001", "Boulangerie"),
            ("Jus d'orange", "Jus d'orange frais", 18.00, "JUS001", "Boissons"),
            ("Sandwich", "Sandwich mixte", 25.00, "SAND001", "Snacks"),
            ("Gâteau", "Gâteau au chocolat", 45.00, "GAT001", "Pâtisserie"),
            ("Eau", "Bouteille d'eau 500ml", 5.00, "EAU001", "Boissons")
        ]
        
        cursor.executemany('''
            INSERT INTO products (name, description, price, barcode, category, stock_quantity, is_active)
            VALUES (?, ?, ?, ?, ?, 50, 1)
        ''', sample_products)
    
    def get_all_products(self) -> List[Product]:
        """Get all active products with caching."""
        # Check if cache is still valid
        cache_key = "active_products"
        current_time = datetime.now()
        
        if (cache_key in self._product_cache and 
            (current_time - self._last_cache_update).seconds < self._cache_timeout):
            return self._product_cache[cache_key]
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, description, price, barcode, category, stock_quantity, is_active,
                       supplier, cost_price
                FROM products
                WHERE is_active = 1
                ORDER BY name
            ''')
            
            products = []
            for row in cursor.fetchall():
                product = Product(
                    id=row[0],
                    name=row[1],
                    description=row[2] or "",
                    price=row[3],
                    barcode=row[4],
                    category=row[5],
                    stock_quantity=row[6],
                    is_active=bool(row[7]),
                    supplier=row[8],
                    cost_price=row[9] or 0.0
                )
                products.append(product)
            
            # Cache the results
            self._product_cache[cache_key] = products
            self._last_cache_update = current_time
            
            return products
    
    def get_all_products_for_inventory(self) -> List[Product]:
        """Get all products (including inactive ones) for inventory management."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, description, price, barcode, category, stock_quantity, is_active,
                       supplier, cost_price
                FROM products
                ORDER BY name
            ''')
            
            products = []
            for row in cursor.fetchall():
                product = Product(
                    id=row[0],
                    name=row[1],
                    description=row[2] or "",
                    price=row[3],
                    barcode=row[4],
                    category=row[5],
                    stock_quantity=row[6],
                    is_active=bool(row[7]),
                    supplier=row[8],
                    cost_price=row[9] or 0.0
                )
                products.append(product)
            
            return products
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, description, price, barcode, category, stock_quantity, is_active
                FROM products
                WHERE id = ?
            ''', (product_id,))
            
            row = cursor.fetchone()
            if row:
                return Product(
                    id=row[0],
                    name=row[1],
                    description=row[2] or "",
                    price=row[3],
                    barcode=row[4],
                    category=row[5],
                    stock_quantity=row[6],
                    is_active=bool(row[7])
                )
            return None
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Product]:
        """Get product by barcode."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, description, price, barcode, category, stock_quantity, is_active
                FROM products
                WHERE barcode = ? AND is_active = 1
            ''', (barcode,))
            
            row = cursor.fetchone()
            if row:
                return Product(
                    id=row[0],
                    name=row[1],
                    description=row[2] or "",
                    price=row[3],
                    barcode=row[4],
                    category=row[5],
                    stock_quantity=row[6],
                    is_active=bool(row[7])
                )
            return None
    
    def save_product(self, product: Product) -> int:
        """Save a product to database and clear cache."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if product.id is None:
                # Insert new product
                cursor.execute('''
                    INSERT INTO products (name, description, price, barcode, category, stock_quantity, 
                                        is_active, supplier, cost_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (product.name, product.description, product.price, product.barcode,
                      product.category, product.stock_quantity, product.is_active,
                      product.supplier, product.cost_price))
                
                product.id = cursor.lastrowid
                conn.commit()
                
                # Clear cache after modification
                self._clear_cache()
                return product.id
            else:
                # Update existing product
                cursor.execute('''
                    UPDATE products
                    SET name = ?, description = ?, price = ?, barcode = ?, 
                        category = ?, stock_quantity = ?, is_active = ?,
                        supplier = ?, cost_price = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (product.name, product.description, product.price, product.barcode,
                      product.category, product.stock_quantity, product.is_active,
                      product.supplier, product.cost_price, product.id))
                
                conn.commit()
                
                # Clear cache after modification
                self._clear_cache()
                return product.id
    
    def delete_product(self, product_id: int) -> bool:
        """Permanently delete a product from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # First check if product exists in any sales
            cursor.execute('''
                SELECT COUNT(*) FROM sale_items WHERE product_id = ?
            ''', (product_id,))
            
            sale_count = cursor.fetchone()[0]
            
            if sale_count > 0:
                # If product has been sold, just mark as inactive
                cursor.execute('''
                    UPDATE products
                    SET is_active = 0,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (product_id,))
            else:
                # If product hasn't been sold, permanently delete
                cursor.execute('''
                    DELETE FROM products WHERE id = ?
                ''', (product_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def update_product_stock(self, product_id: int, new_stock: int) -> bool:
        """Update product stock quantity."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE products 
                SET stock_quantity = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_stock, product_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def save_sale(self, sale: Sale) -> int:
        """Save a sale to database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert sale
            cursor.execute('''
                INSERT INTO sales (timestamp, subtotal, tax_rate, tax_amount, discount, 
                                 total, item_count, notes, cashier_id, customer_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (sale.timestamp, sale.subtotal, sale.tax_rate, sale.tax_amount,
                  sale.discount, sale.total, sale.item_count, sale.notes,
                  sale.cashier_id, sale.customer_id))
            
            sale_id = cursor.lastrowid
            sale.id = sale_id
            
            # Insert sale items
            for item in sale.items:
                cursor.execute('''
                    INSERT INTO sale_items (sale_id, product_id, product_name, quantity,
                                          unit_price, discount, subtotal, total)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (sale_id, item.product.id, item.product.name, item.quantity,
                      item.unit_price, item.discount, item.subtotal, item.total))
            
            # Insert payment if exists
            if sale.payment:
                cursor.execute('''
                    INSERT INTO payments (sale_id, method, amount, status, timestamp,
                                        transaction_id, reference_number, change_amount, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (sale_id, sale.payment.method.value, sale.payment.amount,
                      sale.payment.status.value, sale.payment.timestamp,
                      sale.payment.transaction_id, sale.payment.reference_number,
                      sale.payment.change_amount, sale.payment.notes))
            
            conn.commit()
            return sale_id
    
    def get_sales_by_date(self, date: datetime) -> List[Sale]:
        """Get sales for a specific date."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            cursor.execute('''
                SELECT id, timestamp, subtotal, tax_rate, tax_amount, discount,
                       total, item_count, notes, cashier_id, customer_id
                FROM sales
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (start_date, end_date))
            
            sales = []
            for row in cursor.fetchall():
                sale = Sale(
                    id=row[0],
                    timestamp=datetime.fromisoformat(row[1]),
                    tax_rate=row[3],
                    discount=row[5],
                    notes=row[8] or "",
                    cashier_id=row[9],
                    customer_id=row[10]
                )
                
                # Load sale items
                sale.items = self._get_sale_items(cursor, sale.id)
                
                # Load payment
                sale.payment = self._get_sale_payment(cursor, sale.id)
                
                sales.append(sale)
            
            return sales
    
    def get_all_sales(self) -> List[Sale]:
        """Get all sales."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, timestamp, subtotal, tax_rate, tax_amount, discount,
                       total, item_count, notes, cashier_id, customer_id
                FROM sales
                ORDER BY timestamp DESC
                LIMIT 100
            ''')
            
            sales = []
            for row in cursor.fetchall():
                sale = Sale(
                    id=row[0],
                    timestamp=datetime.fromisoformat(row[1]),
                    tax_rate=row[3],
                    discount=row[5],
                    notes=row[8] or "",
                    cashier_id=row[9],
                    customer_id=row[10]
                )
                
                # Load sale items
                sale.items = self._get_sale_items(cursor, sale.id)
                
                # Load payment
                sale.payment = self._get_sale_payment(cursor, sale.id)
                
                sales.append(sale)
            
            return sales
    
    def _get_sale_items(self, cursor, sale_id: int) -> List[SaleItem]:
        """Get sale items for a sale."""
        cursor.execute('''
            SELECT si.product_id, si.product_name, si.quantity, si.unit_price, si.discount,
                   p.description, p.price, p.barcode, p.category, p.stock_quantity
            FROM sale_items si
            LEFT JOIN products p ON si.product_id = p.id
            WHERE si.sale_id = ?
        ''', (sale_id,))
        
        items = []
        for row in cursor.fetchall():
            # Create product object
            product = Product(
                id=row[0],
                name=row[1],
                description=row[5] or "",
                price=row[6] if row[6] is not None else row[3],
                barcode=row[7],
                category=row[8],
                stock_quantity=row[9] if row[9] is not None else 0
            )
            
            # Create sale item
            item = SaleItem(
                product=product,
                quantity=row[2],
                unit_price=row[3],
                discount=row[4]
            )
            items.append(item)
        
        return items
    
    def _get_sale_payment(self, cursor, sale_id: int) -> Optional[Payment]:
        """Get payment for a sale."""
        cursor.execute('''
            SELECT method, amount, status, timestamp, transaction_id,
                   reference_number, change_amount, notes
            FROM payments
            WHERE sale_id = ?
            LIMIT 1
        ''', (sale_id,))
        
        row = cursor.fetchone()
        if row:
            return Payment(
                method=PaymentMethod(row[0]),
                amount=row[1],
                status=PaymentStatus(row[2]),
                timestamp=datetime.fromisoformat(row[3]) if row[3] else None,
                transaction_id=row[4],
                reference_number=row[5],
                change_amount=row[6],
                notes=row[7] or ""
            )
        return None
    
    @lru_cache(maxsize=128)
    def get_daily_sales_summary(self, date_str: str) -> dict:
        """Get daily sales summary with caching (date as string for caching)."""
        date = datetime.fromisoformat(date_str) if isinstance(date_str, str) else date_str
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Optimized query with single pass
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_sales,
                    COALESCE(SUM(total), 0) as total_revenue,
                    COALESCE(SUM(item_count), 0) as total_items,
                    COALESCE(AVG(total), 0) as average_sale
                FROM sales
                WHERE timestamp BETWEEN ? AND ?
                    AND status = 'completed'
            ''', (start_date, end_date))
            
            row = cursor.fetchone()
            return {
                'total_sales': row[0] or 0,
                'total_revenue': row[1] or 0.0,
                'total_items': row[2] or 0,
                'average_sale': row[3] or 0.0,
                'date': date.strftime('%Y-%m-%d')
            }
    
    # Keep the original method for backward compatibility
    def get_daily_sales_summary_original(self, date: datetime) -> dict:
        """Original method wrapper for the cached version."""
        return self.get_daily_sales_summary(date.isoformat())
    
    def get_sales_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Sale]:
        """Get all sales within a date range."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, total, tax_amount, timestamp, cashier_id, register_id, item_count
                FROM sales
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (start_date, end_date))
            
            sales = []
            for row in cursor.fetchall():
                # Get sale items
                cursor.execute('''
                    SELECT si.quantity, si.unit_price, si.total_price, si.discount,
                           p.id, p.name, p.description, p.price, p.barcode, p.category, p.stock_quantity, p.is_active
                    FROM sale_items si
                    JOIN products p ON si.product_id = p.id
                    WHERE si.sale_id = ?
                ''', (row[0],))
                
                items = []
                for item_row in cursor.fetchall():
                    product = Product(
                        id=item_row[4],
                        name=item_row[5],
                        description=item_row[6],
                        price=item_row[7],
                        barcode=item_row[8],
                        category=item_row[9],
                        stock_quantity=item_row[10],
                        is_active=bool(item_row[11])
                    )
                    
                    sale_item = SaleItem(
                        product=product,
                        quantity=item_row[0],
                        unit_price=item_row[1],
                        total=item_row[2],
                        discount=item_row[3]
                    )
                    items.append(sale_item)
                
                # Get payment info
                cursor.execute('''
                    SELECT id, amount, payment_method, change_amount, status, transaction_id
                    FROM payments
                    WHERE sale_id = ?
                ''', (row[0],))
                
                payment_row = cursor.fetchone()
                payment = None
                if payment_row:
                    payment = Payment(
                        id=payment_row[0],
                        amount=payment_row[1],
                        method=PaymentMethod(payment_row[2]),
                        change_amount=payment_row[3],
                        status=PaymentStatus(payment_row[4]),
                        transaction_id=payment_row[5]
                    )
                
                sale = Sale(
                    id=row[0],
                    items=items,
                    total=row[1],
                    tax_amount=row[2],
                    timestamp=datetime.fromisoformat(row[3]) if row[3] else None,
                    cashier_id=row[4],
                    register_id=row[5],
                    payment=payment
                )
                sales.append(sale)
            
            return sales

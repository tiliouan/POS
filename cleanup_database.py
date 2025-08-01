#!/usr/bin/env python3
"""
Database Cleanup Tool for POS System
=====================================

This script helps clean up problematic products like GTT that won't delete properly.
"""

import sqlite3
import os

def check_database():
    """Check the current state of the database."""
    db_path = 'pos_database.db'
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check all products
        cursor.execute('SELECT id, name, is_active FROM products ORDER BY id')
        products = cursor.fetchall()
        
        print("=== Current Products in Database ===")
        for product in products:
            status = "Active" if product[2] else "Inactive"
            print(f"ID: {product[0]}, Name: '{product[1]}', Status: {status}")
        
        # Check for GTT specifically
        cursor.execute('SELECT id, name, is_active FROM products WHERE name LIKE "%GTT%"')
        gtt_products = cursor.fetchall()
        
        if gtt_products:
            print("\n=== GTT Products Found ===")
            for product in gtt_products:
                status = "Active" if product[2] else "Inactive"
                print(f"ID: {product[0]}, Name: '{product[1]}', Status: {status}")
        else:
            print("\n✅ No GTT products found in database")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")

def force_delete_gtt():
    """Force delete any GTT products from the database."""
    db_path = 'pos_database.db'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Delete any GTT products
        cursor.execute('DELETE FROM products WHERE name LIKE "%GTT%"')
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"✅ Deleted {deleted_count} GTT product(s) from database")
        
    except Exception as e:
        print(f"Error deleting GTT products: {e}")

if __name__ == "__main__":
    print("POS Database Cleanup Tool")
    print("=" * 30)
    
    # Check current state
    check_database()
    
    # Force delete GTT products
    print("\nForce deleting GTT products...")
    force_delete_gtt()
    
    # Check final state
    print("\nFinal state after cleanup:")
    check_database()
    
    print("\n✅ Database cleanup completed!")
    print("You can now restart the POS application.")

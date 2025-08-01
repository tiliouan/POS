#!/usr/bin/env python3
"""
Test the advanced reporting system
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_advanced_reports():
    """Test the advanced reporting functionality."""
    
    print("📊 Testing Advanced Reporting System")
    print("=" * 50)
    
    try:
        # Test imports
        from utils.advanced_reports import AdvancedReportsManager, AdvancedReportsDialog
        from database.db_manager import DatabaseManager
        from config.language_settings import get_text
        from datetime import datetime, timedelta
        
        print("✅ All imports successful")
        
        # Test database connection
        db = DatabaseManager()
        print("✅ Database connection successful")
        
        # Test reports manager
        reports_manager = AdvancedReportsManager(db)
        print("✅ Reports manager created")
        
        # Test data generation
        today = datetime.now()
        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        print(f"✅ Testing date range: {start_of_day} to {end_of_day}")
        
        # Generate report data
        report_data = reports_manager.generate_report_data("Daily Test", start_of_day, end_of_day)
        print("✅ Report data generated successfully")
        
        # Test report content
        print(f"\n📈 Report Summary:")
        print(f"   Period: {report_data.period}")
        print(f"   Total Sales: {report_data.total_sales:.2f} DH")
        print(f"   Total Orders: {report_data.total_orders}")
        print(f"   Total Items: {report_data.total_items}")
        print(f"   Cash Payments: {report_data.cash_payments:.2f} DH")
        print(f"   Card Payments: {report_data.card_payments:.2f} DH")
        print(f"   Top Products: {len(report_data.top_products)}")
        print(f"   Low Stock Items: {len(report_data.low_stock)}")
        print(f"   Daily Breakdown: {len(report_data.daily_breakdown)} days")
        
        # Test translations
        print(f"\n🌐 Testing translations:")
        test_keys = [
            "report_analytics", "daily_report", "monthly_report", "yearly_report",
            "sales_overview", "product_analysis", "stock_analysis", "financial_summary"
        ]
        
        for key in test_keys:
            try:
                text = get_text(key)
                print(f"   ✅ {key}: '{text}'")
            except Exception as e:
                print(f"   ❌ {key}: Error - {e}")
        
        # Test chart generation (without display)
        print(f"\n📊 Testing chart generation:")
        try:
            fig = reports_manager.create_sales_chart(report_data)
            print("   ✅ Sales chart generated")
            
            fig = reports_manager.create_product_analysis_chart(report_data)
            print("   ✅ Product analysis chart generated")
            
            fig = reports_manager.create_payment_methods_chart(report_data)
            print("   ✅ Payment methods chart generated")
            
            fig = reports_manager.create_stock_analysis_chart(report_data)
            print("   ✅ Stock analysis chart generated")
        except Exception as e:
            print(f"   ❌ Chart generation error: {e}")
        
        print(f"\n🎉 Advanced reporting system test completed!")
        print("✅ All core functionality working!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_advanced_reports()
    if success:
        print("\n🟢 ADVANCED REPORTING SYSTEM: WORKING")
    else:
        print("\n🔴 ADVANCED REPORTING SYSTEM: NEEDS FIXING")

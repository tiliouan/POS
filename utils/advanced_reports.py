"""
Advanced Analytics and Reporting Module
=======================================

This module provides comprehensive reporting functionality with charts, graphs,
and detailed analytics for sales, products, stock, and financial data.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

from models.sale import Sale
from models.product import Product
from database.db_manager import DatabaseManager
from database.user_manager import user_manager
from config.language_settings import get_text


@dataclass
class ReportData:
    """Data structure for report information."""
    period: str
    start_date: datetime
    end_date: datetime
    total_sales: float
    total_orders: int
    total_items: int
    cash_payments: float
    card_payments: float
    top_products: List[Dict[str, Any]]
    low_stock: List[Dict[str, Any]]
    daily_breakdown: List[Dict[str, Any]]
    user_sales_data: Optional[List[Dict[str, Any]]] = None


class AdvancedReportsManager:
    """Manager for advanced reporting and analytics."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.setup_style()
    
    def setup_style(self):
        """Setup matplotlib and seaborn styling."""
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette("husl")
        
    def get_sales_data(self, start_date: datetime, end_date: datetime) -> List[Sale]:
        """Get sales data for the specified date range."""
        try:
            return self.db_manager.get_sales_by_date_range(start_date, end_date)
        except:
            # Fallback if date range method doesn't exist
            all_sales = self.db_manager.get_all_sales()
            return [sale for sale in all_sales 
                   if sale.timestamp and start_date <= sale.timestamp <= end_date]
    
    def get_products_data(self) -> List[Product]:
        """Get all products data."""
        return self.db_manager.get_all_products()
    
    def generate_report_data(self, period: str, start_date: datetime, end_date: datetime) -> ReportData:
        """Generate comprehensive report data for the specified period."""
        
        # Get sales and products data
        sales = self.get_sales_data(start_date, end_date)
        products = self.get_products_data()
        
        # Calculate basic metrics
        total_sales = sum(sale.total for sale in sales)
        total_orders = len(sales)
        total_items = sum(len(sale.items) for sale in sales)
        
        # Payment method breakdown
        cash_payments = sum(sale.total for sale in sales 
                           if sale.payment and sale.payment.method.value == "cash")
        card_payments = total_sales - cash_payments
        
        # Product analysis
        product_sales = defaultdict(lambda: {"quantity": 0, "revenue": 0})
        for sale in sales:
            for item in sale.items:
                product_sales[item.product.name]["quantity"] += item.quantity
                product_sales[item.product.name]["revenue"] += item.total
        
        # Top products
        top_products = sorted(
            [{"name": name, **data} for name, data in product_sales.items()],
            key=lambda x: x["revenue"],
            reverse=True
        )[:10]
        
        # Low stock products
        low_stock = [
            {
                "name": product.name,
                "current_stock": product.stock_quantity,
                "price": product.price
            }
            for product in products
            if product.stock_quantity <= 10  # Low stock threshold
        ]
        
        # Daily breakdown
        daily_breakdown = self._calculate_daily_breakdown(sales, start_date, end_date)
        
        # Get user sales data
        user_sales_data = self._get_user_sales_data(sales)
        
        return ReportData(
            period=period,
            start_date=start_date,
            end_date=end_date,
            total_sales=total_sales,
            total_orders=total_orders,
            total_items=total_items,
            cash_payments=cash_payments,
            card_payments=card_payments,
            top_products=top_products,
            low_stock=low_stock,
            daily_breakdown=daily_breakdown,
            user_sales_data=user_sales_data
        )
    
    def _calculate_daily_breakdown(self, sales: List[Sale], start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Calculate daily breakdown of sales."""
        daily_data = defaultdict(lambda: {"sales": 0, "orders": 0, "items": 0})
        
        for sale in sales:
            if sale.timestamp:
                date_key = sale.timestamp.strftime("%Y-%m-%d")
                daily_data[date_key]["sales"] += sale.total
                daily_data[date_key]["orders"] += 1
                daily_data[date_key]["items"] += len(sale.items)
        
        # Fill in missing dates with zero values
        current_date = start_date
        result = []
        while current_date <= end_date:
            date_key = current_date.strftime("%Y-%m-%d")
            result.append({
                "date": current_date,
                "date_str": date_key,
                **daily_data[date_key]
            })
            current_date += timedelta(days=1)
        
        return result
    
    def _get_user_sales_data(self, sales: List[Sale]) -> List[Dict[str, Any]]:
        """Get user sales data from sales."""
        user_sales = defaultdict(lambda: {"sales": 0, "orders": 0, "revenue": 0})
        
        for sale in sales:
            if hasattr(sale, 'cashier_id') and sale.cashier_id:
                user_id = sale.cashier_id
                user_sales[user_id]["sales"] += 1
                user_sales[user_id]["orders"] += 1
                user_sales[user_id]["revenue"] += sale.total
        
        # Get user names from user manager
        users = user_manager.get_all_users()
        user_names = {user.id: user.name for user in users}
        
        result = []
        for user_id, data in user_sales.items():
            result.append({
                "user_id": user_id,
                "user_name": user_names.get(user_id, f"User {user_id}"),
                "total_sales": data["sales"],
                "total_orders": data["orders"],
                "total_revenue": data["revenue"],
                "average_sale": data["revenue"] / data["sales"] if data["sales"] > 0 else 0
            })
        
        return sorted(result, key=lambda x: x["total_revenue"], reverse=True)
    
    def create_sales_chart(self, report_data: ReportData, chart_type: str = "line") -> plt.Figure:
        """Create sales chart."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        dates = [day["date"] for day in report_data.daily_breakdown]
        sales = [day["sales"] for day in report_data.daily_breakdown]
        
        if chart_type == "line":
            ax.plot(dates, sales, marker='o', linewidth=2, markersize=6)
        elif chart_type == "bar":
            ax.bar(dates, sales, alpha=0.7)
        
        ax.set_title(f'{get_text("sales_overview")} - {report_data.period}', fontsize=16, fontweight='bold')
        ax.set_xlabel(get_text("date_range"))
        ax.set_ylabel(f'{get_text("revenue")} (DH)')
        
        # Format x-axis
        if len(dates) > 10:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//10)))
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
    
    def create_product_analysis_chart(self, report_data: ReportData) -> plt.Figure:
        """Create product analysis chart."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Top products by revenue
        if report_data.top_products:
            top_5 = report_data.top_products[:5]
            names = [p["name"][:15] + "..." if len(p["name"]) > 15 else p["name"] for p in top_5]
            revenues = [p["revenue"] for p in top_5]
            
            ax1.barh(names, revenues, color=sns.color_palette("viridis", len(names)))
            ax1.set_title(f'{get_text("top_products")} ({get_text("revenue")})', fontweight='bold')
            ax1.set_xlabel(f'{get_text("revenue")} (DH)')
            
            # Top products by quantity
            quantities = [p["quantity"] for p in top_5]
            ax2.barh(names, quantities, color=sns.color_palette("plasma", len(names)))
            ax2.set_title(f'{get_text("top_products")} ({get_text("units_sold")})', fontweight='bold')
            ax2.set_xlabel(get_text("units_sold"))
        
        plt.tight_layout()
        return fig
    
    def create_payment_methods_chart(self, report_data: ReportData) -> plt.Figure:
        """Create payment methods pie chart."""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        if report_data.cash_payments > 0 or report_data.card_payments > 0:
            sizes = [report_data.cash_payments, report_data.card_payments]
            labels = [get_text("cash_payments"), get_text("card_payments")]
            colors = ['#ff9999', '#66b3ff']
            
            # Only include non-zero values
            non_zero_data = [(label, size, color) for label, size, color in zip(labels, sizes, colors) if size > 0]
            if non_zero_data:
                labels, sizes, colors = zip(*non_zero_data)
                
                wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                ax.set_title(get_text("payment_methods"), fontsize=16, fontweight='bold')
                
                # Enhance text
                for text in texts:
                    text.set_fontsize(12)
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontsize(11)
                    autotext.set_fontweight('bold')
        else:
            ax.text(0.5, 0.5, 'No payment data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(get_text("payment_methods"), fontsize=16, fontweight='bold')
        
        return fig
    
    def create_user_sales_chart(self, report_data: ReportData) -> plt.Figure:
        """Create user sales performance chart."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        if report_data.user_sales_data and len(report_data.user_sales_data) > 0:
            users = report_data.user_sales_data[:10]  # Top 10 users
            
            # Sales by user (revenue)
            names = [u["user_name"][:15] + "..." if len(u["user_name"]) > 15 else u["user_name"] for u in users]
            revenues = [u["total_revenue"] for u in users]
            
            ax1.barh(names, revenues, color=sns.color_palette("viridis", len(names)))
            ax1.set_title(f'{get_text("user_sales_report")} - {get_text("revenue")}', fontweight='bold')
            ax1.set_xlabel(f'{get_text("revenue")} (DH)')
            
            # Sales by user (count)
            orders = [u["total_orders"] for u in users]
            ax2.barh(names, orders, color=sns.color_palette("plasma", len(names)))
            ax2.set_title(f'{get_text("user_sales_report")} - {get_text("total_orders")}', fontweight='bold')
            ax2.set_xlabel(get_text("total_orders"))
        else:
            ax1.text(0.5, 0.5, "No user data available", 
                    ha='center', va='center', transform=ax1.transAxes)
            ax2.text(0.5, 0.5, "No user data available", 
                    ha='center', va='center', transform=ax2.transAxes)
            ax1.set_title(f'{get_text("user_sales_report")} - {get_text("revenue")}', fontweight='bold')
            ax2.set_title(f'{get_text("user_sales_report")} - {get_text("total_orders")}', fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def create_stock_analysis_chart(self, report_data: ReportData) -> plt.Figure:
        """Create stock analysis chart."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if report_data.low_stock:
            products = report_data.low_stock[:10]  # Top 10 low stock items
            names = [p["name"][:20] + "..." if len(p["name"]) > 20 else p["name"] for p in products]
            stocks = [p["current_stock"] for p in products]
            
            colors = ['red' if stock <= 5 else 'orange' if stock <= 10 else 'yellow' for stock in stocks]
            
            bars = ax.bar(names, stocks, color=colors, alpha=0.7)
            ax.set_title(get_text("low_stock"), fontsize=16, fontweight='bold')
            ax.set_xlabel(get_text("product_name"))
            ax.set_ylabel(get_text("current_stock"))
            
            # Add value labels on bars
            for bar, stock in zip(bars, stocks):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{stock}', ha='center', va='bottom', fontweight='bold')
            
            plt.xticks(rotation=45, ha='right')
        else:
            ax.text(0.5, 0.5, 'All products have sufficient stock', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(get_text("low_stock"), fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def export_report_to_csv(self, report_data: ReportData, filename: str):
        """Export report data to CSV file."""
        try:
            # Create summary data
            summary_data = {
                'Metric': [
                    get_text("total_sales"),
                    get_text("total_orders"),
                    get_text("units_sold"),
                    get_text("cash_payments"),
                    get_text("card_payments"),
                    get_text("average_order")
                ],
                'Value': [
                    f"{report_data.total_sales:.2f} DH",
                    str(report_data.total_orders),
                    str(report_data.total_items),
                    f"{report_data.cash_payments:.2f} DH",
                    f"{report_data.card_payments:.2f} DH",
                    f"{(report_data.total_sales / max(1, report_data.total_orders)):.2f} DH"
                ]
            }
            
            # Save to CSV
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_csv(filename, index=False, encoding='utf-8')
            
            messagebox.showinfo("Export", f"Report exported successfully to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")


class AdvancedReportsDialog:
    """Advanced reports dialog with comprehensive analytics."""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        self.parent = parent
        self.db_manager = db_manager
        self.reports_manager = AdvancedReportsManager(db_manager)
        
        self.window = tk.Toplevel(parent)
        self.window.title(get_text("report_analytics"))
        self.window.geometry("1200x800")
        self.window.transient(parent)
        
        # Center the window
        self.window.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.current_report_data = None
        self.setup_ui()
        
        # Load default daily report
        self.load_daily_report()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Control panel
        self.create_control_panel(main_frame)
        
        # Content area with notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, pady=(10, 0))
        
        # Create tabs
        self.create_overview_tab()
        self.create_charts_tab()
        self.create_details_tab()
        self.create_user_activities_tab()
    
    def create_control_panel(self, parent):
        """Create control panel with filters and options."""
        control_frame = ttk.LabelFrame(parent, text=get_text("time_period"), padding="10")
        control_frame.pack(fill="x", pady=(0, 10))
        
        # Period selection buttons
        period_frame = ttk.Frame(control_frame)
        period_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(period_frame, text=get_text("daily_report"), 
                  command=self.load_daily_report, width=15).pack(side="left", padx=(0, 5))
        ttk.Button(period_frame, text=get_text("monthly_report"), 
                  command=self.load_monthly_report, width=15).pack(side="left", padx=(0, 5))
        ttk.Button(period_frame, text=get_text("yearly_report"), 
                  command=self.load_yearly_report, width=15).pack(side="left", padx=(0, 5))
        
        # Date range selection
        date_frame = ttk.Frame(control_frame)
        date_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(date_frame, text=get_text("from_date")).pack(side="left", padx=(0, 5))
        self.from_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.from_date_entry = ttk.Entry(date_frame, textvariable=self.from_date_var, width=12)
        self.from_date_entry.pack(side="left", padx=(0, 10))
        
        ttk.Label(date_frame, text=get_text("to_date")).pack(side="left", padx=(0, 5))
        self.to_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.to_date_entry = ttk.Entry(date_frame, textvariable=self.to_date_var, width=12)
        self.to_date_entry.pack(side="left", padx=(0, 10))
        
        ttk.Button(date_frame, text=get_text("apply_filter"), 
                  command=self.load_custom_report, width=12).pack(side="left", padx=(0, 5))
        ttk.Button(date_frame, text=get_text("export_report"), 
                  command=self.export_report, width=12).pack(side="left")
    
    def create_overview_tab(self):
        """Create overview tab with key metrics."""
        self.overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.overview_frame, text=get_text("financial_summary"))
        
        # Scrollable frame for overview
        canvas = tk.Canvas(self.overview_frame)
        scrollbar = ttk.Scrollbar(self.overview_frame, orient="vertical", command=canvas.yview)
        self.overview_scrollable = ttk.Frame(canvas)
        
        self.overview_scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.overview_scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_charts_tab(self):
        """Create charts tab."""
        self.charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_frame, text=get_text("generate_chart"))
        
        # Chart selection
        chart_control = ttk.Frame(self.charts_frame)
        chart_control.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(chart_control, text=get_text("sales_overview"), 
                  command=lambda: self.show_chart("sales")).pack(side="left", padx=(0, 5))
        ttk.Button(chart_control, text=get_text("product_analysis"), 
                  command=lambda: self.show_chart("products")).pack(side="left", padx=(0, 5))
        ttk.Button(chart_control, text=get_text("payment_methods"), 
                  command=lambda: self.show_chart("payments")).pack(side="left", padx=(0, 5))
        ttk.Button(chart_control, text=get_text("stock_analysis"), 
                  command=lambda: self.show_chart("stock")).pack(side="left", padx=(0, 5))
        ttk.Button(chart_control, text=get_text("user_sales_report"), 
                  command=lambda: self.show_chart("users")).pack(side="left", padx=(0, 5))
        
        # Chart display area
        self.chart_frame = ttk.Frame(self.charts_frame)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def create_details_tab(self):
        """Create details tab with tables."""
        self.details_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.details_frame, text=get_text("product_analysis"))
        
        # Create treeview for detailed data
        columns = ("Product", "Units Sold", "Revenue", "Stock")
        self.details_tree = ttk.Treeview(self.details_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.details_tree.heading(col, text=col)
            self.details_tree.column(col, width=120)
        
        # Scrollbar for details
        details_scrollbar = ttk.Scrollbar(self.details_frame, orient="vertical", command=self.details_tree.yview)
        self.details_tree.configure(yscrollcommand=details_scrollbar.set)
        
        self.details_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        details_scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
    
    def load_daily_report(self):
        """Load daily report."""
        today = datetime.now()
        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        self.current_report_data = self.reports_manager.generate_report_data(
            get_text("daily_report"), start_of_day, end_of_day
        )
        self.update_overview()
        self.update_details()
        self.update_user_activities()
    
    def load_monthly_report(self):
        """Load monthly report."""
        today = datetime.now()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate end of month
        if today.month == 12:
            end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        end_of_month = end_of_month.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        self.current_report_data = self.reports_manager.generate_report_data(
            get_text("monthly_report"), start_of_month, end_of_month
        )
        self.update_overview()
        self.update_details()
        self.update_user_activities()
    
    def load_yearly_report(self):
        """Load yearly report."""
        today = datetime.now()
        start_of_year = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_year = today.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        
        self.current_report_data = self.reports_manager.generate_report_data(
            get_text("yearly_report"), start_of_year, end_of_year
        )
        self.update_overview()
        self.update_details()
        self.update_user_activities()
    
    def load_custom_report(self):
        """Load custom date range report."""
        try:
            start_date = datetime.strptime(self.from_date_var.get(), "%Y-%m-%d")
            end_date = datetime.strptime(self.to_date_var.get(), "%Y-%m-%d")
            
            if start_date > end_date:
                messagebox.showerror("Error", "Start date cannot be after end date")
                return
            
            # Adjust times
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            period_text = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            
            self.current_report_data = self.reports_manager.generate_report_data(
                period_text, start_date, end_date
            )
            self.update_overview()
            self.update_details()
            self.update_user_activities()
            
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
    
    def update_overview(self):
        """Update overview tab with current report data."""
        # Clear existing content
        for widget in self.overview_scrollable.winfo_children():
            widget.destroy()
        
        if not self.current_report_data:
            return
        
        data = self.current_report_data
        
        # Title
        title_label = ttk.Label(self.overview_scrollable, 
                               text=f"{get_text('report_analytics')} - {data.period}",
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(10, 20))
        
        # Create metrics cards
        metrics = [
            (get_text("total_sales"), f"{data.total_sales:.2f} DH", "#2E8B57"),
            (get_text("total_orders"), str(data.total_orders), "#4169E1"),
            (get_text("units_sold"), str(data.total_items), "#FF6347"),
            (get_text("average_order"), f"{(data.total_sales / max(1, data.total_orders)):.2f} DH", "#9932CC"),
            (get_text("cash_payments"), f"{data.cash_payments:.2f} DH", "#FFD700"),
            (get_text("card_payments"), f"{data.card_payments:.2f} DH", "#20B2AA")
        ]
        
        # Create grid of metric cards
        metrics_frame = ttk.Frame(self.overview_scrollable)
        metrics_frame.pack(fill="x", padx=20, pady=10)
        
        for i, (label, value, color) in enumerate(metrics):
            row = i // 3
            col = i % 3
            
            card = tk.Frame(metrics_frame, bg=color, relief="raised", bd=2)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            # Configure grid weights
            metrics_frame.grid_columnconfigure(col, weight=1)
            
            value_label = tk.Label(card, text=value, font=("Arial", 16, "bold"), 
                                  bg=color, fg="white")
            value_label.pack(pady=(15, 5))
            
            label_widget = tk.Label(card, text=label, font=("Arial", 10), 
                                   bg=color, fg="white")
            label_widget.pack(pady=(0, 15))
        
        # Top products section
        if data.top_products:
            top_products_frame = ttk.LabelFrame(self.overview_scrollable, 
                                              text=get_text("top_products"), padding="10")
            top_products_frame.pack(fill="x", padx=20, pady=20)
            
            for i, product in enumerate(data.top_products[:5]):
                product_frame = ttk.Frame(top_products_frame)
                product_frame.pack(fill="x", pady=2)
                
                rank_label = ttk.Label(product_frame, text=f"{i+1}.", 
                                      font=("Arial", 10, "bold"), width=3)
                rank_label.pack(side="left")
                
                name_label = ttk.Label(product_frame, text=product["name"], width=30)
                name_label.pack(side="left", padx=(0, 10))
                
                revenue_label = ttk.Label(product_frame, 
                                         text=f'{product["revenue"]:.2f} DH',
                                         font=("Arial", 10, "bold"))
                revenue_label.pack(side="right")
                
                qty_label = ttk.Label(product_frame, 
                                     text=f'({product["quantity"]} units)')
                qty_label.pack(side="right", padx=(0, 10))
        
        # Low stock warning
        if data.low_stock:
            low_stock_frame = ttk.LabelFrame(self.overview_scrollable, 
                                           text=get_text("low_stock"), padding="10")
            low_stock_frame.pack(fill="x", padx=20, pady=20)
            
            for product in data.low_stock[:5]:
                product_frame = ttk.Frame(low_stock_frame)
                product_frame.pack(fill="x", pady=2)
                
                warning_label = ttk.Label(product_frame, text="⚠️", 
                                         foreground="red", width=3)
                warning_label.pack(side="left")
                
                name_label = ttk.Label(product_frame, text=product["name"], width=30)
                name_label.pack(side="left", padx=(0, 10))
                
                stock_label = ttk.Label(product_frame, 
                                       text=f'Stock: {product["current_stock"]}',
                                       foreground="red" if product["current_stock"] <= 5 else "orange")
                stock_label.pack(side="right")
    
    def update_details(self):
        """Update details tab with product information."""
        # Clear existing items
        for item in self.details_tree.get_children():
            self.details_tree.delete(item)
        
        if not self.current_report_data:
            return
        
        # Add product details
        products = self.reports_manager.get_products_data()
        product_sales = {p["name"]: p for p in self.current_report_data.top_products}
        
        for product in products:
            sales_data = product_sales.get(product.name, {"quantity": 0, "revenue": 0})
            
            self.details_tree.insert("", "end", values=(
                product.name,
                sales_data["quantity"],
                f'{sales_data["revenue"]:.2f} DH',
                product.stock_quantity
            ))
    
    def show_chart(self, chart_type: str):
        """Show selected chart type."""
        # Clear existing chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        if not self.current_report_data:
            ttk.Label(self.chart_frame, text="No data available").pack(expand=True)
            return
        
        try:
            # Generate chart based on type
            if chart_type == "sales":
                fig = self.reports_manager.create_sales_chart(self.current_report_data)
            elif chart_type == "products":
                fig = self.reports_manager.create_product_analysis_chart(self.current_report_data)
            elif chart_type == "payments":
                fig = self.reports_manager.create_payment_methods_chart(self.current_report_data)
            elif chart_type == "stock":
                fig = self.reports_manager.create_stock_analysis_chart(self.current_report_data)
            elif chart_type == "users":
                fig = self.reports_manager.create_user_sales_chart(self.current_report_data)
            else:
                return
            
            # Embed chart in tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            error_label = ttk.Label(self.chart_frame, text=f"Error generating chart: {str(e)}")
            error_label.pack(expand=True)
    
    def export_report(self):
        """Export current report to CSV."""
        if not self.current_report_data:
            messagebox.showwarning("Warning", "No report data to export")
            return
        
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Report"
        )
        
        if filename:
            self.reports_manager.export_report_to_csv(self.current_report_data, filename)
    
    def create_user_activities_tab(self):
        """Create user activities and performance tab."""
        user_frame = ttk.Frame(self.notebook)
        self.notebook.add(user_frame, text=get_text("user_activities"))
        
        # Split into two panels
        paned_window = ttk.PanedWindow(user_frame, orient="horizontal")
        paned_window.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel - User sales summary
        left_frame = ttk.LabelFrame(paned_window, text=get_text("user_sales_report"), padding="10")
        paned_window.add(left_frame, weight=1)
        
        # User sales tree
        user_columns = ("name", "total_sales", "total_revenue", "avg_sale")
        self.user_tree = ttk.Treeview(left_frame, columns=user_columns, show="tree headings", height=12)
        
        self.user_tree.heading("#0", text="User ID")
        self.user_tree.heading("name", text="Name")
        self.user_tree.heading("total_sales", text="Total Sales")
        self.user_tree.heading("total_revenue", text="Revenue (DH)")
        self.user_tree.heading("avg_sale", text="Avg Sale (DH)")
        
        self.user_tree.column("#0", width=80)
        self.user_tree.column("name", width=150)
        self.user_tree.column("total_sales", width=100)
        self.user_tree.column("total_revenue", width=120)
        self.user_tree.column("avg_sale", width=120)
        
        # Add scrollbar
        user_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=user_scrollbar.set)
        
        self.user_tree.pack(side="left", fill="both", expand=True)
        user_scrollbar.pack(side="right", fill="y")
        
        # Right panel - User activities log
        right_frame = ttk.LabelFrame(paned_window, text=get_text("user_operations"), padding="10")
        paned_window.add(right_frame, weight=1)
        
        # Activities tree
        activity_columns = ("timestamp", "activity", "details")
        self.activity_tree = ttk.Treeview(right_frame, columns=activity_columns, show="tree headings", height=12)
        
        self.activity_tree.heading("#0", text="User")
        self.activity_tree.heading("timestamp", text="Time")
        self.activity_tree.heading("activity", text="Activity")
        self.activity_tree.heading("details", text="Details")
        
        self.activity_tree.column("#0", width=100)
        self.activity_tree.column("timestamp", width=130)
        self.activity_tree.column("activity", width=120)
        self.activity_tree.column("details", width=200)
        
        # Add scrollbar
        activity_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.activity_tree.yview)
        self.activity_tree.configure(yscrollcommand=activity_scrollbar.set)
        
        self.activity_tree.pack(side="left", fill="both", expand=True)
        activity_scrollbar.pack(side="right", fill="y")
        
        # Update with initial data
        self.update_user_activities()
    
    def update_user_activities(self):
        """Update user activities display."""
        # Clear existing data
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        
        if not self.current_report_data:
            return
        
        # Update user sales summary
        if self.current_report_data.user_sales_data:
            for user_data in self.current_report_data.user_sales_data:
                self.user_tree.insert(
                    "",
                    "end",
                    text=str(user_data["user_id"]),
                    values=(
                        user_data["user_name"],
                        user_data["total_sales"],
                        f"{user_data['total_revenue']:.2f}",
                        f"{user_data['average_sale']:.2f}"
                    )
                )
        
        # Update user activities
        try:
            activities = user_manager.get_user_activities(
                start_date=self.current_report_data.start_date,
                end_date=self.current_report_data.end_date
            )
            
            for activity in activities[:50]:  # Show last 50 activities
                user_name = activity.details.split('\n')[-1].replace('User: ', '') if activity.details else "Unknown"
                
                self.activity_tree.insert(
                    "",
                    "end",
                    text=user_name.split(' (')[0] if ' (' in user_name else user_name,
                    values=(
                        activity.timestamp.strftime("%Y-%m-%d %H:%M") if activity.timestamp else "",
                        activity.activity_type.replace('_', ' ').title(),
                        activity.description[:50] + "..." if len(activity.description) > 50 else activity.description
                    )
                )
        except Exception as e:
            print(f"Error loading user activities: {e}")

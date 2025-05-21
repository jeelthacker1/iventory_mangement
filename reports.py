from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QDateEdit, QFileDialog,
                             QTabWidget, QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from charts import ChartWidget

class ReportsWidget(QWidget):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel('Reports and Analytics')
        header.setFont(QFont('Arial', 24))
        header.setProperty('heading', 'true')  # For stylesheet
        layout.addWidget(header)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Date range selection
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        
        # Report type selection
        self.report_type = QComboBox()
        self.report_type.addItems(['Sales Report', 'Inventory Report', 'Profit Analysis'])
        
        # Export buttons
        self.export_csv_btn = QPushButton('Export CSV')
        self.export_csv_btn.clicked.connect(self.export_csv)
        
        self.export_pdf_btn = QPushButton('Export PDF')
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        
        self.generate_btn = QPushButton('Generate Report')
        self.generate_btn.clicked.connect(self.generate_report)
        
        # Add widgets to controls layout
        controls_layout.addWidget(QLabel('Start Date:'))
        controls_layout.addWidget(self.start_date)
        controls_layout.addWidget(QLabel('End Date:'))
        controls_layout.addWidget(self.end_date)
        controls_layout.addWidget(QLabel('Report Type:'))
        controls_layout.addWidget(self.report_type)
        controls_layout.addWidget(self.generate_btn)
        controls_layout.addWidget(self.export_csv_btn)
        controls_layout.addWidget(self.export_pdf_btn)
        
        layout.addLayout(controls_layout)
        
        # Tab widget for different views
        self.tabs = QTabWidget()
        
        # Create tabs
        self.chart_tab = QWidget()
        self.table_tab = QWidget()
        
        self.setup_chart_tab()
        self.setup_table_tab()
        
        self.tabs.addTab(self.chart_tab, "Charts")
        self.tabs.addTab(self.table_tab, "Data Table")
        
        layout.addWidget(self.tabs)
    
    def setup_chart_tab(self):
        layout = QVBoxLayout(self.chart_tab)
        
        # Create chart widget
        self.chart_widget = ChartWidget(self.db)
        layout.addWidget(self.chart_widget)
    
    def setup_table_tab(self):
        layout = QVBoxLayout(self.table_tab)
        
        # Create table for report data
        self.report_table = QTableWidget()
        layout.addWidget(self.report_table)
    
    def generate_report(self):
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        report_type = self.report_type.currentText()
        
        # Validate date range
        if start_date > end_date:
            QMessageBox.warning(self, "Invalid Date Range", 
                               "Start date must be before end date.")
            return
        
        # Convert to datetime for database query
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        try:
            if report_type == 'Sales Report':
                self.generate_sales_report(start_datetime, end_datetime)
            elif report_type == 'Inventory Report':
                self.generate_inventory_report()
            elif report_type == 'Profit Analysis':
                self.generate_profit_report(start_datetime, end_datetime)
                
            # Switch to table tab to show results
            self.tabs.setCurrentIndex(1)
            
        except Exception as e:
            QMessageBox.critical(self, "Report Generation Error", 
                                f"An error occurred: {str(e)}")
    
    def generate_sales_report(self, start_date, end_date):
        # Get sales data from database
        sales = self.db.get_sales_report(start_date, end_date)
        
        # Prepare table
        self.report_table.clear()
        self.report_table.setRowCount(len(sales))
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels([
            'Sale ID', 'Date', 'Customer', 'Items', 'Total Amount'
        ])
        
        # Fill table with data
        for row, sale in enumerate(sales):
            self.report_table.setItem(row, 0, QTableWidgetItem(str(sale.id)))
            self.report_table.setItem(row, 1, QTableWidgetItem(sale.sale_date.strftime('%Y-%m-%d %H:%M')))
            
            customer_name = sale.customer.name if sale.customer else 'Walk-in Customer'
            self.report_table.setItem(row, 2, QTableWidgetItem(customer_name))
            
            # Count items
            item_count = len(sale.items) if hasattr(sale, 'items') else 0
            self.report_table.setItem(row, 3, QTableWidgetItem(str(item_count)))
            
            self.report_table.setItem(row, 4, QTableWidgetItem(f"₹{sale.total_amount:.2f}"))
        
        # Resize columns to content
        self.report_table.resizeColumnsToContents()
        
        # Update chart
        self.chart_widget.chart_type_combo.setCurrentText('Sales Trend')
        self.chart_widget.update_chart()
    
    def generate_inventory_report(self):
        # Get inventory data
        products = self.db.get_all_products()
        
        # Prepare table
        self.report_table.clear()
        self.report_table.setRowCount(len(products))
        self.report_table.setColumnCount(6)
        self.report_table.setHorizontalHeaderLabels([
            'Product ID', 'Name', 'Category', 'Quantity', 'Value', 'Status'
        ])
        
        # Fill table with data
        for row, product in enumerate(products):
            self.report_table.setItem(row, 0, QTableWidgetItem(str(product.id)))
            self.report_table.setItem(row, 1, QTableWidgetItem(product.name))
            self.report_table.setItem(row, 2, QTableWidgetItem(product.category or 'Uncategorized'))
            self.report_table.setItem(row, 3, QTableWidgetItem(str(product.quantity)))
            
            # Calculate inventory value
            value = product.quantity * product.purchase_price
            self.report_table.setItem(row, 4, QTableWidgetItem(f"₹{value:.2f}"))
            
            # Stock status
            if product.quantity <= 0:
                status = "Out of Stock"
            elif product.quantity <= product.reorder_threshold:
                status = "Low Stock"
            else:
                status = "In Stock"
            self.report_table.setItem(row, 5, QTableWidgetItem(status))
        
        # Resize columns to content
        self.report_table.resizeColumnsToContents()
        
        # Update chart
        self.chart_widget.chart_type_combo.setCurrentText('Product Categories')
        self.chart_widget.update_chart()
    
    def generate_profit_report(self, start_date, end_date):
        # Get sales data
        sales = self.db.get_sales_report(start_date, end_date)
        
        # Dictionary to store product profits
        product_profits = {}
        
        # Calculate profits for each product
        for sale in sales:
            for item in sale.items:
                product = item.product
                profit = (item.unit_price - product.purchase_price) * item.quantity
                
                if product.id in product_profits:
                    product_profits[product.id]['quantity'] += item.quantity
                    product_profits[product.id]['revenue'] += item.subtotal
                    product_profits[product.id]['profit'] += profit
                else:
                    product_profits[product.id] = {
                        'name': product.name,
                        'quantity': item.quantity,
                        'revenue': item.subtotal,
                        'cost': product.purchase_price * item.quantity,
                        'profit': profit
                    }
        
        # Prepare table
        self.report_table.clear()
        self.report_table.setRowCount(len(product_profits))
        self.report_table.setColumnCount(6)
        self.report_table.setHorizontalHeaderLabels([
            'Product', 'Quantity Sold', 'Revenue', 'Cost', 'Profit', 'Margin %'
        ])
        
        # Fill table with data
        for row, (product_id, data) in enumerate(product_profits.items()):
            self.report_table.setItem(row, 0, QTableWidgetItem(data['name']))
            self.report_table.setItem(row, 1, QTableWidgetItem(str(data['quantity'])))
            self.report_table.setItem(row, 2, QTableWidgetItem(f"${data['revenue']:.2f}"))
            self.report_table.setItem(row, 3, QTableWidgetItem(f"${data['cost']:.2f}"))
            self.report_table.setItem(row, 4, QTableWidgetItem(f"${data['profit']:.2f}"))
            
            # Calculate margin percentage
            if data['revenue'] > 0:
                margin = (data['profit'] / data['revenue']) * 100
                self.report_table.setItem(row, 5, QTableWidgetItem(f"{margin:.2f}%"))
            else:
                self.report_table.setItem(row, 5, QTableWidgetItem("N/A"))
        
        # Resize columns to content
        self.report_table.resizeColumnsToContents()
        
        # Update chart
        self.chart_widget.chart_type_combo.setCurrentText('Profit Margin')
        self.chart_widget.update_chart()
    
    def export_csv(self):
        # Get file path from user
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Report", "", "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            # Convert table data to pandas DataFrame
            rows = self.report_table.rowCount()
            cols = self.report_table.columnCount()
            headers = [self.report_table.horizontalHeaderItem(col).text() for col in range(cols)]
            
            data = []
            for row in range(rows):
                row_data = []
                for col in range(cols):
                    item = self.report_table.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)
            
            df = pd.DataFrame(data, columns=headers)
            
            # Export to CSV
            df.to_csv(file_path, index=False)
            
            QMessageBox.information(self, "Export Successful", 
                                   f"Report exported to {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", 
                                f"Failed to export report: {str(e)}")
    
    def export_pdf(self):
        # Get file path from user
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Report", "", "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return
        
        try:
            # Create printer
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)
            
            # Show print dialog
            dialog = QPrintDialog(printer, self)
            if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                # TODO: Implement PDF generation
                # For now, we'll use matplotlib to create a simple PDF
                self.generate_pdf_with_matplotlib(file_path)
                
                QMessageBox.information(self, "Export Successful", 
                                      f"Report exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", 
                                f"Failed to export report: {str(e)}")
    
    def generate_pdf_with_matplotlib(self, file_path):
        # Convert table data to pandas DataFrame
        rows = self.report_table.rowCount()
        cols = self.report_table.columnCount()
        headers = [self.report_table.horizontalHeaderItem(col).text() for col in range(cols)]
        
        data = []
        for row in range(rows):
            row_data = []
            for col in range(cols):
                item = self.report_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        
        df = pd.DataFrame(data, columns=headers)
        
        # Create a figure with a table
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('tight')
        ax.axis('off')
        
        # Add title
        report_type = self.report_type.currentText()
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        plt.suptitle(f"{report_type}: {start_date} to {end_date}", fontsize=16)
        
        # Create table
        table = ax.table(
            cellText=df.values,
            colLabels=df.columns,
            cellLoc='center',
            loc='center'
        )
        
        # Adjust table style
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
        
        # Save to PDF
        plt.savefig(file_path, bbox_inches='tight')
        plt.close()
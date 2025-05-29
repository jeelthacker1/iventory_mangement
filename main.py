import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QTableWidget, QTableWidgetItem, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtGui import QFont, QPainter, QPixmap
from database import DatabaseManager
from qr_handler import QRHandler
from datetime import datetime, timedelta
from reports import ReportsWidget
from charts import ChartWidget
from repair_ui import RepairTaskWidget
from todo_ui import TodoWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.qr_handler = QRHandler()
        self.load_stylesheet()
        self.setup_ui()
    
    def load_stylesheet(self):
        # Load and apply the QSS stylesheet
        try:
            style_path = os.path.join(os.path.dirname(__file__), 'style.qss')
            with open(style_path, 'r') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Could not load stylesheet: {e}")
    
    def setup_ui(self):
        self.setWindowTitle('Shop Inventory Management')
        self.setGeometry(100, 100, 1200, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create sidebar for navigation
        sidebar = QWidget()
        sidebar.setMaximumWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Create navigation buttons
        nav_buttons = [
            ('Dashboard', self.show_dashboard),
            ('Inventory', self.show_inventory),
            ('Sales', self.show_sales),
            ('Customers', self.show_customers),
            ('Reports', self.show_reports),
            ('Low Stock', self.show_low_stock),
            ('Repair Tasks', self.show_repair_tasks),
            ('Todo Tasks', self.show_todo_tasks)
        ]
        
        for text, callback in nav_buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(50)
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        layout.addWidget(sidebar)
        
        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Create pages
        self.create_dashboard_page()
        self.create_inventory_page()
        self.create_sales_page()
        self.create_customers_page()
        self.create_reports_page()
        self.create_low_stock_page()
        self.create_repair_tasks_page()
        self.create_todo_tasks_page()
        
        # Show dashboard by default
        self.show_dashboard()
    
    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QLabel('Dashboard')
        header.setFont(QFont('Arial', 24))
        header.setProperty('heading', 'true')  # For stylesheet
        layout.addWidget(header)
        
        # Quick stats
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        
        # Add stat boxes
        stat_boxes = [
            ('Total Products', self.get_total_products),
            ('Low Stock Items', self.get_low_stock_count),
            ('Today\'s Sales', self.get_today_sales),
            ('Monthly Revenue', self.get_monthly_revenue)
        ]
        
        for title, callback in stat_boxes:
            box = QWidget()
            box.setProperty('class', 'stat-box')
            box_layout = QVBoxLayout(box)
            
            title_label = QLabel(title)
            value_label = QLabel(str(callback()))
            value_label.setFont(QFont('Arial', 20))
            
            box_layout.addWidget(title_label)
            box_layout.addWidget(value_label)
            stats_layout.addWidget(box)
        
        layout.addWidget(stats_widget)
        
        # Add a chart to the dashboard
        chart_label = QLabel('Sales Overview')
        chart_label.setFont(QFont('Arial', 16))
        layout.addWidget(chart_label)
        
        # Add chart widget
        chart_widget = ChartWidget(self.db)
        chart_widget.setMaximumHeight(400)  # Limit height
        layout.addWidget(chart_widget)
        
        self.stacked_widget.addWidget(page)
    
    def create_inventory_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QLabel('Inventory Management')
        header.setFont(QFont('Arial', 24))
        layout.addWidget(header)
        
        # Add buttons for inventory actions
        actions = QHBoxLayout()
        add_btn = QPushButton('Add Product')
        add_btn.clicked.connect(self.add_product)
        edit_btn = QPushButton('Edit Product')
        edit_btn.clicked.connect(self.edit_product)
        delete_btn = QPushButton('Delete Product')
        delete_btn.clicked.connect(self.delete_product)
        print_qr_btn = QPushButton('Print QR Code')
        print_qr_btn.clicked.connect(self.print_inventory_qr_code)
        
        actions.addWidget(add_btn)
        actions.addWidget(edit_btn)
        actions.addWidget(delete_btn)
        actions.addWidget(print_qr_btn)
        actions.addStretch()
        
        layout.addLayout(actions)
        
        # Location filter
        location_layout = QHBoxLayout()
        location_label = QLabel('Filter by Location:')
        self.location_filter = QComboBox()
        self.location_filter.addItems(['All', 'store', 'warehouse', 'assembly'])
        self.location_filter.currentTextChanged.connect(self.update_inventory_table)
        location_layout.addWidget(location_label)
        location_layout.addWidget(self.location_filter)
        location_layout.addStretch()
        layout.addLayout(location_layout)
        
        # Add inventory table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(8)
        self.inventory_table.setHorizontalHeaderLabels([
            'ID', 'Name', 'Category', 'Quantity', 'Purchase Price',
            'Selling Price', 'Location', 'Supplier'
        ])
        layout.addWidget(self.inventory_table)
        
        self.stacked_widget.addWidget(page)
        self.update_inventory_table()
    
    def create_sales_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QLabel('Sales Processing')
        header.setFont(QFont('Arial', 24))
        layout.addWidget(header)
        
        # Add scan button
        scan_btn = QPushButton('Scan QR Code')
        scan_btn.clicked.connect(self.start_scanning)
        layout.addWidget(scan_btn)
        
        # Add sales table
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels([
            'Product', 'Quantity', 'Unit Price', 'Subtotal', 'Actions'
        ])
        layout.addWidget(self.sales_table)
        
        # Add total amount display
        total_layout = QHBoxLayout()
        total_label = QLabel('Total Amount:')
        self.total_amount_label = QLabel('₹0.00')
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_amount_label)
        total_layout.addStretch()
        
        # Add print buttons
        print_layout = QHBoxLayout()
        print_qr_btn = QPushButton('Print QR Code')
        print_qr_btn.clicked.connect(self.print_qr_code)
        print_bill_btn = QPushButton('Print Bill')
        print_bill_btn.clicked.connect(self.print_bill)
        print_layout.addWidget(print_qr_btn)
        print_layout.addWidget(print_bill_btn)
        
        layout.addLayout(total_layout)
        layout.addLayout(print_layout)
        
        self.stacked_widget.addWidget(page)
    
    def print_bill(self):
        if self.sales_table.rowCount() == 0:
            QMessageBox.warning(self, "Empty Cart", "Please add items to cart before printing bill.")
            return
        
        # Get customer information
        from dialogs import CustomerDialog
        customer_dialog = CustomerDialog(self)
        if customer_dialog.exec():
            # Get customer data
            customer_name = customer_dialog.name_input.text()
            customer_phone = customer_dialog.phone_input.text()
            customer_email = customer_dialog.email_input.text()
            customer_address = customer_dialog.address_input.toPlainText()
            
            # Save customer to database if needed
            customer_data = {
                'name': customer_name,
                'phone': customer_phone,
                'email': customer_email,
                'address': customer_address,
                'loyalty_points': 0
            }
            customer = self.db.add_customer(customer_data)
            
            try:
                # Setup printer
                printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                dialog = QPrintDialog(printer, self)
                
                if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                    # Create painter for drawing
                    painter = QPainter(printer)
                    
                    # Set font for bill
                    font = QFont('Arial', 10)
                    painter.setFont(font)
                    
                    # Starting position
                    x = 100
                    y = 100
                    
                    # Print header
                    painter.drawText(x, y, "Shop Inventory Management System")
                    y += 30
                    painter.drawText(x, y, "Sales Receipt")
                    y += 30
                    painter.drawText(x, y, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                    y += 30
                    
                    # Print customer information
                    painter.drawText(x, y, f"Customer: {customer_name}")
                    y += 20
                    painter.drawText(x, y, f"Phone: {customer_phone}")
                    y += 20
                    painter.drawText(x, y, f"Email: {customer_email}")
                    y += 30
                    
                    # Print column headers
                    col_width = 150
                    painter.drawText(x, y, "Product")
                    painter.drawText(x + col_width, y, "Quantity")
                    painter.drawText(x + col_width * 2, y, "Unit Price")
                    painter.drawText(x + col_width * 3, y, "Subtotal")
                    y += 30
                    
                    # Print items and collect sale items data
                    total_amount = 0
                    items_data = []
                    
                    for row in range(self.sales_table.rowCount()):
                        product = self.sales_table.item(row, 0).text()
                        product_id = self.sales_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                        serial_number = self.sales_table.item(row, 0).data(Qt.ItemDataRole.UserRole + 1)
                        quantity = int(self.sales_table.item(row, 1).text())
                        unit_price = self.sales_table.item(row, 2).text()
                        subtotal = self.sales_table.item(row, 3).text()
                        
                        painter.drawText(x, y, f"{product} (SN: {serial_number})")
                        painter.drawText(x + col_width, y, str(quantity))
                        painter.drawText(x + col_width * 2, y, unit_price)
                        painter.drawText(x + col_width * 3, y, subtotal)
                        
                        # Extract amount from subtotal (remove currency symbol)
                        amount = float(subtotal.replace('₹', '').strip())
                        total_amount += amount
                        
                        # Add to items data for database
                        items_data.append({
                            'product_id': product_id,
                            'quantity': quantity,
                            'unit_price': float(unit_price.replace('₹', '').strip()),
                            'subtotal': amount
                        })
                        
                        y += 30
                    
                    # Print total
                    y += 30
                    painter.drawText(x + col_width * 2, y, "Total Amount:")
                    painter.drawText(x + col_width * 3, y, f"₹{total_amount:.2f}")
                    
                    # End painting
                    painter.end()
                    
                    # Save sale to database
                    sale_data = {
                        'customer_id': customer.id,
                        'total_amount': total_amount,
                        'tax_amount': total_amount * 0.18,  # Assuming 18% tax
                        'sale_date': datetime.now()
                    }
                    
                    self.db.add_sale(sale_data, items_data)
                    
                    # Clear sales table
                    self.sales_table.setRowCount(0)
                    self.update_sales_total()
                    
                    QMessageBox.information(self, "Success", "Bill printed successfully and sale recorded!")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to print bill: {str(e)}")
        else:
            QMessageBox.information(self, "Cancelled", "Bill printing cancelled.")
    
    def create_customers_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QLabel('Customer Management')
        header.setFont(QFont('Arial', 24))
        layout.addWidget(header)
        
        # Add customer actions
        actions = QHBoxLayout()
        add_btn = QPushButton('Add Customer')
        add_btn.clicked.connect(self.add_customer)
        edit_btn = QPushButton('Edit Customer')
        edit_btn.clicked.connect(self.edit_customer)
        
        actions.addWidget(add_btn)
        actions.addWidget(edit_btn)
        actions.addStretch()
        
        layout.addLayout(actions)
        
        # Add customers table
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(5)
        self.customers_table.setHorizontalHeaderLabels([
            'ID', 'Name', 'Phone', 'Email', 'Loyalty Points'
        ])
        layout.addWidget(self.customers_table)
        
        self.stacked_widget.addWidget(page)
    
    def create_reports_page(self):
        # Create reports widget with integrated charts
        reports_widget = ReportsWidget(self.db)
        self.stacked_widget.addWidget(reports_widget)
    
    def create_low_stock_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Header
        header = QLabel('Low Stock Items')
        header.setFont(QFont('Arial', 24))
        layout.addWidget(header)
        
        # Add low stock table
        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(5)
        self.low_stock_table.setHorizontalHeaderLabels([
            'Product', 'Current Quantity', 'Threshold', 'Supplier', 'Actions'
        ])
        layout.addWidget(self.low_stock_table)
        
        self.stacked_widget.addWidget(page)
        self.update_low_stock_table()
    
    # Navigation methods
    def show_dashboard(self):
        self.stacked_widget.setCurrentIndex(0)
    
    def show_inventory(self):
        self.stacked_widget.setCurrentIndex(1)
        self.update_inventory_table()
    
    def show_sales(self):
        self.stacked_widget.setCurrentIndex(2)
    
    def show_customers(self):
        self.stacked_widget.setCurrentIndex(3)
    
    def show_reports(self):
        self.stacked_widget.setCurrentIndex(4)
    
    def show_low_stock(self):
        self.stacked_widget.setCurrentIndex(5)
    
    def show_repair_tasks(self):
        self.stacked_widget.setCurrentIndex(6)
    
    def show_todo_tasks(self):
        self.stacked_widget.setCurrentIndex(7)
    
    def create_repair_tasks_page(self):
        repair_widget = RepairTaskWidget(self.db)
        self.stacked_widget.addWidget(repair_widget)
        self.update_low_stock_table()
    
    def create_todo_tasks_page(self):
        todo_widget = TodoWidget()
        self.stacked_widget.addWidget(todo_widget)
    
    # Utility methods
    def get_total_products(self):
        return len(self.db.get_all_products())
    
    def get_low_stock_count(self):
        return len(self.db.get_low_stock_products())
    
    def get_today_sales(self):
        today = datetime.now().date()
        sales = self.db.get_sales_report(today, today + timedelta(days=1))
        return sum(sale.total_amount for sale in sales)
    
    def get_monthly_revenue(self):
        start_date = datetime.now().replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1)
        sales = self.db.get_sales_report(start_date, end_date)
        return sum(sale.total_amount for sale in sales)
    
    def update_inventory_table(self):
        products = self.db.get_all_products()
        
        # Filter by location if needed
        location_filter = self.location_filter.currentText() if hasattr(self, 'location_filter') else 'All'
        if location_filter != 'All':
            products = [p for p in products if hasattr(p, 'location') and p.location == location_filter]
        
        self.inventory_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # Basic product information
            self.inventory_table.setItem(row, 0, QTableWidgetItem(str(product.id)))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(product.name))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(product.category or 'Uncategorized'))
            
            # Quantity information
            store_qty = getattr(product, 'store_quantity', 0)
            warehouse_qty = getattr(product, 'warehouse_quantity', 0)
            total_qty = store_qty + warehouse_qty
            
            # Format quantity display
            qty_text = f"{total_qty} (S:{store_qty}, W:{warehouse_qty})"
            qty_item = QTableWidgetItem(qty_text)
            
            # Highlight low stock
            if total_qty <= getattr(product, 'reorder_threshold', 5):
                qty_item.setBackground(QColor(255, 200, 200))  # Light red for low stock
            
            self.inventory_table.setItem(row, 3, qty_item)
            
            # Price information
            self.inventory_table.setItem(row, 4, QTableWidgetItem(f"₹{product.purchase_price:.2f}"))
            self.inventory_table.setItem(row, 5, QTableWidgetItem(f"₹{product.selling_price:.2f}"))
            
            # Location and supplier info
            location = getattr(product, 'location', 'store')
            self.inventory_table.setItem(row, 6, QTableWidgetItem(location))
            self.inventory_table.setItem(row, 7, QTableWidgetItem(getattr(product, 'supplier_info', '')))
    
    def update_low_stock_table(self):
        products = self.db.get_low_stock_products()
        self.low_stock_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.low_stock_table.setItem(row, 0, QTableWidgetItem(product.name))
            total_qty = product.store_quantity + product.warehouse_quantity
            self.low_stock_table.setItem(row, 1, QTableWidgetItem(f"{total_qty} (S:{product.store_quantity}, W:{product.warehouse_quantity})"))
            self.low_stock_table.setItem(row, 2, QTableWidgetItem(str(product.reorder_threshold)))
            self.low_stock_table.setItem(row, 3, QTableWidgetItem(product.supplier_info))
            
            reorder_btn = QPushButton('Reorder')
            self.low_stock_table.setCellWidget(row, 4, reorder_btn)
    
    # Event handlers
    def add_product(self):
        from dialogs import ProductDialog
        dialog = ProductDialog(self)
        if dialog.exec():
            self.update_inventory_table()
            QMessageBox.information(self, "Success", "Product added successfully!")
            # Update dashboard stats
            self.show_dashboard()
            self.show_inventory()
    
    def edit_product(self):
        selected_items = self.inventory_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a product to edit.")
            return
        
        # Get the product ID from the first column of the selected row
        row = selected_items[0].row()
        product_id = int(self.inventory_table.item(row, 0).text())
        product = self.db.get_product(product_id)
        
        if product:
            from dialogs import ProductDialog
            dialog = ProductDialog(self, product)
            if dialog.exec():
                self.update_inventory_table()
                QMessageBox.information(self, "Success", "Product updated successfully!")
                # Update dashboard stats and low stock if needed
                self.update_low_stock_table()
        else:
            QMessageBox.warning(self, "Error", "Could not find the selected product.")
    
    def delete_product(self):
        selected_items = self.inventory_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a product to delete.")
            return
        
        # Get the product ID from the first column of the selected row
        row = selected_items[0].row()
        product_id = int(self.inventory_table.item(row, 0).text())
        product_name = self.inventory_table.item(row, 1).text()
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete '{product_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            if self.db.delete_product(product_id):
                self.update_inventory_table()
                QMessageBox.information(self, "Success", "Product deleted successfully!")
                # Update dashboard stats and low stock if needed
                self.update_low_stock_table()
                self.show_dashboard()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete the product.")
                
    def print_inventory_qr_code(self):
        # Get selected product from inventory table
        selected_items = self.inventory_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a product to print QR code.")
            return
        
        # Get product ID from the selected row
        row = selected_items[0].row()
        product_id = int(self.inventory_table.item(row, 0).text())
        product_name = self.inventory_table.item(row, 1).text()
        
        # Ask for quantity
        from PyQt6.QtWidgets import QInputDialog
        quantity, ok = QInputDialog.getInt(self, "Quantity", "Enter quantity for QR code:", 1, 1, 100, 1)
        
        if not ok:
            return
        
        try:
            # Generate QR code with product information
            qr_path, serial_number = self.qr_handler.generate_qr_code(
                product_id,
                product_name,
                quantity
            )
            
            if qr_path:
                # Update product with serial number
                product = self.db.get_product(product_id)
                if product:
                    self.db.update_product(product_id, {
                        'serial_number': serial_number
                    })
                
                QMessageBox.information(self, "Success", f"QR code generated successfully!\nSerial Number: {serial_number}")
                
                # Print the QR code
                printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                dialog = QPrintDialog(printer, self)
                if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                    # Load the QR code image
                    qr_pixmap = QPixmap(qr_path)
                    # Scale to fit printer page
                    scaled_pixmap = qr_pixmap.scaled(printer.pageRect().size(),
                                                    Qt.AspectRatioMode.KeepAspectRatio,
                                                    Qt.TransformationMode.SmoothTransformation)
                    # Create painter and draw
                    painter = QPainter(printer)
                    painter.drawPixmap(0, 0, scaled_pixmap)
                    painter.end()
            else:
                QMessageBox.warning(self, "Error", "Failed to generate QR code.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate QR code: {str(e)}")

    def print_qr_code(self):
        # Get selected product from sales table
        selected_items = self.sales_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a product to print QR code.")
            return
        
        # Get product ID and quantity from the selected row
        row = selected_items[0].row()
        product_id = self.sales_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        product_name = self.sales_table.item(row, 0).text()
        quantity = int(self.sales_table.item(row, 1).text())
        
        try:
            # Generate QR code with product information
            qr_path, serial_number = self.qr_handler.generate_qr_code(
                product_id,
                product_name,
                quantity
            )
            
            if qr_path:
                QMessageBox.information(self, "Success", f"QR code generated successfully!\nSerial Number: {serial_number}")
                # Print the QR code
                printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                dialog = QPrintDialog(printer, self)
                if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                    # Load the QR code image
                    qr_pixmap = QPixmap(qr_path)
                    # Scale to fit printer page
                    scaled_pixmap = qr_pixmap.scaled(printer.pageRect().size(),
                                                    Qt.AspectRatioMode.KeepAspectRatio,
                                                    Qt.TransformationMode.SmoothTransformation)
                    # Create painter and draw
                    painter = QPainter(printer)
                    painter.drawPixmap(0, 0, scaled_pixmap)
                    painter.end()
            else:
                QMessageBox.warning(self, "Error", "Failed to generate QR code.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate QR code: {str(e)}")

    
    def start_scanning(self):
        try:
            # Start the camera
            self.qr_handler.start_camera()
            QMessageBox.information(self, "QR Scanner", "Camera started. Scan a product QR code or press 'q' to quit.")
            
            # Scan QR code
            qr_data = self.qr_handler.scan_qr_code()
            
            # Stop the camera
            self.qr_handler.stop_camera()
            
            if qr_data:
                # Parse QR data (format: product_id|product_name|quantity|serial_number)
                try:
                    qr_parts = qr_data.split('|')
                    product_id = int(qr_parts[0])
                    scan_quantity = int(qr_parts[2]) if len(qr_parts) > 2 else 1
                    serial_number = qr_parts[3] if len(qr_parts) > 3 else None
                    
                    product = self.db.get_product(product_id)
                    
                    if product:
                        if product.store_quantity >= scan_quantity:
                            # Add product to sales table
                            row = self.sales_table.rowCount()
                            self.sales_table.insertRow(row)
                            
                            # Product name with ID as user data
                            name_item = QTableWidgetItem(product.name)
                            name_item.setData(Qt.ItemDataRole.UserRole, product.id)
                            # Store serial number as additional user data if available
                            if serial_number:
                                name_item.setData(Qt.ItemDataRole.UserRole + 1, serial_number)
                            self.sales_table.setItem(row, 0, name_item)
                            
                            # Quantity
                            self.sales_table.setItem(row, 1, QTableWidgetItem(str(scan_quantity)))
                            
                            # Unit price
                            self.sales_table.setItem(row, 2, QTableWidgetItem(f"₹{product.selling_price:.2f}"))
                            
                            # Subtotal
                            subtotal = scan_quantity * product.selling_price
                            self.sales_table.setItem(row, 3, QTableWidgetItem(f"₹{subtotal:.2f}"))
                            
                            # Remove button
                            remove_btn = QPushButton("Remove")
                            remove_btn.clicked.connect(lambda checked, r=row: self.remove_sale_item(r))
                            self.sales_table.setCellWidget(row, 4, remove_btn)
                            
                            # Update total
                            self.update_sales_total()
                            
                            # Update inventory - reduce store quantity
                            product.store_quantity -= scan_quantity
                            self.db.update_product(product.id, {'store_quantity': product.store_quantity})
                            self.update_inventory_table()
                            
                            QMessageBox.information(self, "Success", f"Added {product.name} to cart.\nSerial Number: {serial_number}")
                        else:
                            QMessageBox.warning(self, "Insufficient Stock", 
                                              f"Not enough stock available. Current store stock: {product.store_quantity}")
                    else:
                        QMessageBox.warning(self, "Product Not Found", "Could not find the scanned product.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to process QR code: {str(e)}")
            else:
                QMessageBox.information(self, "Cancelled", "QR code scanning was cancelled.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to scan QR code: {str(e)}")
            if self.qr_handler.camera:
                self.qr_handler.stop_camera()
    
    def add_to_sale(self, product, quantity=1):
        """Add a product to the current sale"""
        # Find if product already in sale table
        for row in range(self.sales_table.rowCount()):
            if self.sales_table.item(row, 0).data(Qt.ItemDataRole.UserRole) == product.id:
                # Update quantity
                current_qty = int(self.sales_table.item(row, 1).text())
                new_qty = current_qty + quantity
                self.sales_table.item(row, 1).setText(str(new_qty))
                
                # Update subtotal
                unit_price = product.selling_price
                subtotal = unit_price * new_qty
                self.sales_table.item(row, 3).setText(f"${subtotal:.2f}")
                return
        
        # Add new row if product not in table
        row = self.sales_table.rowCount()
        self.sales_table.setRowCount(row + 1)
        
        # Product name with ID as user data
        name_item = QTableWidgetItem(product.name)
        name_item.setData(Qt.ItemDataRole.UserRole, product.id)
        
        # Quantity
        qty_item = QTableWidgetItem(str(quantity))
        
        # Unit price
        price_item = QTableWidgetItem(f"₹{product.selling_price:.2f}")
        
        # Subtotal
        subtotal = product.selling_price * quantity
        subtotal_item = QTableWidgetItem(f"₹{subtotal:.2f}")
        
        # Add items to row
        self.sales_table.setItem(row, 0, name_item)
        self.sales_table.setItem(row, 1, qty_item)
        self.sales_table.setItem(row, 2, price_item)
        self.sales_table.setItem(row, 3, subtotal_item)
        
        # Add remove button
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(lambda: self.remove_from_sale(row))
        self.sales_table.setCellWidget(row, 4, remove_btn)
    
    def remove_from_sale(self, row):
        """Remove a product from the current sale"""
        self.sales_table.removeRow(row)
    
    def add_customer(self):
        from dialogs import CustomerDialog
        dialog = CustomerDialog(self)
        if dialog.exec():
            self.update_customers_table()
            QMessageBox.information(self, "Success", "Customer added successfully!")
    
    def edit_customer(self):
        selected_items = self.customers_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a customer to edit.")
            return
        
        # Get the customer ID from the first column of the selected row
        row = selected_items[0].row()
        customer_id = int(self.customers_table.item(row, 0).text())
        customer = self.db.get_customer(customer_id)
        
        if customer:
            from dialogs import CustomerDialog
            dialog = CustomerDialog(self, customer)
            if dialog.exec():
                self.update_customers_table()
                QMessageBox.information(self, "Success", "Customer updated successfully!")
        else:
            QMessageBox.warning(self, "Error", "Could not find the selected customer.")
            
    def update_customers_table(self):
        customers = self.db.get_all_customers()
        self.customers_table.setRowCount(len(customers))
        
        for row, customer in enumerate(customers):
            self.customers_table.setItem(row, 0, QTableWidgetItem(str(customer.id)))
            self.customers_table.setItem(row, 1, QTableWidgetItem(customer.name))
            self.customers_table.setItem(row, 2, QTableWidgetItem(customer.phone))
            self.customers_table.setItem(row, 3, QTableWidgetItem(customer.email))
            self.customers_table.setItem(row, 4, QTableWidgetItem(str(customer.loyalty_points)))

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
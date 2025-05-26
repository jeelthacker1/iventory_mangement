from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QSpinBox, QDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from datetime import datetime
from inventory_manager import InventoryManager

class InventoryDashboardWidget(QWidget):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.inventory_manager = InventoryManager(db_manager)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel('Inventory Dashboard')
        header.setFont(QFont('Arial', 24))
        header.setProperty('heading', 'true')
        layout.addWidget(header)
        
        # Critical Lists Section
        lists_layout = QHBoxLayout()
        
        # Assembly Needed List
        assembly_group = QWidget()
        assembly_layout = QVBoxLayout(assembly_group)
        assembly_header = QLabel('Assembly Needed')
        assembly_header.setFont(QFont('Arial', 14))
        self.assembly_table = QTableWidget()
        self.assembly_table.setColumnCount(4)
        self.assembly_table.setHorizontalHeaderLabels([
            'Product', 'Store Qty', 'Warehouse Qty', 'Actions'
        ])
        assembly_layout.addWidget(assembly_header)
        assembly_layout.addWidget(self.assembly_table)
        
        # Reorder Needed List
        reorder_group = QWidget()
        reorder_layout = QVBoxLayout(reorder_group)
        reorder_header = QLabel('Reorder Needed')
        reorder_header.setFont(QFont('Arial', 14))
        self.reorder_table = QTableWidget()
        self.reorder_table.setColumnCount(4)
        self.reorder_table.setHorizontalHeaderLabels([
            'Product', 'Total Qty', 'Last Ordered', 'Actions'
        ])
        reorder_layout.addWidget(reorder_header)
        reorder_layout.addWidget(self.reorder_table)
        
        lists_layout.addWidget(assembly_group)
        lists_layout.addWidget(reorder_group)
        layout.addLayout(lists_layout)
        
        # Full Inventory Section
        inventory_header = QLabel('Full Inventory')
        inventory_header.setFont(QFont('Arial', 14))
        layout.addWidget(inventory_header)
        
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(4)
        self.inventory_table.setHorizontalHeaderLabels([
            'Product', 'Store Quantity', 'Warehouse Quantity', 'Total'
        ])
        layout.addWidget(self.inventory_table)
        
        # Refresh button
        refresh_btn = QPushButton('Refresh Dashboard')
        refresh_btn.clicked.connect(self.refresh_dashboard)
        layout.addWidget(refresh_btn)
        
        self.refresh_dashboard()
    
    def refresh_dashboard(self):
        # Update Assembly Needed list
        assembly_products = self.inventory_manager.get_assembly_suggestions()
        self.assembly_table.setRowCount(len(assembly_products))
        for i, product in enumerate(assembly_products):
            self.assembly_table.setItem(i, 0, QTableWidgetItem(product.name))
            self.assembly_table.setItem(i, 1, QTableWidgetItem(str(product.store_quantity)))
            self.assembly_table.setItem(i, 2, QTableWidgetItem(str(product.warehouse_quantity)))
            
            assemble_btn = QPushButton('Assemble')
            assemble_btn.clicked.connect(lambda _, p=product: self.show_assembly_dialog(p))
            self.assembly_table.setCellWidget(i, 3, assemble_btn)
        
        # Update Reorder Needed list
        reorder_products = self.inventory_manager.get_reorder_suggestions()
        self.reorder_table.setRowCount(len(reorder_products))
        for i, product in enumerate(reorder_products):
            self.reorder_table.setItem(i, 0, QTableWidgetItem(product.name))
            total_qty = product.store_quantity + product.warehouse_quantity
            self.reorder_table.setItem(i, 1, QTableWidgetItem(str(total_qty)))
            
            last_ordered = product.last_ordered_at or 'Never'
            if isinstance(last_ordered, datetime):
                last_ordered = last_ordered.strftime('%Y-%m-%d')
            self.reorder_table.setItem(i, 2, QTableWidgetItem(str(last_ordered)))
            
            order_btn = QPushButton('Mark Ordered')
            order_btn.clicked.connect(lambda _, p=product: self.mark_product_ordered(p))
            self.reorder_table.setCellWidget(i, 3, order_btn)
        
        # Update Full Inventory table
        inventory = self.inventory_manager.get_inventory_breakdown()
        self.inventory_table.setRowCount(len(inventory))
        for i, item in enumerate(inventory):
            self.inventory_table.setItem(i, 0, QTableWidgetItem(item['name']))
            self.inventory_table.setItem(i, 1, QTableWidgetItem(str(item['store_quantity'])))
            self.inventory_table.setItem(i, 2, QTableWidgetItem(str(item['warehouse_quantity'])))
            self.inventory_table.setItem(i, 3, QTableWidgetItem(str(item['total_quantity'])))
            
            # Highlight low quantities
            if item['store_quantity'] < self.inventory_manager.MIN_STORE_THRESHOLD:
                self.highlight_row(self.inventory_table, i, QColor(255, 200, 200))
            elif item['total_quantity'] < self.inventory_manager.MIN_TOTAL_THRESHOLD:
                self.highlight_row(self.inventory_table, i, QColor(255, 255, 200))
        
        # Resize columns to content
        self.assembly_table.resizeColumnsToContents()
        self.reorder_table.resizeColumnsToContents()
        self.inventory_table.resizeColumnsToContents()
    
    def show_assembly_dialog(self, product):
        dialog = AssemblyDialog(product, self)
        if dialog.exec():
            try:
                quantity = dialog.quantity.value()
                self.inventory_manager.assemble_products(product.id, quantity)
                self.refresh_dashboard()
                QMessageBox.information(self, 'Success',
                    f'Successfully assembled {quantity} units of {product.name}')
            except ValueError as e:
                QMessageBox.warning(self, 'Error', str(e))
    
    def mark_product_ordered(self, product):
        try:
            self.inventory_manager.mark_product_ordered(product.id)
            self.refresh_dashboard()
            QMessageBox.information(self, 'Success',
                f'Successfully marked {product.name} as ordered')
        except ValueError as e:
            QMessageBox.warning(self, 'Error', str(e))
    
    def highlight_row(self, table, row, color):
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if item:
                item.setBackground(color)

class AssemblyDialog(QDialog):
    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.product = product
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle('Assemble Products')
        layout = QVBoxLayout(self)
        
        # Product info
        layout.addWidget(QLabel(f'Product: {self.product.name}'))
        layout.addWidget(QLabel(f'Available in Warehouse: {self.product.warehouse_quantity}'))
        
        # Quantity selection
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel('Quantity to Assemble:'))
        self.quantity = QSpinBox()
        self.quantity.setMinimum(1)
        self.quantity.setMaximum(self.product.warehouse_quantity)
        quantity_layout.addWidget(self.quantity)
        layout.addLayout(quantity_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        assemble_btn = QPushButton('Assemble')
        assemble_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(assemble_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
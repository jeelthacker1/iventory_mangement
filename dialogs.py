from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
                             QPushButton, QTextEdit, QMessageBox, QCheckBox,
                             QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from database import DatabaseManager
from enhanced_product_manager import EnhancedProductManager
from todo_manager import TodoManager

class ProductDialog(QDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.enhanced_manager = EnhancedProductManager(self.db)
        self.todo_manager = TodoManager(self.db)
        self.product = product
        self.is_editing = product is not None
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle('Add Product' if not self.product else 'Edit Product')
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Product Name
        name_layout = QHBoxLayout()
        name_label = QLabel('Name:')
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Description
        desc_layout = QVBoxLayout()
        desc_label = QLabel('Description:')
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(100)
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_input)
        layout.addLayout(desc_layout)
        
        # Category
        cat_layout = QHBoxLayout()
        cat_label = QLabel('Category:')
        self.cat_input = QComboBox()
        self.cat_input.setEditable(True)
        self.cat_input.addItems(['Tricycle', 'Accessories', 'Spare Parts', 'Other'])
        cat_layout.addWidget(cat_label)
        cat_layout.addWidget(self.cat_input)
        layout.addLayout(cat_layout)
        
        # For editing: Additional quantity section
        if self.is_editing:
            add_qty_group = QGroupBox('Add Additional Quantity')
            add_qty_layout = QGridLayout(add_qty_group)
            
            add_store_label = QLabel('Add to Store:')
            self.add_store_qty_input = QSpinBox()
            self.add_store_qty_input.setMaximum(9999)
            add_qty_layout.addWidget(add_store_label, 0, 0)
            add_qty_layout.addWidget(self.add_store_qty_input, 0, 1)
            
            add_warehouse_label = QLabel('Add to Warehouse:')
            self.add_warehouse_qty_input = QSpinBox()
            self.add_warehouse_qty_input.setMaximum(9999)
            add_qty_layout.addWidget(add_warehouse_label, 0, 2)
            add_qty_layout.addWidget(self.add_warehouse_qty_input, 0, 3)
            
            layout.addWidget(add_qty_group)
        
        # Prices
        prices_layout = QHBoxLayout()
        
        purchase_label = QLabel('Purchase Price:')
        self.purchase_input = QDoubleSpinBox()
        self.purchase_input.setMaximum(999999.99)
        self.purchase_input.setPrefix('₹')
        
        selling_label = QLabel('Selling Price:')
        self.selling_input = QDoubleSpinBox()
        self.selling_input.setMaximum(999999.99)
        self.selling_input.setPrefix('₹')
        
        prices_layout.addWidget(purchase_label)
        prices_layout.addWidget(self.purchase_input)
        prices_layout.addWidget(selling_label)
        prices_layout.addWidget(self.selling_input)
        layout.addLayout(prices_layout)
        
        # Quantity Section
        qty_group = QGroupBox('Inventory Quantities')
        qty_layout = QGridLayout(qty_group)
        
        # Store Quantity
        store_qty_label = QLabel('Store Quantity:')
        self.store_qty_input = QSpinBox()
        self.store_qty_input.setMaximum(9999)
        qty_layout.addWidget(store_qty_label, 0, 0)
        qty_layout.addWidget(self.store_qty_input, 0, 1)
        
        # Warehouse Quantity
        warehouse_qty_label = QLabel('Warehouse Quantity:')
        self.warehouse_qty_input = QSpinBox()
        self.warehouse_qty_input.setMaximum(9999)
        qty_layout.addWidget(warehouse_qty_label, 0, 2)
        qty_layout.addWidget(self.warehouse_qty_input, 0, 3)
        
        # Reorder Threshold
        threshold_label = QLabel('Reorder Threshold:')
        self.threshold_input = QSpinBox()
        self.threshold_input.setMaximum(999)
        self.threshold_input.setValue(5)
        qty_layout.addWidget(threshold_label, 1, 0)
        qty_layout.addWidget(self.threshold_input, 1, 1)
        
        # QR Code Generation Options
        self.generate_qr_checkbox = QCheckBox('Generate QR Codes & Barcodes')
        self.generate_qr_checkbox.setChecked(True)
        qty_layout.addWidget(self.generate_qr_checkbox, 1, 2, 1, 2)
        
        layout.addWidget(qty_group)
        
        # Supplier Info
        supplier_layout = QVBoxLayout()
        supplier_label = QLabel('Supplier Information:')
        self.supplier_input = QTextEdit()
        self.supplier_input.setMaximumHeight(100)
        supplier_layout.addWidget(supplier_label)
        supplier_layout.addWidget(self.supplier_input)
        layout.addLayout(supplier_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.save_product)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        # Fill data if editing
        if self.product:
            self.name_input.setText(self.product.name)
            self.desc_input.setText(self.product.description)
            self.cat_input.setCurrentText(self.product.category)
            self.purchase_input.setValue(self.product.purchase_price)
            self.selling_input.setValue(self.product.selling_price)
            self.store_qty_input.setValue(self.product.store_quantity)
            self.warehouse_qty_input.setValue(self.product.warehouse_quantity)
            self.threshold_input.setValue(self.product.reorder_threshold)
            self.supplier_input.setText(self.product.supplier_info or '')
            
            # For editing, disable the main quantity inputs and show current values as read-only
            self.store_qty_input.setEnabled(False)
            self.warehouse_qty_input.setEnabled(False)
            self.generate_qr_checkbox.setChecked(False)  # Default to not generating for edits
    
    def save_product(self):
        # Validate inputs
        if not self.name_input.text():
            QMessageBox.warning(self, 'Validation Error', 'Product name is required')
            return
        
        if self.selling_input.value() < self.purchase_input.value():
            QMessageBox.warning(self, 'Validation Error',
                               'Selling price must be greater than purchase price')
            return
        
        # Prepare product data
        product_data = {
            'name': self.name_input.text(),
            'description': self.desc_input.toPlainText(),
            'category': self.cat_input.currentText(),
            'purchase_price': self.purchase_input.value(),
            'selling_price': self.selling_input.value(),
            'reorder_threshold': self.threshold_input.value(),
            'supplier_info': self.supplier_input.toPlainText()
        }
        
        try:
            if self.product:  # Editing existing product
                # Update basic product info
                product = self.db.update_product(self.product.id, product_data)
                
                # Add additional quantities if specified
                add_store = self.add_store_qty_input.value()
                add_warehouse = self.add_warehouse_qty_input.value()
                
                if add_store > 0 or add_warehouse > 0:
                    if self.generate_qr_checkbox.isChecked():
                        updated_product, new_store_items, new_warehouse_items = self.enhanced_manager.add_quantity_to_product(
                            self.product.id, add_store, add_warehouse
                        )
                        QMessageBox.information(self, 'Success', 
                            f'Added {add_store} store items and {add_warehouse} warehouse items with QR codes!')
                    else:
                        # Just update quantities without generating QR codes
                        updated_data = {
                            'store_quantity': self.product.store_quantity + add_store,
                            'warehouse_quantity': self.product.warehouse_quantity + add_warehouse
                        }
                        self.db.update_product(self.product.id, updated_data)
                        
                        # Create assembly task if total quantity is below threshold
                        total_qty = updated_data['store_quantity'] + updated_data['warehouse_quantity']
                        if total_qty <= self.product.reorder_threshold:
                            assembly_qty = max(self.product.reorder_threshold - total_qty + 5, 0)  # Order 5 extra
                            self.todo_manager.create_assembly_task(self.product.id, assembly_qty)
                            QMessageBox.information(self, 'Success', 
                                f'Added {add_store} store items and {add_warehouse} warehouse items!\n\nCreated assembly task for {assembly_qty} additional units.')
                        else:
                            QMessageBox.information(self, 'Success', 
                                f'Added {add_store} store items and {add_warehouse} warehouse items!')
                
            else:  # Adding new product
                store_qty = self.store_qty_input.value()
                warehouse_qty = self.warehouse_qty_input.value()
                
                if self.generate_qr_checkbox.isChecked() and (store_qty > 0 or warehouse_qty > 0):
                    product, store_items, warehouse_items = self.enhanced_manager.add_product_with_items(
                        product_data, store_qty, warehouse_qty
                    )
                    QMessageBox.information(self, 'Success', 
                        f'Product created with {len(store_items)} store items and {len(warehouse_items)} warehouse items with QR codes!')
                else:
                    # Add product without individual item tracking
                    product_data['store_quantity'] = store_qty
                    product_data['warehouse_quantity'] = warehouse_qty
                    product = self.db.add_product(product_data)
                    
                    # Check if initial quantity is below threshold
                    total_qty = store_qty + warehouse_qty
                    if total_qty <= product_data['reorder_threshold']:
                        assembly_qty = max(product_data['reorder_threshold'] - total_qty + 5, 0)  # Order 5 extra
                        self.todo_manager.create_assembly_task(product.id, assembly_qty)
                        QMessageBox.information(self, 'Success', 
                            f'Product created successfully!\n\nCreated assembly task for {assembly_qty} additional units.')
                    else:
                        QMessageBox.information(self, 'Success', 'Product created successfully!')
            
            # Check for low stock and create restock tasks if needed
            self.enhanced_manager.check_and_create_restock_tasks()
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save product: {str(e)}')

class CustomerDialog(QDialog):
    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.customer = customer
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle('Add Customer' if not self.customer else 'Edit Customer')
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Customer Name
        name_layout = QHBoxLayout()
        name_label = QLabel('Name:')
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Contact Information
        phone_layout = QHBoxLayout()
        phone_label = QLabel('Phone:')
        self.phone_input = QLineEdit()
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_input)
        layout.addLayout(phone_layout)
        
        email_layout = QHBoxLayout()
        email_label = QLabel('Email:')
        self.email_input = QLineEdit()
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)
        
        # Address
        address_layout = QVBoxLayout()
        address_label = QLabel('Address:')
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(100)
        address_layout.addWidget(address_label)
        address_layout.addWidget(self.address_input)
        layout.addLayout(address_layout)
        
        # Loyalty Points
        points_layout = QHBoxLayout()
        points_label = QLabel('Loyalty Points:')
        self.points_input = QSpinBox()
        self.points_input.setMaximum(999999)
        points_layout.addWidget(points_label)
        points_layout.addWidget(self.points_input)
        layout.addLayout(points_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.save_customer)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        # Fill data if editing
        if self.customer:
            self.name_input.setText(self.customer.name)
            self.phone_input.setText(self.customer.phone)
            self.email_input.setText(self.customer.email)
            self.address_input.setText(self.customer.address)
            self.points_input.setValue(self.customer.loyalty_points)
    
    def save_customer(self):
        # Validate inputs
        if not self.name_input.text():
            QMessageBox.warning(self, 'Validation Error', 'Customer name is required')
            return
        
        # Prepare customer data
        customer_data = {
            'name': self.name_input.text(),
            'phone': self.phone_input.text(),
            'email': self.email_input.text(),
            'address': self.address_input.toPlainText(),
            'loyalty_points': self.points_input.value()
        }
        
        try:
            if self.customer:  # Editing existing customer
                customer = self.db.update_customer(self.customer.id, customer_data)
            else:  # Adding new customer
                customer = self.db.add_customer(customer_data)
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, 'Error',
                                f'Failed to save customer: {str(e)}')
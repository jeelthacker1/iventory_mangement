from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox,
                             QPushButton, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from database import DatabaseManager
from qr_handler import QRHandler

class ProductDialog(QDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.qr_handler = QRHandler()
        self.product = product
        self.serial_number = None
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
        
        # Location
        location_layout = QHBoxLayout()
        location_label = QLabel('Location:')
        self.location_input = QComboBox()
        self.location_input.addItems(['store', 'warehouse', 'assembly'])
        location_layout.addWidget(location_label)
        location_layout.addWidget(self.location_input)
        layout.addLayout(location_layout)
        
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
        
        # Quantity and Threshold
        qty_layout = QHBoxLayout()
        
        qty_label = QLabel('Quantity:')
        self.qty_input = QSpinBox()
        self.qty_input.setMaximum(9999)
        
        threshold_label = QLabel('Reorder Threshold:')
        self.threshold_input = QSpinBox()
        self.threshold_input.setMaximum(999)
        self.threshold_input.setValue(5)
        
        qty_layout.addWidget(qty_label)
        qty_layout.addWidget(self.qty_input)
        qty_layout.addWidget(threshold_label)
        qty_layout.addWidget(self.threshold_input)
        layout.addLayout(qty_layout)
        
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
            self.qty_input.setValue(self.product.quantity)
            self.threshold_input.setValue(self.product.reorder_threshold)
            self.supplier_input.setText(self.product.supplier_info)
            if hasattr(self.product, 'location') and self.product.location:
                self.location_input.setCurrentText(self.product.location)
            if hasattr(self.product, 'serial_number') and self.product.serial_number:
                self.serial_number = self.product.serial_number
    
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
            'quantity': self.qty_input.value(),
            'reorder_threshold': self.threshold_input.value(),
            'supplier_info': self.supplier_input.toPlainText(),
            'location': self.location_input.currentText()
        }
        
        try:
            if self.product:  # Editing existing product
                product = self.db.update_product(self.product.id, product_data)
            else:  # Adding new product
                product = self.db.add_product(product_data)
                # Generate QR code for new product with serial number
                qr_path, serial_number = self.qr_handler.generate_qr_code(
                    product.id, product.name, quantity=product_data['quantity'])
                self.db.update_product(product.id, {
                    'qr_code': qr_path,
                    'serial_number': serial_number
                })
            
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
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QComboBox, QTextEdit,
                             QSpinBox, QDoubleSpinBox, QDialog, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtPdf import QPdfDocument
from datetime import datetime
from qr_handler import QRHandler
from database import Customer, RepairTask, RepairTaskManager
import os

class RepairTaskWidget(QWidget):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.task_manager = RepairTaskManager(db_manager)
        self.qr_handler = QRHandler()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel('Repair Tasks Management')
        header.setFont(QFont('Arial', 24))
        header.setProperty('heading', 'true')
        layout.addWidget(header)
        
        # Controls
        controls = QHBoxLayout()
        
        self.new_task_btn = QPushButton('New Repair Task')
        self.new_task_btn.clicked.connect(self.show_new_task_dialog)
        
        self.view_mode = QComboBox()
        self.view_mode.addItems(['All Tasks', 'Pending Tasks', 'My Tasks'])
        self.view_mode.currentTextChanged.connect(self.refresh_tasks)
        
        controls.addWidget(self.new_task_btn)
        controls.addWidget(self.view_mode)
        controls.addStretch()
        
        layout.addLayout(controls)
        
        # Tasks table
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(7)
        self.tasks_table.setHorizontalHeaderLabels([
            'ID', 'Customer', 'Description', 'Status',
            'Parts Cost', 'Service Charge', 'Total'
        ])
        self.tasks_table.itemDoubleClicked.connect(self.edit_task)
        layout.addWidget(self.tasks_table)
        
        self.refresh_tasks()
    
    def refresh_tasks(self, mode=None):
        if mode is None:
            mode = self.view_mode.currentText()
        
        if mode == 'Pending Tasks':
            tasks = self.task_manager.get_pending_tasks()
        elif mode == 'My Tasks':
            # TODO: Replace with actual employee name
            tasks = self.task_manager.get_employee_tasks('current_employee')
        else:
            tasks = self.task_manager.get_pending_tasks()
        
        self.tasks_table.setRowCount(len(tasks))
        for i, task in enumerate(tasks):
            self.tasks_table.setItem(i, 0, QTableWidgetItem(str(task.id)))
            self.tasks_table.setItem(i, 1, QTableWidgetItem(task.customer.name))
            self.tasks_table.setItem(i, 2, QTableWidgetItem(task.description))
            self.tasks_table.setItem(i, 3, QTableWidgetItem(task.status))
            self.tasks_table.setItem(i, 4, QTableWidgetItem(f'${task.total_parts_cost:.2f}'))
            self.tasks_table.setItem(i, 5, QTableWidgetItem(f'${task.service_charge:.2f}'))
            self.tasks_table.setItem(i, 6, QTableWidgetItem(f'${task.total_cost:.2f}'))
    
    def show_new_task_dialog(self):
        dialog = RepairTaskDialog(self.db, self)
        if dialog.exec():
            self.refresh_tasks()
    
    def edit_task(self, item):
        row = item.row()
        task_id = int(self.tasks_table.item(row, 0).text())
        dialog = RepairTaskDialog(self.db, self, task_id)
        if dialog.exec():
            self.refresh_tasks()

class RepairTaskDialog(QDialog):
    def __init__(self, db_manager, parent=None, task_id=None):
        super().__init__(parent)
        self.db = db_manager
        self.task_manager = RepairTaskManager(db_manager)
        self.task_id = task_id
        self.task = None
        if task_id:
            self.task = self.db.session.query(RepairTask).get(task_id)
        
        self.setup_ui()
        if self.task:
            self.load_task_data()
    
    def setup_ui(self):
        self.setWindowTitle('Repair Task')
        layout = QVBoxLayout(self)
        
        # Customer selection
        customer_layout = QHBoxLayout()
        customer_layout.addWidget(QLabel('Customer:'))
        self.customer_combo = QComboBox()
        customers = self.db.session.query(Customer).all()
        for customer in customers:
            self.customer_combo.addItem(customer.name, customer.id)
        customer_layout.addWidget(self.customer_combo)
        layout.addLayout(customer_layout)
        
        # Description
        layout.addWidget(QLabel('Description:'))
        self.description = QTextEdit()
        layout.addWidget(self.description)
        
        # Parts section
        layout.addWidget(QLabel('Required Parts:'))
        self.parts_table = QTableWidget()
        self.parts_table.setColumnCount(5)
        self.parts_table.setHorizontalHeaderLabels([
            'Part', 'Quantity', 'Unit Price', 'Subtotal', 'Actions'
        ])
        layout.addWidget(self.parts_table)
        
        # Add part button
        add_part_btn = QPushButton('Add Part')
        add_part_btn.clicked.connect(self.add_part)
        layout.addWidget(add_part_btn)
        
        # Service charge
        charge_layout = QHBoxLayout()
        charge_layout.addWidget(QLabel('Service Charge:'))
        self.service_charge = QDoubleSpinBox()
        self.service_charge.setPrefix('$')
        self.service_charge.setMaximum(10000)
        charge_layout.addWidget(self.service_charge)
        layout.addLayout(charge_layout)
        
        # Status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel('Status:'))
        self.status_combo = QComboBox()
        self.status_combo.addItems(['pending', 'in_progress', 'completed'])
        status_layout.addWidget(self.status_combo)
        layout.addLayout(status_layout)
        
        # Buttons
        buttons = QHBoxLayout()
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.save_task)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        
        if self.task_id:
            generate_bill_btn = QPushButton('Generate Bill')
            generate_bill_btn.clicked.connect(self.generate_bill)
            buttons.addWidget(generate_bill_btn)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
    
    def add_part(self):
        dialog = AddPartDialog(self.db, self)
        if dialog.exec():
            product = dialog.selected_product
            quantity = dialog.quantity.value()
            
            if self.task:
                part = self.task_manager.add_part(
                    self.task.id, product.id, quantity)
                if part:
                    self.refresh_parts()
    
    def refresh_parts(self):
        if not self.task:
            return
        
        self.parts_table.setRowCount(len(self.task.parts))
        for i, part in enumerate(self.task.parts):
            self.parts_table.setItem(i, 0, QTableWidgetItem(part.product.name))
            self.parts_table.setItem(i, 1, QTableWidgetItem(str(part.quantity)))
            self.parts_table.setItem(i, 2, QTableWidgetItem(f'${part.unit_price:.2f}'))
            self.parts_table.setItem(i, 3, QTableWidgetItem(f'${part.subtotal:.2f}'))
            
            remove_btn = QPushButton('Remove')
            remove_btn.clicked.connect(lambda _, p=part: self.remove_part(p))
            self.parts_table.setCellWidget(i, 4, remove_btn)
    
    def remove_part(self, part):
        self.db.session.delete(part)
        self.task.total_parts_cost -= part.subtotal
        self.task.total_cost = self.task.total_parts_cost + self.task.service_charge
        self.db.session.commit()
        self.refresh_parts()
    
    def save_task(self):
        customer_id = self.customer_combo.currentData()
        description = self.description.toPlainText()
        status = self.status_combo.currentText()
        service_charge = self.service_charge.value()
        
        if not description:
            QMessageBox.warning(self, 'Error', 'Please enter a description')
            return
        
        if self.task:
            self.task.customer_id = customer_id
            self.task.description = description
            self.task.status = status
            self.task_manager.set_service_charge(self.task.id, service_charge)
            if status == 'completed' and self.task.status != 'completed':
                self.task.completed_at = datetime.now()
        else:
            self.task = self.task_manager.create_task(
                customer_id, description, 'current_employee')
            self.task_manager.set_service_charge(self.task.id, service_charge)
        
        self.db.session.commit()
        self.accept()
    
    def generate_bill(self):
        if not self.task:
            return
        
        # Create PDF content
        content = f"""Repair Bill

Customer: {self.task.customer.name}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Task ID: {self.task.id}

Description:
{self.task.description}

Parts Used:
"""
        
        for part in self.task.parts:
            content += f"\n{part.product.name} x {part.quantity} @ ${part.unit_price:.2f} = ${part.subtotal:.2f}"
        
        content += f"\n\nParts Total: ${self.task.total_parts_cost:.2f}"
        content += f"\nService Charge: ${self.task.service_charge:.2f}"
        content += f"\nTotal Amount: ${self.task.total_cost:.2f}"
        
        # Generate QR code for the bill
        qr_data = f"BILL#{self.task.id}|{self.task.customer.name}|${self.task.total_cost:.2f}"
        qr_path = self.qr_handler.generate_qr_code(qr_data)
        
        # Save PDF
        file_name = f"repair_bill_{self.task.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        save_path, _ = QFileDialog.getSaveFileName(
            self, 'Save Bill', file_name, 'PDF Files (*.pdf)')
        
        if save_path:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(save_path)
            
            doc = QPdfDocument()
            doc.load(content)
            doc.save(printer)
            
            QMessageBox.information(self, 'Success', 'Bill has been generated and saved!')
    
    def load_task_data(self):
        if not self.task:
            return
        
        # Set customer
        index = self.customer_combo.findData(self.task.customer_id)
        if index >= 0:
            self.customer_combo.setCurrentIndex(index)
        
        self.description.setPlainText(self.task.description)
        self.service_charge.setValue(self.task.service_charge)
        
        index = self.status_combo.findText(self.task.status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        
        self.refresh_parts()

class AddPartDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.selected_product = None
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle('Add Part')
        layout = QVBoxLayout(self)
        
        # Product selection
        layout.addWidget(QLabel('Select Part:'))
        self.product_combo = QComboBox()
        products = self.db.session.query(Product)\
            .filter(Product.category == 'spareparts')\
            .all()
        for product in products:
            self.product_combo.addItem(
                f'{product.name} (${product.selling_price:.2f})', product.id)
        layout.addWidget(self.product_combo)
        
        # Quantity
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel('Quantity:'))
        self.quantity = QSpinBox()
        self.quantity.setMinimum(1)
        self.quantity.setMaximum(100)
        quantity_layout.addWidget(self.quantity)
        layout.addLayout(quantity_layout)
        
        # Buttons
        buttons = QHBoxLayout()
        add_btn = QPushButton('Add')
        add_btn.clicked.connect(self.add_part)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(add_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
    
    def add_part(self):
        product_id = self.product_combo.currentData()
        self.selected_product = self.db.session.query(Product).get(product_id)
        if self.selected_product:
            self.accept()
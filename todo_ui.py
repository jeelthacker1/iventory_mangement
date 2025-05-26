from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QComboBox, QTextEdit, QMessageBox, QDialog,
                             QLineEdit, QGroupBox, QGridLayout, QHeaderView,
                             QSpinBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from database import DatabaseManager, TodoTask
from todo_manager import TodoManager
from enhanced_product_manager import EnhancedProductManager
from datetime import datetime

class TodoWidget(QWidget):
    task_completed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.todo_manager = TodoManager(self.db)
        self.enhanced_manager = EnhancedProductManager(self.db)
        self.setup_ui()
        self.load_tasks()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel('Employee Task Management')
        title.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Filter controls
        filter_label = QLabel('Filter by:')
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(['All Tasks', 'Pending', 'In Progress', 'High Priority', 'Restock Tasks', 'Assembly Tasks'])
        self.filter_combo.currentTextChanged.connect(self.filter_tasks)
        
        refresh_btn = QPushButton('Refresh')
        refresh_btn.clicked.connect(self.load_tasks)
        
        header_layout.addWidget(filter_label)
        header_layout.addWidget(self.filter_combo)
        header_layout.addWidget(refresh_btn)
        layout.addLayout(header_layout)
        
        # Tasks table
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(8)
        self.tasks_table.setHorizontalHeaderLabels([
            'ID', 'Type', 'Description', 'Product', 'Quantity', 'Priority', 'Status', 'Actions'
        ])
        
        # Set column widths
        header = self.tasks_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.tasks_table)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.complete_btn = QPushButton('Complete Selected Task')
        self.complete_btn.clicked.connect(self.complete_task)
        
        self.move_stock_btn = QPushButton('Move Stock (Warehouse → Store)')
        self.move_stock_btn.clicked.connect(self.move_stock)
        
        self.create_task_btn = QPushButton('Create New Task')
        self.create_task_btn.clicked.connect(self.create_task)
        
        actions_layout.addWidget(self.complete_btn)
        actions_layout.addWidget(self.move_stock_btn)
        actions_layout.addWidget(self.create_task_btn)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
    
    def load_tasks(self):
        """Load all tasks into the table."""
        tasks = self.todo_manager.get_pending_tasks()
        self.populate_table(tasks)
    
    def filter_tasks(self):
        """Filter tasks based on selected filter."""
        filter_text = self.filter_combo.currentText()
        
        if filter_text == 'All Tasks':
            tasks = self.db.get_todo_tasks()
        elif filter_text == 'Pending':
            tasks = self.todo_manager.get_pending_tasks()
        elif filter_text == 'In Progress':
            tasks = self.db.get_todo_tasks(status='in_progress')
        elif filter_text == 'High Priority':
            tasks = self.todo_manager.get_high_priority_tasks()
        elif filter_text == 'Restock Tasks':
            tasks = self.todo_manager.get_pending_tasks(task_type='restock')
        elif filter_text == 'Assembly Tasks':
            tasks = self.todo_manager.get_pending_tasks(task_type='assembly')
        else:
            tasks = self.todo_manager.get_pending_tasks()
        
        self.populate_table(tasks)
    
    def populate_table(self, tasks):
        """Populate the table with tasks."""
        self.tasks_table.setRowCount(len(tasks))
        
        for row, task in enumerate(tasks):
            # ID
            self.tasks_table.setItem(row, 0, QTableWidgetItem(str(task.id)))
            
            # Type
            type_item = QTableWidgetItem(task.task_type.title())
            if task.priority == 'high':
                type_item.setBackground(Qt.GlobalColor.red)
                type_item.setForeground(Qt.GlobalColor.white)
            elif task.priority == 'medium':
                type_item.setBackground(Qt.GlobalColor.yellow)
            self.tasks_table.setItem(row, 1, type_item)
            
            # Description
            self.tasks_table.setItem(row, 2, QTableWidgetItem(task.description))
            
            # Product
            product_name = task.product.name if task.product else 'N/A'
            self.tasks_table.setItem(row, 3, QTableWidgetItem(product_name))
            
            # Quantity
            self.tasks_table.setItem(row, 4, QTableWidgetItem(str(task.quantity_needed)))
            
            # Priority
            priority_item = QTableWidgetItem(task.priority.title())
            if task.priority == 'high':
                priority_item.setBackground(Qt.GlobalColor.red)
                priority_item.setForeground(Qt.GlobalColor.white)
            self.tasks_table.setItem(row, 5, priority_item)
            
            # Status
            status_item = QTableWidgetItem(task.status.title())
            if task.status == 'completed':
                status_item.setBackground(Qt.GlobalColor.green)
                status_item.setForeground(Qt.GlobalColor.white)
            elif task.status == 'in_progress':
                status_item.setBackground(Qt.GlobalColor.blue)
                status_item.setForeground(Qt.GlobalColor.white)
            self.tasks_table.setItem(row, 6, status_item)
            
            # Actions
            if task.status == 'pending':
                start_btn = QPushButton('Start')
                start_btn.clicked.connect(lambda checked, t_id=task.id: self.start_task(t_id))
                self.tasks_table.setCellWidget(row, 7, start_btn)
            elif task.status == 'in_progress':
                complete_btn = QPushButton('Complete')
                complete_btn.clicked.connect(lambda checked, t_id=task.id: self.complete_task_by_id(t_id))
                self.tasks_table.setCellWidget(row, 7, complete_btn)
    
    def start_task(self, task_id):
        """Start a task (change status to in_progress)."""
        self.todo_manager.update_task_status(task_id, 'in_progress')
        self.load_tasks()
        QMessageBox.information(self, 'Success', 'Task started!')
    
    def complete_task_by_id(self, task_id):
        """Complete a specific task."""
        task = self.db.session.query(TodoTask).get(task_id)
        if task:
            dialog = CompleteTaskDialog(self, task)
            if dialog.exec():
                self.load_tasks()
                self.task_completed.emit()
    
    def complete_task(self):
        """Complete the selected task."""
        selected_items = self.tasks_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, 'No Selection', 'Please select a task to complete.')
            return
        
        row = selected_items[0].row()
        task_id = int(self.tasks_table.item(row, 0).text())
        
        task = self.db.session.query(TodoTask).get(task_id)
        if task:
            dialog = CompleteTaskDialog(self, task)
            if dialog.exec():
                self.load_tasks()
                self.task_completed.emit()
    
    def move_stock(self):
        """Open dialog to move stock from warehouse to store."""
        dialog = MoveStockDialog(self)
        if dialog.exec():
            self.load_tasks()
            QMessageBox.information(self, 'Success', 'Stock moved successfully!')
    
    def create_task(self):
        """Open dialog to create a new task."""
        dialog = CreateTaskDialog(self)
        if dialog.exec():
            self.load_tasks()

class CompleteTaskDialog(QDialog):
    def __init__(self, parent=None, task=None):
        super().__init__(parent)
        self.task = task
        self.db = DatabaseManager()
        self.todo_manager = TodoManager(self.db)
        self.enhanced_manager = EnhancedProductManager(self.db)
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle('Complete Task')
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Task info
        info_group = QGroupBox('Task Information')
        info_layout = QGridLayout(info_group)
        
        info_layout.addWidget(QLabel('Type:'), 0, 0)
        info_layout.addWidget(QLabel(self.task.task_type.title()), 0, 1)
        
        info_layout.addWidget(QLabel('Description:'), 1, 0)
        desc_label = QLabel(self.task.description)
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label, 1, 1)
        
        if self.task.product:
            info_layout.addWidget(QLabel('Product:'), 2, 0)
            info_layout.addWidget(QLabel(self.task.product.name), 2, 1)
            
            info_layout.addWidget(QLabel('Quantity Needed:'), 3, 0)
            info_layout.addWidget(QLabel(str(self.task.quantity_needed)), 3, 1)
        
        layout.addWidget(info_group)
        
        # Notes
        notes_group = QGroupBox('Completion Notes')
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText('Add any notes about completing this task...')
        notes_layout.addWidget(self.notes_input)
        
        layout.addWidget(notes_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        complete_btn = QPushButton('Complete Task')
        complete_btn.clicked.connect(self.complete_task)
        
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(complete_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
    
    def complete_task(self):
        """Complete the task and handle any special actions."""
        notes = self.notes_input.toPlainText()
        
        # If it's a restock task, actually move the items
        if self.task.task_type == 'restock' and self.task.product:
            try:
                moved_items = self.enhanced_manager.move_warehouse_to_store(
                    self.task.product_id, self.task.quantity_needed
                )
                if moved_items:
                    notes += f"\n\nMoved {len(moved_items)} items from warehouse to store."
                else:
                    QMessageBox.warning(self, 'Warning', 
                        'No items were available in warehouse to move.')
                    return
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to move stock: {str(e)}')
                return
        
        # Complete the task
        self.todo_manager.complete_task(self.task.id, notes)
        
        QMessageBox.information(self, 'Success', 'Task completed successfully!')
        self.accept()

class MoveStockDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.enhanced_manager = EnhancedProductManager(self.db)
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle('Move Stock: Warehouse → Store')
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Product selection
        product_layout = QHBoxLayout()
        product_layout.addWidget(QLabel('Product:'))
        
        self.product_combo = QComboBox()
        self.load_products()
        product_layout.addWidget(self.product_combo)
        
        layout.addLayout(product_layout)
        
        # Quantity
        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel('Quantity to Move:'))
        
        self.qty_input = QSpinBox()
        self.qty_input.setMinimum(1)
        self.qty_input.setMaximum(9999)
        qty_layout.addWidget(self.qty_input)
        
        layout.addLayout(qty_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        move_btn = QPushButton('Move Stock')
        move_btn.clicked.connect(self.move_stock)
        
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(move_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
    
    def load_products(self):
        """Load products that have warehouse stock."""
        products = self.db.get_all_products()
        
        for product in products:
            if product.warehouse_quantity > 0:
                self.product_combo.addItem(
                    f"{product.name} (Warehouse: {product.warehouse_quantity})",
                    product.id
                )
    
    def move_stock(self):
        """Move the specified quantity from warehouse to store."""
        if self.product_combo.count() == 0:
            QMessageBox.warning(self, 'No Products', 'No products with warehouse stock available.')
            return
        
        product_id = self.product_combo.currentData()
        quantity = self.qty_input.value()
        
        try:
            moved_items = self.enhanced_manager.move_warehouse_to_store(product_id, quantity)
            if moved_items:
                QMessageBox.information(self, 'Success', 
                    f'Successfully moved {len(moved_items)} items to store.')
                self.accept()
            else:
                QMessageBox.warning(self, 'Warning', 
                    'No items were available to move.')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to move stock: {str(e)}')

class CreateTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.todo_manager = TodoManager(self.db)
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle('Create New Task')
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Task type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel('Task Type:'))
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(['restock', 'assembly', 'other'])
        type_layout.addWidget(self.type_combo)
        
        layout.addLayout(type_layout)
        
        # Description
        layout.addWidget(QLabel('Description:'))
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(100)
        layout.addWidget(self.desc_input)
        
        # Product (optional)
        product_layout = QHBoxLayout()
        product_layout.addWidget(QLabel('Product (optional):'))
        
        self.product_combo = QComboBox()
        self.product_combo.addItem('None', None)
        
        products = self.db.get_all_products()
        for product in products:
            self.product_combo.addItem(product.name, product.id)
        
        product_layout.addWidget(self.product_combo)
        layout.addLayout(product_layout)
        
        # Quantity
        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel('Quantity:'))
        
        self.qty_input = QSpinBox()
        self.qty_input.setMaximum(9999)
        qty_layout.addWidget(self.qty_input)
        
        layout.addLayout(qty_layout)
        
        # Priority
        priority_layout = QHBoxLayout()
        priority_layout.addWidget(QLabel('Priority:'))
        
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(['low', 'medium', 'high'])
        self.priority_combo.setCurrentText('medium')
        priority_layout.addWidget(self.priority_combo)
        
        layout.addLayout(priority_layout)
        
        # Assigned to
        assigned_layout = QHBoxLayout()
        assigned_layout.addWidget(QLabel('Assign to:'))
        
        self.assigned_input = QLineEdit()
        self.assigned_input.setPlaceholderText('Employee name (optional)')
        assigned_layout.addWidget(self.assigned_input)
        
        layout.addLayout(assigned_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        create_btn = QPushButton('Create Task')
        create_btn.clicked.connect(self.create_task)
        
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(create_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
    
    def create_task(self):
        """Create the new task."""
        if not self.desc_input.toPlainText().strip():
            QMessageBox.warning(self, 'Validation Error', 'Description is required.')
            return
        
        # TodoTask is already imported at the top
        
        task = TodoTask(
            task_type=self.type_combo.currentText(),
            description=self.desc_input.toPlainText(),
            product_id=self.product_combo.currentData(),
            quantity_needed=self.qty_input.value(),
            priority=self.priority_combo.currentText(),
            assigned_to=self.assigned_input.text() or None
        )
        
        self.db.session.add(task)
        self.db.session.commit()
        
        QMessageBox.information(self, 'Success', 'Task created successfully!')
        self.accept()
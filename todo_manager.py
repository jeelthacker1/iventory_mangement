from datetime import datetime
from database import DatabaseManager, TodoTask

class TodoManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create_restock_task(self, product_id, quantity_needed, assigned_to=None):
        """Create a task to restock items from warehouse to store."""
        product = self.db.get_product(product_id)
        if not product:
            return None
        
        description = f"Move {quantity_needed} units of '{product.name}' from warehouse to store"
        
        task = TodoTask(
            task_type='restock',
            description=description,
            product_id=product_id,
            quantity_needed=quantity_needed,
            assigned_to=assigned_to,
            priority='high' if product.store_quantity <= 2 else 'medium'
        )
        
        self.db.session.add(task)
        self.db.session.commit()
        return task
    
    def create_assembly_task(self, product_id, quantity_needed, assigned_to=None):
        """Create a task to assemble products for warehouse stock."""
        product = self.db.get_product(product_id)
        if not product:
            return None
        
        description = f"Assemble {quantity_needed} units of '{product.name}' for warehouse stock"
        
        task = TodoTask(
            task_type='assembly',
            description=description,
            product_id=product_id,
            quantity_needed=quantity_needed,
            assigned_to=assigned_to,
            priority='medium'
        )
        
        self.db.session.add(task)
        self.db.session.commit()
        return task
    
    def complete_task(self, task_id, notes=None):
        """Mark a task as completed."""
        task = self.db.session.query(TodoTask).get(task_id)
        if task:
            task.status = 'completed'
            task.completed_at = datetime.now()
            if notes:
                task.notes = notes
            self.db.session.commit()
            return task
        return None
    
    def get_pending_tasks(self, task_type=None, assigned_to=None):
        """Get all pending tasks, optionally filtered by type or assignee."""
        query = self.db.session.query(TodoTask).filter(TodoTask.status == 'pending')
        
        if task_type:
            query = query.filter(TodoTask.task_type == task_type)
        
        if assigned_to:
            query = query.filter(TodoTask.assigned_to == assigned_to)
        
        return query.order_by(TodoTask.created_at.desc()).all()
    
    def get_high_priority_tasks(self):
        """Get all high priority pending tasks."""
        return self.db.session.query(TodoTask).filter(
            TodoTask.status == 'pending',
            TodoTask.priority == 'high'
        ).order_by(TodoTask.created_at.desc()).all()
    
    def update_task_status(self, task_id, status):
        """Update task status."""
        task = self.db.session.query(TodoTask).get(task_id)
        if task:
            task.status = status
            if status == 'completed':
                task.completed_at = datetime.now()
            self.db.session.commit()
            return task
        return None
    
    def assign_task(self, task_id, assigned_to):
        """Assign a task to an employee."""
        task = self.db.session.query(TodoTask).get(task_id)
        if task:
            task.assigned_to = assigned_to
            self.db.session.commit()
            return task
        return None
    
    def check_low_stock_and_create_tasks(self):
        """Check for low stock products and create restock and assembly tasks automatically."""
        tasks_created = []
        
        # Handle products needing restock from warehouse to store
        restock_products = self.db.get_products_needing_restock()
        for product in restock_products:
            # Check if there's already a pending restock task
            existing_task = self.db.session.query(TodoTask).filter(
                TodoTask.product_id == product.id,
                TodoTask.task_type == 'restock',
                TodoTask.status == 'pending'
            ).first()
            
            if not existing_task:
                needed_in_store = max(product.reorder_threshold - product.store_quantity, 0)
                available_in_warehouse = product.warehouse_quantity
                quantity_to_move = min(needed_in_store, available_in_warehouse)
                
                if quantity_to_move > 0:
                    task = self.create_restock_task(product.id, quantity_to_move)
                    if task:
                        tasks_created.append(task)
        
        # Handle products needing assembly/ordering
        assembly_products = self.db.get_products_needing_assembly()
        for product in assembly_products:
            # Check if there's already a pending assembly task
            existing_task = self.db.session.query(TodoTask).filter(
                TodoTask.product_id == product.id,
                TodoTask.task_type == 'assembly',
                TodoTask.status == 'pending'
            ).first()
            
            if not existing_task:
                total_quantity = product.store_quantity + product.warehouse_quantity
                if total_quantity <= product.reorder_threshold:
                    # Order 5 extra units above the threshold
                    assembly_qty = max(product.reorder_threshold - total_quantity + 5, 0)
                    task = self.create_assembly_task(product.id, assembly_qty)
                    if task:
                        tasks_created.append(task)
        
        return tasks_created
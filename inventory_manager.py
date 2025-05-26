from datetime import datetime
from sqlalchemy import and_
from database import Product

class InventoryManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self.MIN_STORE_THRESHOLD = 5
        self.MIN_TOTAL_THRESHOLD = 10
    
    def add_product(self, product_data):
        """Add a new product with store and warehouse quantities."""
        if 'quantity' in product_data:
            store_qty = product_data.pop('quantity')
            product_data['store_quantity'] = store_qty
            product_data['warehouse_quantity'] = 0
        
        return self.db.add_product(product_data)
    
    def get_inventory_breakdown(self):
        """List all products with store and warehouse quantities."""
        products = self.db.session.query(Product).all()
        return [{
            'id': p.id,
            'name': p.name,
            'store_quantity': p.store_quantity,
            'warehouse_quantity': p.warehouse_quantity,
            'total_quantity': p.store_quantity + p.warehouse_quantity
        } for p in products]
    
    def get_assembly_suggestions(self, min_store_threshold=None):
        """Get list of products that need assembly (low store quantity)."""
        threshold = min_store_threshold or self.MIN_STORE_THRESHOLD
        return self.db.session.query(Product).filter(
            and_(
                Product.store_quantity < threshold,
                Product.warehouse_quantity > 0
            )
        ).all()
    
    def get_reorder_suggestions(self, min_total_threshold=None):
        """Get list of products that need reordering (low total quantity)."""
        threshold = min_total_threshold or self.MIN_TOTAL_THRESHOLD
        return self.db.session.query(Product).filter(
            (Product.store_quantity + Product.warehouse_quantity) < threshold
        ).all()
    
    def assemble_products(self, product_id, quantity):
        """Transfer products from warehouse to store after assembly."""
        product = self.db.get_product(product_id)
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        if product.warehouse_quantity < quantity:
            raise ValueError(f"Insufficient warehouse quantity. Available: {product.warehouse_quantity}")
        
        product.warehouse_quantity -= quantity
        product.store_quantity += quantity
        product.updated_at = datetime.now()
        self.db.session.commit()
        return product
    
    def mark_product_ordered(self, product_id, supplier_id=None, order_date=None, eta=None):
        """Mark a product as ordered with optional supplier and ETA info."""
        product = self.db.get_product(product_id)
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        product.last_ordered_at = order_date or datetime.now()
        if supplier_id:
            product.supplier_id = supplier_id
        if eta:
            product.expected_arrival = eta
        
        product.updated_at = datetime.now()
        self.db.session.commit()
        return product
    
    def set_thresholds(self, min_store=None, min_total=None):
        """Update the threshold values for store and total inventory."""
        if min_store is not None:
            self.MIN_STORE_THRESHOLD = min_store
        if min_total is not None:
            self.MIN_TOTAL_THRESHOLD = min_total
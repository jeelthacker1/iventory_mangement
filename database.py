from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.types import Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    category = Column(String)
    purchase_price = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)
    store_quantity = Column(Integer, default=0)
    warehouse_quantity = Column(Integer, default=0)
    supplier_info = Column(String)
    reorder_threshold = Column(Integer, default=5)
    qr_code = Column(String)  # Path to QR code image
    serial_number = Column(String)  # Unique serial number for each product unit
    last_ordered_at = Column(DateTime)
    expected_arrival = Column(DateTime)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    supplier = relationship('Supplier', backref='products')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class RepairTask(Base):
    __tablename__ = 'repair_tasks'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    description = Column(Text, nullable=False)
    status = Column(String, default='pending')  # pending, in_progress, completed
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime)
    total_parts_cost = Column(Float, default=0.0)
    service_charge = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    assigned_to = Column(String)  # Employee name
    customer = relationship('Customer', backref='repair_tasks')

class RepairPart(Base):
    __tablename__ = 'repair_parts'
    
    id = Column(Integer, primary_key=True)
    repair_task_id = Column(Integer, ForeignKey('repair_tasks.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    repair_task = relationship('RepairTask', backref='parts')
    product = relationship('Product')

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    email = Column(String)
    address = Column(String)
    loyalty_points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class Sale(Base):
    __tablename__ = 'sales'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    total_amount = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False)
    sale_date = Column(DateTime, default=datetime.now)
    customer = relationship('Customer', backref='sales')

class SaleItem(Base):
    __tablename__ = 'sale_items'
    
    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey('sales.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    sale = relationship('Sale', backref='items')
    product = relationship('Product')

class Supplier(Base):
    __tablename__ = 'suppliers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    contact_person = Column(String)
    phone = Column(String)
    email = Column(String)
    address = Column(String)
    created_at = Column(DateTime, default=datetime.now)

class TodoTask(Base):
    __tablename__ = 'todo_tasks'
    
    id = Column(Integer, primary_key=True)
    task_type = Column(String, nullable=False)  # 'restock', 'assembly', 'other'
    description = Column(String, nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    quantity_needed = Column(Integer, default=0)
    assigned_to = Column(String)  # Employee name
    priority = Column(String, default='medium')  # low, medium, high
    status = Column(String, default='pending')  # pending, in_progress, completed
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime)
    notes = Column(String)
    
    # Relationships
    product = relationship('Product', backref='todo_tasks')

class ProductItem(Base):
    __tablename__ = 'product_items'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    item_number = Column(Integer, nullable=False)  # Sequential number for each product
    serial_number = Column(String, unique=True, nullable=False)  # Unique serial like P1I1, P1I2
    qr_code_path = Column(String)  # Path to QR code image
    barcode_path = Column(String)  # Path to barcode image
    location = Column(String, default='store')  # store, warehouse, sold
    status = Column(String, default='in_stock')  # in_stock, sold, damaged
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    product = relationship('Product', backref='items')

class DatabaseManager:
    def __init__(self, db_path='inventory.db'):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def add_product(self, product_data):
        product = Product(**product_data)
        self.session.add(product)
        self.session.commit()
        return product
    
    def update_product(self, product_id, product_data):
        product = self.session.query(Product).filter_by(id=product_id).first()
        if product:
            for key, value in product_data.items():
                setattr(product, key, value)
            self.session.commit()
            return product
        return None
    
    def delete_product(self, product_id):
        product = self.session.query(Product).filter_by(id=product_id).first()
        if product:
            self.session.delete(product)
            self.session.commit()
            return True
        return False
    
    def get_product(self, product_id):
        return self.session.query(Product).filter_by(id=product_id).first()
    
    def get_all_products(self):
        return self.session.query(Product).all()
    
    def get_low_stock_products(self):
        # Get products where either store quantity is low or total quantity is low
        return self.session.query(Product).filter(
            ((Product.store_quantity <= Product.reorder_threshold) |
             ((Product.store_quantity + Product.warehouse_quantity) <= Product.reorder_threshold))
        ).all()

    def get_products_needing_assembly(self):
        # Get products where total quantity (store + warehouse) is below threshold
        return self.session.query(Product).filter(
            (Product.store_quantity + Product.warehouse_quantity) <= Product.reorder_threshold
        ).all()

    def get_products_needing_restock(self):
        # Get products where store quantity is low but warehouse has stock
        return self.session.query(Product).filter(
            (Product.store_quantity <= Product.reorder_threshold) &
            (Product.warehouse_quantity > 0)
        ).all()
    
    def add_customer(self, customer_data):
        customer = Customer(**customer_data)
        self.session.add(customer)
        self.session.commit()
        return customer
    
    def add_sale(self, sale_data, items_data):
        sale = Sale(**sale_data)
        self.session.add(sale)
        self.session.flush()
        
        for item_data in items_data:
            item_data['sale_id'] = sale.id
            sale_item = SaleItem(**item_data)
            self.session.add(sale_item)
            
            # Update product store quantity
            product = self.get_product(item_data['product_id'])
            if product:
                product.store_quantity -= item_data['quantity']
        
        self.session.commit()
        return sale
    
    def get_sales_report(self, start_date, end_date):
        return self.session.query(Sale).filter(
            Sale.sale_date.between(start_date, end_date)
        ).all()
    
    def get_customer(self, customer_id):
        return self.session.query(Customer).filter_by(id=customer_id).first()
    
    def get_all_customers(self):
        return self.session.query(Customer).all()
    
    def update_customer(self, customer_id, customer_data):
        customer = self.session.query(Customer).filter_by(id=customer_id).first()
        if customer:
            for key, value in customer_data.items():
                setattr(customer, key, value)
            self.session.commit()
            return customer
        return None
    
    def add_product_item(self, product_id, serial_number, qr_code_path=None, barcode_path=None, location='store'):
        """Add a new product item with unique serial number."""
        # Get the next item number for this product
        last_item = self.session.query(ProductItem).filter_by(product_id=product_id).order_by(ProductItem.item_number.desc()).first()
        item_number = (last_item.item_number + 1) if last_item else 1
        
        item = ProductItem(
            product_id=product_id,
            item_number=item_number,
            serial_number=serial_number,
            qr_code_path=qr_code_path,
            barcode_path=barcode_path,
            location=location
        )
        self.session.add(item)
        self.session.commit()
        return item
    
    def get_product_items(self, product_id, location=None, status=None):
        """Get product items, optionally filtered by location and status."""
        query = self.session.query(ProductItem).filter_by(product_id=product_id)
        
        if location:
            query = query.filter_by(location=location)
        if status:
            query = query.filter_by(status=status)
            
        return query.order_by(ProductItem.item_number).all()
    
    def update_product_item_location(self, item_id, new_location):
        """Update the location of a product item."""
        item = self.session.query(ProductItem).get(item_id)
        if item:
            item.location = new_location
            self.session.commit()
            return item
        return None
    
    def move_items_warehouse_to_store(self, product_id, quantity):
        """Move items from warehouse to store location."""
        # Get warehouse items for this product
        warehouse_items = self.session.query(ProductItem).filter_by(
            product_id=product_id,
            location='warehouse',
            status='in_stock'
        ).limit(quantity).all()
        
        moved_items = []
        for item in warehouse_items:
            item.location = 'store'
            moved_items.append(item)
        
        if moved_items:
            # Update product quantities
            product = self.get_product(product_id)
            if product:
                product.warehouse_quantity -= len(moved_items)
                product.store_quantity += len(moved_items)
            
            self.session.commit()
        
        return moved_items
    
    def get_todo_tasks(self, status=None, task_type=None, assigned_to=None):
        """Get todo tasks with optional filters."""
        query = self.session.query(TodoTask)
        
        if status:
            query = query.filter_by(status=status)
        if task_type:
            query = query.filter_by(task_type=task_type)
        if assigned_to:
            query = query.filter_by(assigned_to=assigned_to)
            
        return query.order_by(TodoTask.created_at.desc()).all()
    
    def close(self):
        self.session.close()

class RepairTaskManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def create_task(self, customer_id, description, assigned_to):
        task = RepairTask(
            customer_id=customer_id,
            description=description,
            assigned_to=assigned_to
        )
        self.db.session.add(task)
        self.db.session.commit()
        return task
    
    def add_part(self, task_id, product_id, quantity):
        product = self.db.session.query(Product).get(product_id)
        if not product:
            return None
        
        part = RepairPart(
            repair_task_id=task_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=product.selling_price,
            subtotal=product.selling_price * quantity
        )
        self.db.session.add(part)
        
        # Update task total
        task = self.db.session.query(RepairTask).get(task_id)
        task.total_parts_cost += part.subtotal
        task.total_cost = task.total_parts_cost + task.service_charge
        
        self.db.session.commit()
        return part
    
    def update_task_status(self, task_id, status):
        task = self.db.session.query(RepairTask).get(task_id)
        if task:
            task.status = status
            if status == 'completed':
                task.completed_at = datetime.now()
            self.db.session.commit()
            return task
        return None
    
    def set_service_charge(self, task_id, charge):
        task = self.db.session.query(RepairTask).get(task_id)
        if task:
            task.service_charge = charge
            task.total_cost = task.total_parts_cost + charge
            self.db.session.commit()
            return task
        return None
    
    def get_pending_tasks(self):
        return self.db.session.query(RepairTask)\
            .filter(RepairTask.status != 'completed')\
            .order_by(RepairTask.created_at.desc())\
            .all()
    
    def get_employee_tasks(self, employee_name):
        return self.db.session.query(RepairTask)\
            .filter(RepairTask.assigned_to == employee_name)\
            .filter(RepairTask.status != 'completed')\
            .order_by(RepairTask.created_at.desc())\
            .all()
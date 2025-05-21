from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
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
    quantity = Column(Integer, default=0)
    supplier_info = Column(String)
    reorder_threshold = Column(Integer, default=5)
    qr_code = Column(String)  # Path to QR code image
    location = Column(String, default='store')  # 'store', 'warehouse', or 'assembly'
    serial_number = Column(String)  # Unique serial number for each product unit
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

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
        return self.session.query(Product).filter(
            Product.quantity <= Product.reorder_threshold
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
            
            # Update product quantity
            product = self.get_product(item_data['product_id'])
            if product:
                product.quantity -= item_data['quantity']
        
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
    
    def close(self):
        self.session.close()
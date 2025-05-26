from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class ProductItem(Base):
    __tablename__ = 'product_items'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    item_number = Column(Integer, nullable=False)  # Sequential number for each product
    qr_code_path = Column(String)  # Path to QR code image
    status = Column(String, default='in_stock')  # in_stock, sold, damaged
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    product = relationship('Product', backref='items')
    
    def __repr__(self):
        return f"<ProductItem(product_id={self.product_id}, item_number={self.item_number})>"
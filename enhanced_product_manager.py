import qrcode
import barcode
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
from database import DatabaseManager, ProductItem
from todo_manager import TodoManager

class EnhancedProductManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self.todo_manager = TodoManager(db_manager)
        self.qr_code_dir = 'qr_codes'
        self.barcode_dir = 'barcodes'
        
        # Create directories if they don't exist
        for directory in [self.qr_code_dir, self.barcode_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def generate_serial_number(self, product_id, item_number):
        """Generate unique serial number in format P{product_id}I{item_number}."""
        return f"P{product_id}I{item_number}"
    
    def generate_qr_code(self, product_id, item_number, serial_number):
        """Generate QR code for a specific product item."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Create QR code data with product info and serial number
        product = self.db.get_product(product_id)
        data = f"Product: {product.name}\nSerial: {serial_number}\nID: {product_id}\nItem: {item_number}"
        qr.add_data(data)
        qr.make(fit=True)

        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code
        filename = f"{self.qr_code_dir}/{serial_number}_qr.png"
        qr_image.save(filename)
        return filename
    
    def generate_barcode(self, serial_number):
        """Generate barcode for the serial number."""
        try:
            # Use Code128 barcode format
            code128 = barcode.get_barcode_class('code128')
            barcode_instance = code128(serial_number, writer=ImageWriter())
            
            filename = f"{self.barcode_dir}/{serial_number}_barcode"
            barcode_path = barcode_instance.save(filename)
            return barcode_path
        except Exception as e:
            print(f"Error generating barcode: {e}")
            return None
    
    def add_product_with_items(self, product_data, store_quantity=0, warehouse_quantity=0):
        """Add a new product with individual items and generate QR codes/barcodes."""
        # Set the quantities in product data
        product_data['store_quantity'] = store_quantity
        product_data['warehouse_quantity'] = warehouse_quantity
        
        # Add the main product
        product = self.db.add_product(product_data)
        
        # Generate items for store
        store_items = []
        for i in range(store_quantity):
            item_number = i + 1
            serial_number = self.generate_serial_number(product.id, item_number)
            qr_code_path = self.generate_qr_code(product.id, item_number, serial_number)
            barcode_path = self.generate_barcode(serial_number)
            
            item = self.db.add_product_item(
                product_id=product.id,
                serial_number=serial_number,
                qr_code_path=qr_code_path,
                barcode_path=barcode_path,
                location='store'
            )
            store_items.append(item)
        
        # Generate items for warehouse
        warehouse_items = []
        for i in range(warehouse_quantity):
            item_number = store_quantity + i + 1
            serial_number = self.generate_serial_number(product.id, item_number)
            qr_code_path = self.generate_qr_code(product.id, item_number, serial_number)
            barcode_path = self.generate_barcode(serial_number)
            
            item = self.db.add_product_item(
                product_id=product.id,
                serial_number=serial_number,
                qr_code_path=qr_code_path,
                barcode_path=barcode_path,
                location='warehouse'
            )
            warehouse_items.append(item)
        
        return product, store_items, warehouse_items
    
    def add_quantity_to_product(self, product_id, store_quantity=0, warehouse_quantity=0):
        """Add additional quantity to existing product and generate QR codes/barcodes."""
        product = self.db.get_product(product_id)
        if not product:
            return None, [], []
        
        # Get the last item number for this product
        last_item = self.db.session.query(ProductItem).filter_by(
            product_id=product_id
        ).order_by(ProductItem.item_number.desc()).first()
        
        next_item_number = (last_item.item_number + 1) if last_item else 1
        
        # Generate new store items
        new_store_items = []
        for i in range(store_quantity):
            item_number = next_item_number + i
            serial_number = self.generate_serial_number(product_id, item_number)
            qr_code_path = self.generate_qr_code(product_id, item_number, serial_number)
            barcode_path = self.generate_barcode(serial_number)
            
            item = self.db.add_product_item(
                product_id=product_id,
                serial_number=serial_number,
                qr_code_path=qr_code_path,
                barcode_path=barcode_path,
                location='store'
            )
            new_store_items.append(item)
        
        # Generate new warehouse items
        new_warehouse_items = []
        for i in range(warehouse_quantity):
            item_number = next_item_number + store_quantity + i
            serial_number = self.generate_serial_number(product_id, item_number)
            qr_code_path = self.generate_qr_code(product_id, item_number, serial_number)
            barcode_path = self.generate_barcode(serial_number)
            
            item = self.db.add_product_item(
                product_id=product_id,
                serial_number=serial_number,
                qr_code_path=qr_code_path,
                barcode_path=barcode_path,
                location='warehouse'
            )
            new_warehouse_items.append(item)
        
        # Update product quantities
        updated_data = {
            'store_quantity': product.store_quantity + store_quantity,
            'warehouse_quantity': product.warehouse_quantity + warehouse_quantity
        }
        updated_product = self.db.update_product(product_id, updated_data)
        
        return updated_product, new_store_items, new_warehouse_items
    
    def generate_qr_codes_pdf(self, product_id, location='store', include_barcode=True):
        """Generate a PDF containing QR codes and barcodes for product items."""
        product = self.db.get_product(product_id)
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        # Get items for the specified location
        items = self.db.get_product_items(product_id, location=location, status='in_stock')
        
        if not items:
            raise ValueError(f"No items found for product {product_id} in {location}")
        
        # Create PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"{self.qr_code_dir}/product_{product_id}_{location}_codes_{timestamp}.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=A4)
        width, height = A4
        
        # Layout settings
        qr_size = 1.5 * inch
        barcode_width = 2 * inch
        barcode_height = 0.5 * inch
        margin = 0.5 * inch
        spacing = 0.3 * inch
        
        # Calculate layout
        items_per_row = 3
        item_height = qr_size + (barcode_height if include_barcode else 0) + 1 * inch  # Extra space for text
        
        x_positions = [margin + i * (width - 2*margin) / items_per_row for i in range(items_per_row)]
        
        current_item = 0
        y = height - margin - qr_size
        
        for item in items:
            if current_item > 0 and current_item % items_per_row == 0:
                y -= item_height
                if y < margin + item_height:
                    c.showPage()
                    y = height - margin - qr_size
            
            x = x_positions[current_item % items_per_row]
            
            # Draw QR code
            if item.qr_code_path and os.path.exists(item.qr_code_path):
                c.drawImage(item.qr_code_path, x, y, width=qr_size, height=qr_size)
            
            # Draw barcode if requested
            if include_barcode and item.barcode_path and os.path.exists(item.barcode_path):
                barcode_y = y - barcode_height - 0.1 * inch
                c.drawImage(item.barcode_path, x, barcode_y, width=barcode_width, height=barcode_height)
            
            # Add text information
            text_y = y - (barcode_height + 0.2 * inch if include_barcode else 0.1 * inch)
            c.setFont("Helvetica", 8)
            c.drawString(x, text_y - 12, f"Product: {product.name}")
            c.drawString(x, text_y - 24, f"Serial: {item.serial_number}")
            c.drawString(x, text_y - 36, f"Location: {item.location.title()}")
            
            current_item += 1
        
        c.save()
        return pdf_filename
    
    def check_and_create_restock_tasks(self):
        """Check for low stock and create restock tasks."""
        return self.todo_manager.check_low_stock_and_create_tasks()
    
    def move_warehouse_to_store(self, product_id, quantity):
        """Move items from warehouse to store and update quantities."""
        moved_items = self.db.move_items_warehouse_to_store(product_id, quantity)
        return moved_items
    
    def get_product_summary(self, product_id):
        """Get a summary of product with item counts by location."""
        product = self.db.get_product(product_id)
        if not product:
            return None
        
        store_items = self.db.get_product_items(product_id, location='store', status='in_stock')
        warehouse_items = self.db.get_product_items(product_id, location='warehouse', status='in_stock')
        sold_items = self.db.get_product_items(product_id, status='sold')
        
        return {
            'product': product,
            'store_count': len(store_items),
            'warehouse_count': len(warehouse_items),
            'sold_count': len(sold_items),
            'total_items': len(store_items) + len(warehouse_items) + len(sold_items)
        }
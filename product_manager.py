from datetime import datetime
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import os

class ProductManager:
    def __init__(self, db_manager):
        self.db = db_manager
        self.qr_code_dir = 'qr_codes'
        if not os.path.exists(self.qr_code_dir):
            os.makedirs(self.qr_code_dir)

    def generate_qr_code(self, product_id, item_number):
        """Generate QR code for a specific product item."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Create QR code data
        data = f"Product ID: {product_id}\nItem Number: {item_number}"
        qr.add_data(data)
        qr.make(fit=True)

        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code
        filename = f"{self.qr_code_dir}/product_{product_id}_item_{item_number}.png"
        qr_image.save(filename)
        return filename

    def add_product_with_items(self, product_data, quantity):
        """Add a new product with individual items and QR codes."""
        # Add the main product
        product = self.db.add_product(product_data)
        
        # Generate QR codes for each item
        qr_codes = []
        for i in range(quantity):
            item_number = i + 1
            qr_code_path = self.generate_qr_code(product.id, item_number)
            qr_codes.append({
                'product_id': product.id,
                'item_number': item_number,
                'qr_code_path': qr_code_path
            })
        
        return product, qr_codes

    def generate_qr_codes_pdf(self, product_id, start_item=1, end_item=None):
        """Generate a PDF containing QR codes for product items."""
        product = self.db.get_product(product_id)
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")

        if end_item is None:
            end_item = product.store_quantity

        # Create PDF
        pdf_filename = f"{self.qr_code_dir}/product_{product_id}_qrcodes.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=letter)
        width, height = letter

        # Layout settings
        qr_size = 2 * inch  # 2 inches for QR code
        margin = 0.5 * inch  # 0.5 inch margin
        spacing = 0.25 * inch  # 0.25 inch spacing
        
        # Calculate how many QR codes fit per row and column
        codes_per_row = int((width - 2*margin) / (qr_size + spacing))
        codes_per_col = int((height - 2*margin) / (qr_size + spacing))
        codes_per_page = codes_per_row * codes_per_col

        current_item = start_item
        while current_item <= end_item:
            # Reset position for new page
            x = margin
            y = height - margin - qr_size
            codes_on_page = 0

            while (codes_on_page < codes_per_page and current_item <= end_item):
                # Generate and place QR code
                qr_code_path = self.generate_qr_code(product_id, current_item)
                c.drawImage(qr_code_path, x, y, width=qr_size, height=qr_size)
                
                # Add item information below QR code
                c.setFont("Helvetica", 8)
                c.drawString(x, y - 12, f"Product: {product.name}")
                c.drawString(x, y - 24, f"Item #: {current_item}")

                # Update position
                x += qr_size + spacing
                if x + qr_size > width - margin:
                    x = margin
                    y -= qr_size + spacing + 0.5*inch  # Extra space for text
                    if y - qr_size < margin:
                        break

                current_item += 1
                codes_on_page += 1

            if current_item <= end_item:
                c.showPage()  # Start a new page

        c.save()
        return pdf_filename
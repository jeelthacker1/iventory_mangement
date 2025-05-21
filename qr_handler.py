import qrcode
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from datetime import datetime

class QRHandler:
    def __init__(self, qr_codes_dir='qr_codes'):
        self.qr_codes_dir = Path(qr_codes_dir)
        self.qr_codes_dir.mkdir(exist_ok=True)
        self.camera = None
       
    def generate_qr_code(self, product_id, product_name, quantity=1, serial_number=None):
        """Generate a QR code for a product and save it
        
        Args:
            product_id: The ID of the product
            product_name: The name of the product
            quantity: The quantity of the product (default: 1)
            serial_number: Unique serial number for the product unit (default: None)
        
        Returns:
            The path to the saved QR code image
        """
        # Generate a unique serial number if not provided
        if not serial_number:
            serial_number = f"SN{product_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Data format: product_id|product_name|quantity|serial_number
        qr.add_data(f"{product_id}|{product_name}|{quantity}|{serial_number}")
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code with serial number
        filename = f"product_{product_id}_{serial_number}.png"
        file_path = self.qr_codes_dir / filename
        qr_image.save(str(file_path))
        
        return str(file_path), serial_number
    
    def start_camera(self):
        """Initialize and start the camera"""
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            raise Exception("Could not open camera")
    
    def stop_camera(self):
        """Stop and release the camera"""
        if self.camera:
            self.camera.release()
            self.camera = None
    
    def scan_qr_code(self):
        """Scan QR code using the camera and return the decoded data"""
        if not self.camera:
            raise Exception("Camera not initialized")
        
        qr_decoder = cv2.QRCodeDetector()
        
        while True:
            ret, frame = self.camera.read()
            if not ret:
                continue
            
            # Try to detect and decode QR code
            try:
                data, bbox, _ = qr_decoder.detectAndDecode(frame)
                if data:
                    return data
            except Exception as e:
                print(f"Error decoding QR code: {e}")
                continue
            
            # Display the frame (optional)
            cv2.imshow('QR Code Scanner', frame)
            
            # Break loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        return None
    
    def generate_label(self, product_id, product_name, price):
        """Generate a printable label with QR code and product information"""
        # Create QR code
        qr_path = self.generate_qr_code(product_id, product_name)
        qr_image = Image.open(qr_path)
        
        # Create a new image with white background
        label_width = 400
        label_height = 200
        label = Image.new('RGB', (label_width, label_height), 'white')
        
        # Paste QR code
        qr_size = 150
        qr_image = qr_image.resize((qr_size, qr_size))
        label.paste(qr_image, (10, 25))
        
        # Add text information
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(label)
        
        # Use a default font
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Add product information
        text_x = qr_size + 30
        draw.text((text_x, 40), f"Name: {product_name}", fill='black', font=font)
        draw.text((text_x, 70), f"ID: {product_id}", fill='black', font=font)
        draw.text((text_x, 100), f"Price: ${price:.2f}", fill='black', font=font)
        
        # Save the label
        label_path = self.qr_codes_dir / f"label_{product_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        label.save(str(label_path))
        
        return str(label_path)
# Shop Inventory Management System

A comprehensive desktop application for managing shop inventory, processing sales through QR codes, and tracking business analytics.

## Features

- **Inventory Management**
  - Add, edit, and delete products
  - Track product quantities
  - Set reorder thresholds
  - Supplier information management

- **QR Code Integration**
  - Automatic QR code generation for products
  - QR code scanning for quick sales processing
  - Printable product labels with QR codes

- **Sales Processing**
  - Quick sales through QR code scanning
  - Customer information management
  - Loyalty program tracking
  - Receipt generation

- **Analytics and Reporting**
  - Sales reports (daily, weekly, monthly)
  - Inventory value tracking
  - Profit analysis
  - Low stock alerts

- **Customer Management**
  - Customer database
  - Purchase history tracking
  - Loyalty points system
  - Contact information management

## Installation

1. Ensure you have Python 3.8 or higher installed

2. Clone the repository:
   ```bash
   git clone [repository-url]
   cd inventory_management
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```bash
   python main.py
   ```

2. Navigate through different sections using the sidebar:
   - Dashboard: Overview of key metrics
   - Inventory: Manage products
   - Sales: Process sales transactions
   - Customers: Manage customer database
   - Reports: View analytics and reports
   - Low Stock: Monitor items needing reorder

## System Requirements

- Windows/Linux/MacOS
- Python 3.8 or higher
- Webcam for QR code scanning
- Minimum 4GB RAM
- 500MB free disk space

## Dependencies

- PyQt6: GUI framework
- SQLAlchemy: Database ORM
- OpenCV: Camera integration and QR scanning
- qrcode: QR code generation
- Pillow: Image processing
- pandas: Data analysis
- matplotlib: Data visualization

## Database

The application uses SQLite for data storage, with the following main tables:
- Products
- Customers
- Sales
- SaleItems
- Suppliers

## Security

- Local data storage for privacy
- User authentication system
- Regular automated backups
- Encrypted sensitive information

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
# Inventory Management System Setup Guide

## Database Installation and Setup

This application uses SQLite, which is already integrated into the system. No additional database installation is required.

### Database Features
- **Built-in SQLite**: Lightweight, serverless database that requires no configuration
- **SQLAlchemy ORM**: Object-Relational Mapping for easy database interactions
- **Automatic Schema Creation**: Tables are created automatically on first run

## Installation Steps

1. **Install Python Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   This will install all required packages including:
   - PyQt6 and PyQt6-Charts for the GUI and data visualization
   - SQLAlchemy for database management
   - OpenCV and qrcode for QR code functionality
   - Pandas and Matplotlib for data analysis

2. **Run the Application**

   ```bash
   python main.py
   ```

## Enhanced UI Features

The application has been designed with a modern, attractive interface:

- **Responsive Layout**: Adapts to different screen sizes
- **Modern Color Scheme**: Professional appearance with consistent branding
- **Intuitive Navigation**: Clear sidebar menu for easy access to all features
- **Interactive Charts**: Visual representation of sales and inventory data
- **Data Tables**: Clean, sortable tables for inventory and customer management

## Analytics and Reporting

The system includes comprehensive analytics features:

- **Dashboard Overview**: Key metrics at a glance
- **Sales Trends**: Interactive charts showing sales over time
- **Inventory Analysis**: Stock level visualization and product performance
- **Customer Insights**: Purchase history and loyalty program analytics
- **Exportable Reports**: Generate PDF and CSV reports for sharing

## Client Delivery Guide

### Packaging the Application

1. **Create a Distribution Package**

   For Windows clients:
   ```bash
   pip install pyinstaller
   pyinstaller --onefile --windowed main.py
   ```

   This creates a standalone executable in the `dist` folder.

2. **Prepare Documentation**

   Include the following documents:
   - User manual (README.md)
   - This setup guide
   - Sample data (if applicable)

3. **Delivery Options**

   - **Direct Installation**: Schedule an appointment to install and configure the system on the client's computer
   - **Remote Setup**: Provide the executable and guide the client through installation via video call
   - **Cloud Hosting**: For multi-user access, consider deploying to a cloud service

### Training and Support

1. **User Training**
   - Provide a walkthrough of all system features
   - Demonstrate daily operations (adding products, processing sales, etc.)
   - Show how to generate and interpret reports

2. **Ongoing Support**
   - Establish a support protocol (email, phone, etc.)
   - Set expectations for response times
   - Consider a maintenance agreement for updates and enhancements

## Backup and Recovery

1. **Database Backup**
   - The SQLite database file (inventory.db) contains all data
   - Recommend regular backups to an external drive or cloud storage
   - Automated backup script (optional):

   ```python
   # backup_script.py
   import shutil
   from datetime import datetime
   
   # Create a timestamped backup
   timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
   shutil.copy2("inventory.db", f"backup/inventory_{timestamp}.db")
   ```

2. **Recovery Procedure**
   - Replace the current inventory.db with the backup file
   - Restart the application

## System Requirements

- Windows 10 or newer
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space
- 1280x720 screen resolution or higher
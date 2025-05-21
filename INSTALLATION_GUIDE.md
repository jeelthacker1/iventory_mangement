# Inventory Management System Installation Guide

## Database Installation

This inventory management system uses SQLite, which is a serverless database engine that requires no separate installation. The database is automatically created and managed by the application.

### Benefits of SQLite

- **Zero Configuration**: No server setup or configuration required
- **Self-Contained**: The entire database is stored in a single file (inventory.db)
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Reliable**: ACID-compliant for data integrity

## Installation Steps

### 1. Install Python

If you don't have Python installed:

1. Download Python 3.8 or newer from [python.org](https://www.python.org/downloads/)
2. During installation, make sure to check "Add Python to PATH"

### 2. Install Required Dependencies

Open a command prompt or terminal in the application directory and run:

```bash
pip install -r requirements.txt
```

This will install all necessary packages including:
- PyQt6 and PyQt6-Charts for the GUI and data visualization
- SQLAlchemy for database management
- OpenCV and qrcode for QR code functionality
- Pandas and Matplotlib for data analysis

### 3. Run the Application

From the application directory, run:

```bash
python main.py
```

The application will start and automatically create the database file if it doesn't exist.

## Enhanced UI Features

The application has been designed with a modern, attractive interface:

- **Professional Color Scheme**: Clean, modern appearance with consistent branding
- **Intuitive Navigation**: Sidebar menu for easy access to all features
- **Interactive Charts**: Visual representation of sales and inventory data
- **Responsive Layout**: Adapts to different screen sizes

## Analytics and Reporting

The system includes comprehensive analytics features with chart-based visualizations:

### Available Charts

- **Sales Trend**: Track sales over time with line charts
- **Product Categories**: View product distribution with pie charts
- **Revenue by Day**: Analyze daily revenue patterns with bar charts
- **Profit Margin**: Compare product profitability with bar charts

### Report Features

- **Date Range Selection**: Generate reports for specific time periods
- **Export Options**: Save reports as CSV or PDF files
- **Tabular Data**: View detailed data alongside visual charts
- **Print Support**: Print reports directly from the application

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   - Error: "ModuleNotFoundError: No module named 'PyQt6'"
   - Solution: Run `pip install -r requirements.txt` again

2. **Database Access Error**
   - Error: "Unable to open database file"
   - Solution: Ensure you have write permissions in the application directory

3. **Camera Access**
   - Error: "Could not open camera"
   - Solution: Ensure your webcam is connected and not in use by another application

### Getting Help

If you encounter issues not covered in this guide:

1. Check the README.md file for additional information
2. Refer to the SETUP_GUIDE.md for more detailed configuration options
3. Contact technical support at your organization's IT department

## System Requirements

- **Operating System**: Windows 10/11, macOS 10.14+, or Linux
- **Processor**: 1.6 GHz or faster
- **Memory**: 4 GB RAM minimum (8 GB recommended)
- **Storage**: 500 MB free disk space
- **Display**: 1280x720 screen resolution or higher
- **Optional**: Webcam for QR code scanning
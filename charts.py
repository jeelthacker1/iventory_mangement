from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPainter
from PyQt6.QtCharts import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QPieSeries
from PyQt6.QtCharts import QLineSeries, QDateTimeAxis
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class ChartWidget(QWidget):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Chart selection
        selection_layout = QHBoxLayout()
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(['Sales Trend', 'Product Categories', 'Revenue by Day', 'Profit Margin'])
        self.chart_type_combo.currentIndexChanged.connect(self.update_chart)
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(['Last 7 Days', 'Last 30 Days', 'Last 90 Days', 'This Year'])
        self.period_combo.currentIndexChanged.connect(self.update_chart)
        
        selection_layout.addWidget(QLabel('Chart Type:'))
        selection_layout.addWidget(self.chart_type_combo)
        selection_layout.addWidget(QLabel('Period:'))
        selection_layout.addWidget(self.period_combo)
        selection_layout.addStretch()
        
        layout.addLayout(selection_layout)
        
        # Chart view
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        layout.addWidget(self.chart_view)
        
        # Initial chart
        self.update_chart()
    
    def update_chart(self):
        chart_type = self.chart_type_combo.currentText()
        period = self.period_combo.currentText()
        
        # Clear previous chart
        self.chart_view.chart().deleteLater() if self.chart_view.chart() else None
        
        # Create new chart based on selection
        if chart_type == 'Sales Trend':
            chart = self.create_sales_trend_chart(period)
        elif chart_type == 'Product Categories':
            chart = self.create_category_chart(period)
        elif chart_type == 'Revenue by Day':
            chart = self.create_revenue_chart(period)
        elif chart_type == 'Profit Margin':
            chart = self.create_profit_margin_chart(period)
        
        # Apply theme and set chart
        chart.setTheme(QChart.ChartTheme.ChartThemeBlueIcy)
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        self.chart_view.setChart(chart)
    
    def get_date_range(self, period):
        end_date = datetime.now()
        
        if period == 'Last 7 Days':
            start_date = end_date - timedelta(days=7)
        elif period == 'Last 30 Days':
            start_date = end_date - timedelta(days=30)
        elif period == 'Last 90 Days':
            start_date = end_date - timedelta(days=90)
        elif period == 'This Year':
            start_date = datetime(end_date.year, 1, 1)
        
        return start_date, end_date
    
    def create_sales_trend_chart(self, period):
        start_date, end_date = self.get_date_range(period)
        
        # Get sales data
        sales = self.db.get_sales_report(start_date, end_date)
        
        # Process data for chart
        if not sales:
            # Create empty chart if no data
            chart = QChart()
            chart.setTitle("No Sales Data Available")
            return chart
        
        # Group sales by date
        sales_by_date = {}
        for sale in sales:
            date_key = sale.sale_date.date()
            if date_key in sales_by_date:
                sales_by_date[date_key] += sale.total_amount
            else:
                sales_by_date[date_key] = sale.total_amount
        
        # Create line series
        series = QLineSeries()
        series.setName("Daily Sales")
        
        # Add data points
        dates = []
        for date, amount in sorted(sales_by_date.items()):
            # Convert to milliseconds since epoch for QDateTime
            timestamp = datetime.combine(date, datetime.min.time()).timestamp() * 1000
            series.append(timestamp, amount)
            dates.append(date)
        
        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"Sales Trend ({period})")
        
        # Create axes
        axis_x = QDateTimeAxis()
        axis_x.setFormat("MMM dd")
        axis_x.setTitleText("Date")
        
        axis_y = QValueAxis()
        axis_y.setLabelFormat("$%.2f")
        axis_y.setTitleText("Sales Amount")
        
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        
        return chart
    
    def create_category_chart(self, period):
        start_date, end_date = self.get_date_range(period)
        
        # Get all products
        products = self.db.get_all_products()
        
        # Group products by category
        categories = {}
        for product in products:
            category = product.category or "Uncategorized"
            if category in categories:
                categories[category] += 1
            else:
                categories[category] = 1
        
        # Create pie series
        series = QPieSeries()
        series.setHoleSize(0.35)  # Donut chart style
        
        # Add slices
        for category, count in categories.items():
            slice = series.append(f"{category} ({count})", count)
            slice.setLabelVisible(True)
        
        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"Product Categories")
        
        return chart
    
    def create_revenue_chart(self, period):
        start_date, end_date = self.get_date_range(period)
        
        # Get sales data
        sales = self.db.get_sales_report(start_date, end_date)
        
        # Process data for chart
        if not sales:
            chart = QChart()
            chart.setTitle("No Revenue Data Available")
            return chart
        
        # Group sales by day of week
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        revenue_by_day = {day: 0 for day in days_of_week}
        
        for sale in sales:
            day_name = days_of_week[sale.sale_date.weekday()]
            revenue_by_day[day_name] += sale.total_amount
        
        # Create bar set
        bar_set = QBarSet("Revenue")
        for day in days_of_week:
            bar_set.append(revenue_by_day[day])
        
        # Create bar series
        series = QBarSeries()
        series.append(bar_set)
        
        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"Revenue by Day of Week ({period})")
        
        # Create axes
        axis_x = QBarCategoryAxis()
        axis_x.append(days_of_week)
        
        axis_y = QValueAxis()
        axis_y.setLabelFormat("$%.2f")
        axis_y.setTitleText("Revenue")
        
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        
        return chart
    
    def create_profit_margin_chart(self, period):
        # Get all products
        products = self.db.get_all_products()
        
        # Calculate profit margins
        margins = []
        names = []
        
        # Get top 10 products by margin
        for product in products:
            if product.selling_price > 0 and product.purchase_price > 0:
                margin = (product.selling_price - product.purchase_price) / product.selling_price * 100
                margins.append((product.name, margin))
        
        # Sort by margin and take top 10
        margins.sort(key=lambda x: x[1], reverse=True)
        top_margins = margins[:10]
        
        # Create bar set
        bar_set = QBarSet("Profit Margin %")
        names = []
        
        for name, margin in top_margins:
            bar_set.append(margin)
            names.append(name[:10] + '...' if len(name) > 10 else name)  # Truncate long names
        
        # Create bar series
        series = QBarSeries()
        series.append(bar_set)
        
        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Top 10 Products by Profit Margin")
        
        # Create axes
        axis_x = QBarCategoryAxis()
        axis_x.append(names)
        
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%.1f%%")
        axis_y.setTitleText("Profit Margin")
        
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        
        return chart
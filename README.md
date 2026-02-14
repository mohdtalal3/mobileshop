# 📱 Mobile Shop - Inventory & Sales Management System

A comprehensive Flask-based web application for managing inventory, sales, expenses, and revenue for a mobile phone shop.

## 🚀 Features

### 1️⃣ **Inventory Management**
- Add, edit, and delete inventory items
- Track mobile phones, chargers, cables, earphones, and accessories
- Automatic calculation of total purchase cost
- Real-time stock level monitoring
- Low stock and out-of-stock alerts

### 2️⃣ **Sales Management**
- Record sales with search functionality
- Automatic inventory quantity updates
- Profit calculation per sale
- Prevent overselling (stock validation)
- Sales history with filtering

### 3️⃣ **Expense Management**
- Track various expense categories (rent, electricity, salaries, etc.)
- Date-based expense tracking
- Category-wise expense breakdown
- Monthly and custom date range summaries

### 4️⃣ **Revenue & Profit Tracking**
- Total sales revenue calculation
- Gross profit computation
- Net profit (profit - expenses)
- Category-wise sales analysis
- Monthly and custom date filtering

### 5️⃣ **Interactive Dashboard**
- KPI cards showing key metrics
- Monthly sales chart (last 12 months)
- Monthly profit chart
- Revenue vs Expenses comparison chart
- Recent sales table
- Low stock alerts

### 6️⃣ **Business Reports**
- Daily sales reports
- Category-wise inventory reports
- Top 10 selling items
- Custom date range filtering

## 🛠️ Technology Stack

- **Backend**: Python 3.x, Flask
- **Database**: SQLite3 with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Charts**: Chart.js
- **Icons**: Bootstrap Icons

## 📦 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Clone or Download the Project
```bash
cd ~/Desktop/areeb
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will:
- Create the SQLite database (`inventory.db`)
- Create default admin user
- Start the development server on `http://localhost:5000`

### Step 5: Access the Application
1. Open your web browser
2. Navigate to: `http://localhost:5000`
3. Login with default credentials:
   - **Username**: `admin`
   - **Password**: `admin123`

## 📁 Project Structure

```
areeb/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── inventory.db               # SQLite database (auto-created)
├── static/
│   └── css/
│       └── style.css          # Custom CSS styles
└── templates/
    ├── base.html              # Base template with navigation
    ├── login.html             # Login page
    ├── dashboard.html         # Dashboard with charts & KPIs
    ├── inventory.html         # Inventory listing
    ├── add_inventory.html     # Add inventory item
    ├── edit_inventory.html    # Edit inventory item
    ├── sales.html             # Sales listing
    ├── add_sale.html          # Record new sale
    ├── expenses.html          # Expenses listing
    ├── add_expense.html       # Add new expense
    ├── revenue.html           # Revenue & net profit page
    └── reports.html           # Business reports
```

## 🗄️ Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique)
- `password_hash`
- `created_at`

### Inventory Table
- `id` (Primary Key)
- `item_name`
- `category`
- `purchase_price`
- `quantity`
- `supplier`
- `added_date`

### Sales Table
- `id` (Primary Key)
- `inventory_id` (Foreign Key)
- `quantity_sold`
- `selling_price`
- `sale_date`

### Expenses Table
- `id` (Primary Key)
- `title`
- `category`
- `amount`
- `expense_date`

## 🎯 Usage Guide

### Adding Inventory Items
1. Navigate to **Inventory** → **Add New Item**
2. Fill in item details (name, category, price, quantity, supplier)
3. System automatically calculates total purchase cost
4. Click **Add Item**

### Recording Sales
1. Navigate to **Sales** → **Record New Sale**
2. Search for the item using the search box
3. Select the item from search results
4. Enter quantity and selling price
5. System shows real-time profit calculation
6. Click **Record Sale** (inventory auto-updates)

### Managing Expenses
1. Navigate to **Expenses** → **Add New Expense**
2. Enter expense details (title, category, amount, date)
3. Click **Add Expense**
4. View expense breakdown by category

### Viewing Reports
- **Dashboard**: Overview with KPIs and charts
- **Revenue**: Detailed revenue, profit, and expense analysis
- **Reports**: Daily sales, category analysis, top selling items

### Date Filtering
- Use date range pickers on Dashboard, Revenue, and Reports pages
- Filter data for specific periods (daily, monthly, custom range)

## 🔒 Security Notes

⚠️ **Important**: This is a development version. For production use:

1. **Change the secret key** in `app.py`:
   ```python
   app.config['SECRET_KEY'] = 'your-secure-random-secret-key'
   ```

2. **Change default admin password**:
   - Login and create a new admin user
   - Delete the default admin account

3. **Use HTTPS** in production
4. **Enable database backups**
5. **Use environment variables** for sensitive data

## 🎨 UI Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern Interface**: Clean cards and soft colors
- **Sidebar Navigation**: Easy access to all modules
- **Flash Messages**: User feedback for all actions
- **Interactive Charts**: Visual data representation
- **Real-time Calculations**: Instant profit/cost calculations
- **Search Functionality**: Quick item lookup for sales

## 📊 Key Features Explained

### Automatic Inventory Updates
- When a sale is recorded, inventory quantity automatically decreases
- Prevents selling more than available stock
- Shows real-time stock levels

### Profit Calculation
- **Per Sale**: (Selling Price - Purchase Price) × Quantity
- **Gross Profit**: Sum of all sales profits
- **Net Profit**: Gross Profit - Total Expenses

### Low Stock Alerts
- Items with quantity ≤ 10 show **Low Stock** badge
- Items with quantity = 0 show **Out of Stock** badge
- Dashboard displays low stock items table

### Monthly Charts
- Sales trend over last 12 months
- Profit trend over last 12 months
- Revenue vs Expenses comparison

## 🔧 Troubleshooting

### Database Issues
```bash
# Delete database and restart (loses all data)
rm inventory.db
python app.py
```

### Port Already in Use
```python
# Change port in app.py (last line)
app.run(debug=True, port=5001)  # Change 5000 to 5001
```

### Missing Dependencies
```bash
pip install --upgrade -r requirements.txt
```

## 🚀 Future Enhancements (Optional)

- [ ] Multi-user support with roles (admin, staff)
- [ ] Barcode scanning for inventory
- [ ] PDF report generation
- [ ] Email notifications for low stock
- [ ] Customer management module
- [ ] Invoice generation
- [ ] Data export (CSV, Excel)
- [ ] Advanced analytics dashboard
- [ ] Mobile app version

## 📝 License

This project is open source and available for personal and commercial use.

## 👨‍💻 Developer

Built with ❤️ using Flask, SQLAlchemy, Bootstrap, and Chart.js

## 📞 Support

For issues or questions, please check the code comments or refer to:
- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Bootstrap Documentation: https://getbootstrap.com/docs/5.3/
- Chart.js Documentation: https://www.chartjs.org/docs/

---

**Happy Managing! 📱💼**

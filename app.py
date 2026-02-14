from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import func, extract
import os
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

app = Flask(
    __name__,
    template_folder=resource_path("templates"),
    static_folder=resource_path("static")
)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + resource_path('inventory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    supplier = db.Column(db.String(200))
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    sales = db.relationship('Sale', backref='inventory_item', lazy=True, cascade='all, delete-orphan')

    @property
    def total_purchase_cost(self):
        return self.purchase_price * self.quantity

    @property
    def is_low_stock(self):
        return self.quantity <= 10  # Low stock threshold

    @property
    def is_out_of_stock(self):
        return self.quantity == 0


class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default='Cash')
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def total_selling_price(self):
        return self.selling_price * self.quantity_sold

    @property
    def profit(self):
        item = Inventory.query.get(self.inventory_id)
        if item:
            return (self.selling_price - item.purchase_price) * self.quantity_sold
        return 0


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    expense_date = db.Column(db.DateTime, default=datetime.utcnow)


class EasyPaisa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(50), nullable=False)  # Withdraw or Transfer
    client_name = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    profit_amount = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def net_amount(self):
        return self.total_amount - self.profit_amount


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Routes
@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Get date range from query params
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Default to current month
    if not start_date or not end_date:
        today = datetime.now()
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    
    # KPIs
    total_inventory_value = db.session.query(
        func.sum(Inventory.purchase_price * Inventory.quantity)
    ).scalar() or 0
    
    total_sales = db.session.query(
        func.sum(Sale.selling_price * Sale.quantity_sold)
    ).filter(Sale.sale_date.between(start_dt, end_dt)).scalar() or 0
    
    # Calculate total profit
    sales_in_range = Sale.query.filter(Sale.sale_date.between(start_dt, end_dt)).all()
    total_profit = sum([sale.profit for sale in sales_in_range])
    
    total_expenses = db.session.query(
        func.sum(Expense.amount)
    ).filter(Expense.expense_date.between(start_dt, end_dt)).scalar() or 0
    
    net_profit = total_profit - total_expenses
    
    # Recent sales
    recent_sales = Sale.query.order_by(Sale.sale_date.desc()).limit(10).all()
    
    # Low stock items
    low_stock_items = Inventory.query.filter(Inventory.quantity <= 10).all()
    
    # Chart data - Monthly sales for last 12 months
    monthly_sales_data = []
    monthly_profit_data = []
    monthly_expense_data = []
    months_labels = []
    
    for i in range(11, -1, -1):
        month_start = (datetime.now().replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
        month_sales = db.session.query(
            func.sum(Sale.selling_price * Sale.quantity_sold)
        ).filter(Sale.sale_date.between(month_start, month_end)).scalar() or 0
        
        month_sales_list = Sale.query.filter(Sale.sale_date.between(month_start, month_end)).all()
        month_profit = sum([sale.profit for sale in month_sales_list])
        
        month_expenses = db.session.query(
            func.sum(Expense.amount)
        ).filter(Expense.expense_date.between(month_start, month_end)).scalar() or 0
        
        monthly_sales_data.append(round(month_sales, 2))
        monthly_profit_data.append(round(month_profit, 2))
        monthly_expense_data.append(round(month_expenses, 2))
        months_labels.append(month_start.strftime('%b %Y'))
    
    return render_template('dashboard.html',
                         total_inventory_value=total_inventory_value,
                         total_sales=total_sales,
                         total_profit=total_profit,
                         total_expenses=total_expenses,
                         net_profit=net_profit,
                         recent_sales=recent_sales,
                         low_stock_items=low_stock_items,
                         monthly_sales_data=monthly_sales_data,
                         monthly_profit_data=monthly_profit_data,
                         monthly_expense_data=monthly_expense_data,
                         months_labels=months_labels,
                         start_date=start_date,
                         end_date=end_date)


@app.route('/inventory')
@login_required
def inventory():
    # Get search and filter parameters
    search_query = request.args.get('search', '').strip()
    show_low_stock = request.args.get('low_stock', '')
    
    # Base query
    query = Inventory.query
    
    # Apply search filter
    if search_query:
        query = query.filter(
            db.or_(
                Inventory.item_name.ilike(f'%{search_query}%'),
                Inventory.category.ilike(f'%{search_query}%'),
                Inventory.supplier.ilike(f'%{search_query}%')
            )
        )
    
    # Apply low stock filter
    if show_low_stock == 'true':
        query = query.filter(Inventory.quantity <= 10)
    
    items = query.order_by(Inventory.added_date.desc()).all()
    return render_template('inventory.html', items=items, search_query=search_query, show_low_stock=show_low_stock)


@app.route('/inventory/add', methods=['GET', 'POST'])
@login_required
def add_inventory():
    if request.method == 'POST':
        item = Inventory(
            item_name=request.form.get('item_name'),
            category=request.form.get('category'),
            purchase_price=float(request.form.get('purchase_price')),
            quantity=int(request.form.get('quantity')),
            supplier=request.form.get('supplier')
        )
        db.session.add(item)
        db.session.commit()
        flash('Item added successfully!', 'success')
        return redirect(url_for('inventory'))
    
    return render_template('add_inventory.html')


@app.route('/inventory/quick-add')
@login_required
def quick_add_inventory():
    return render_template('quick_add_inventory.html')


@app.route('/inventory/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_inventory(id):
    item = Inventory.query.get_or_404(id)
    
    if request.method == 'POST':
        item.item_name = request.form.get('item_name')
        item.category = request.form.get('category')
        item.purchase_price = float(request.form.get('purchase_price'))
        item.quantity = int(request.form.get('quantity'))
        item.supplier = request.form.get('supplier')
        
        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('inventory'))
    
    return render_template('edit_inventory.html', item=item)


@app.route('/inventory/delete/<int:id>')
@login_required
def delete_inventory(id):
    item = Inventory.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('inventory'))


@app.route('/sales')
@login_required
def sales():
    # Get date filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Default to today if no dates provided
    if not start_date or not end_date:
        today = datetime.now().strftime('%Y-%m-%d')
        start_date = today
        end_date = today
    
    # Base query
    query = Sale.query
    
    # Apply date filters
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        query = query.filter(Sale.sale_date.between(start_dt, end_dt))
    except ValueError:
        flash('Invalid date format. Please use YYYY-MM-DD.', 'warning')
    
    all_sales = query.order_by(Sale.sale_date.desc()).all()
    
    # Calculate payment method totals
    cash_total = sum([sale.total_selling_price for sale in all_sales if sale.payment_method == 'Cash'])
    other_total = sum([sale.total_selling_price for sale in all_sales if sale.payment_method != 'Cash'])
    
    return render_template('sales.html', sales=all_sales, start_date=start_date, end_date=end_date,
                         cash_total=cash_total, other_total=other_total)


@app.route('/sales/add', methods=['GET', 'POST'])
@login_required
def add_sale():
    if request.method == 'POST':
        inventory_id = int(request.form.get('inventory_id'))
        quantity_sold = int(request.form.get('quantity_sold'))
        selling_price = float(request.form.get('selling_price'))
        
        item = Inventory.query.get_or_404(inventory_id)
        
        if item.quantity < quantity_sold:
            flash('Insufficient stock! Available quantity: {}'.format(item.quantity), 'danger')
            return redirect(url_for('add_sale'))
        
        # Create sale
        sale = Sale(
            inventory_id=inventory_id,
            quantity_sold=quantity_sold,
            selling_price=selling_price,
            payment_method=request.form.get('payment_method', 'Cash')
        )
        
        # Update inventory
        item.quantity -= quantity_sold
        
        db.session.add(sale)
        db.session.commit()
        
        flash('Sale recorded successfully!', 'success')
        return redirect(url_for('sales'))
    
    inventory_items = Inventory.query.filter(Inventory.quantity > 0).all()
    return render_template('add_sale.html', inventory_items=inventory_items)


@app.route('/api/inventory/add', methods=['POST'])
@login_required
def api_add_inventory():
    try:
        data = request.get_json()
        item = Inventory(
            item_name=data.get('item_name'),
            category=data.get('category'),
            purchase_price=float(data.get('purchase_price', 0)),
            quantity=int(data.get('quantity', 0)),
            supplier=data.get('supplier', '')
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Item added successfully!',
            'item': {
                'id': item.id,
                'item_name': item.item_name,
                'category': item.category,
                'purchase_price': item.purchase_price,
                'quantity': item.quantity,
                'supplier': item.supplier,
                'added_date': item.added_date.strftime('%Y-%m-%d')
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@app.route('/api/inventory/search')
@login_required
def search_inventory():
    query = request.args.get('q', '')
    items = Inventory.query.filter(
        Inventory.item_name.ilike(f'%{query}%')
    ).filter(Inventory.quantity > 0).all()
    
    return jsonify([{
        'id': item.id,
        'name': item.item_name,
        'category': item.category,
        'quantity': item.quantity,
        'purchase_price': item.purchase_price
    } for item in items])


@app.route('/expenses')
@login_required
def expenses():
    all_expenses = Expense.query.order_by(Expense.expense_date.desc()).all()
    return render_template('expenses.html', expenses=all_expenses)


@app.route('/expenses/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        expense = Expense(
            title=request.form.get('title'),
            category=request.form.get('category'),
            amount=float(request.form.get('amount')),
            expense_date=datetime.strptime(request.form.get('expense_date'), '%Y-%m-%d')
        )
        db.session.add(expense)
        db.session.commit()
        flash('Expense added successfully!', 'success')
        return redirect(url_for('expenses'))
    
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('add_expense.html', today=today)


@app.route('/expenses/delete/<int:id>')
@login_required
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('expenses'))


@app.route('/revenue')
@login_required
def revenue():
    # Get date range
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        today = datetime.now()
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    
    # Calculate revenue
    total_revenue = db.session.query(
        func.sum(Sale.selling_price * Sale.quantity_sold)
    ).filter(Sale.sale_date.between(start_dt, end_dt)).scalar() or 0
    
    # Calculate profit
    sales_in_range = Sale.query.filter(Sale.sale_date.between(start_dt, end_dt)).all()
    total_profit = sum([sale.profit for sale in sales_in_range])
    
    # Calculate expenses
    total_expenses = db.session.query(
        func.sum(Expense.amount)
    ).filter(Expense.expense_date.between(start_dt, end_dt)).scalar() or 0
    
    # Net profit
    net_profit = total_profit - total_expenses
    
    # Category wise sales
    category_sales = db.session.query(
        Inventory.category,
        func.sum(Sale.quantity_sold * Sale.selling_price).label('total')
    ).join(Sale).filter(Sale.sale_date.between(start_dt, end_dt)).group_by(Inventory.category).all()
    
    return render_template('revenue.html',
                         total_revenue=total_revenue,
                         total_profit=total_profit,
                         total_expenses=total_expenses,
                         net_profit=net_profit,
                         category_sales=category_sales,
                         start_date=start_date,
                         end_date=end_date)


@app.route('/reports')
@login_required
def reports():
    # Get date range
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        today = datetime.now()
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    
    # Daily sales with purchase cost and profit
    sales_in_range = Sale.query.filter(Sale.sale_date.between(start_dt, end_dt)).all()
    
    # Group sales by date
    daily_sales_dict = {}
    for sale in sales_in_range:
        sale_date = sale.sale_date.date()
        if sale_date not in daily_sales_dict:
            daily_sales_dict[sale_date] = {
                'date': sale_date,
                'num_sales': 0,
                'total_sales': 0,
                'total_purchase': 0,
                'total_profit': 0
            }
        daily_sales_dict[sale_date]['num_sales'] += 1
        daily_sales_dict[sale_date]['total_sales'] += sale.total_selling_price
        daily_sales_dict[sale_date]['total_purchase'] += sale.inventory_item.purchase_price * sale.quantity_sold
        daily_sales_dict[sale_date]['total_profit'] += sale.profit
    
    # Convert to list and sort by date
    daily_sales = [daily_sales_dict[date] for date in sorted(daily_sales_dict.keys())]
    
    # Category wise inventory
    category_inventory = db.session.query(
        Inventory.category,
        func.count(Inventory.id).label('num_items'),
        func.sum(Inventory.quantity).label('total_quantity'),
        func.sum(Inventory.purchase_price * Inventory.quantity).label('total_value')
    ).group_by(Inventory.category).all()
    
    # Top selling items
    top_items = db.session.query(
        Inventory.item_name,
        func.sum(Sale.quantity_sold).label('total_sold'),
        func.sum(Sale.selling_price * Sale.quantity_sold).label('total_revenue')
    ).join(Sale).filter(Sale.sale_date.between(start_dt, end_dt)).group_by(Inventory.item_name).order_by(func.sum(Sale.quantity_sold).desc()).limit(10).all()
    
    return render_template('reports.html',
                         daily_sales=daily_sales,
                         category_inventory=category_inventory,
                         top_items=top_items,
                         start_date=start_date,
                         end_date=end_date)


@app.route('/easypaisa')
@login_required
def easypaisa():
    # Get date filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    report_type = request.args.get('report_type', 'daily')
    
    # Default to today if no dates provided
    if not start_date or not end_date:
        today = datetime.now()
        if report_type == 'monthly':
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
        else:
            start_date = today.strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
    
    # Base query
    query = EasyPaisa.query
    
    # Apply date filters
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        query = query.filter(EasyPaisa.transaction_date.between(start_dt, end_dt))
    except ValueError:
        flash('Invalid date format. Please use YYYY-MM-DD.', 'warning')
    
    all_transactions = query.order_by(EasyPaisa.transaction_date.desc()).all()
    
    # Calculate totals
    total_amount = sum([t.total_amount for t in all_transactions])
    total_profit = sum([t.profit_amount for t in all_transactions])
    withdraw_count = len([t for t in all_transactions if t.transaction_type == 'Withdraw'])
    transfer_count = len([t for t in all_transactions if t.transaction_type == 'Transfer'])
    
    # Group by date for daily report
    daily_report = {}
    for trans in all_transactions:
        trans_date = trans.transaction_date.date()
        if trans_date not in daily_report:
            daily_report[trans_date] = {
                'date': trans_date,
                'count': 0,
                'total_amount': 0,
                'total_profit': 0
            }
        daily_report[trans_date]['count'] += 1
        daily_report[trans_date]['total_amount'] += trans.total_amount
        daily_report[trans_date]['total_profit'] += trans.profit_amount
    
    daily_data = [daily_report[date] for date in sorted(daily_report.keys(), reverse=True)]
    
    return render_template('easypaisa.html', 
                         transactions=all_transactions,
                         start_date=start_date, 
                         end_date=end_date,
                         report_type=report_type,
                         total_amount=total_amount,
                         total_profit=total_profit,
                         withdraw_count=withdraw_count,
                         transfer_count=transfer_count,
                         daily_data=daily_data)


@app.route('/easypaisa/add', methods=['GET', 'POST'])
@login_required
def add_easypaisa():
    if request.method == 'POST':
        transaction = EasyPaisa(
            transaction_type=request.form.get('transaction_type'),
            client_name=request.form.get('client_name'),
            phone_number=request.form.get('phone_number'),
            total_amount=float(request.form.get('total_amount')),
            profit_amount=float(request.form.get('profit_amount'))
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Easy Paisa transaction added successfully!', 'success')
        return redirect(url_for('easypaisa'))
    
    return render_template('add_easypaisa.html')


@app.route('/easypaisa/delete/<int:id>')
@login_required
def delete_easypaisa(id):
    transaction = EasyPaisa.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('easypaisa'))


def init_db():
    """Initialize database and create admin user if not exists"""
    with app.app_context():
        db.create_all()
        
        # Create admin user if doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username=admin, password=admin123")


if __name__ == '__main__':
    init_db()
    app.run(debug=False, port=5000)

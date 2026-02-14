# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Option 1: Using the Start Script (macOS/Linux)

```bash
# Make the script executable
chmod +x start.sh

# Run the script
./start.sh
```

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

## 🌐 Access the Application

1. Open your browser
2. Go to: **http://localhost:5000**
3. Login with:
   - Username: `admin`
   - Password: `admin123`

## 📚 First Steps After Login

1. **Add Inventory Items**
   - Go to Inventory → Add New Item
   - Add some products (phones, accessories, etc.)

2. **Record Sales**
   - Go to Sales → Record New Sale
   - Search for items and record transactions

3. **Add Expenses**
   - Go to Expenses → Add New Expense
   - Record shop expenses (rent, electricity, etc.)

4. **View Dashboard**
   - Check KPIs, charts, and analytics
   - Use date filters for custom reports

## 🛑 Stop the Application

Press `Ctrl + C` in the terminal

## 🔄 Restart the Application

```bash
source venv/bin/activate  # Activate venv first
python app.py
```

## ❓ Common Issues

**Port already in use?**
- Edit `app.py` and change port from 5000 to another (e.g., 5001)

**Database error?**
- Delete `inventory.db` file and restart

**Module not found?**
- Reinstall: `pip install -r requirements.txt`

---

**Need help?** Check the full README.md for detailed documentation.

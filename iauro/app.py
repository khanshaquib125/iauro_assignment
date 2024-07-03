from flask import Flask, render_template, redirect, url_for, flash, session, request
from functools import wraps
from datetime import datetime
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Path to JSON files
USERS_FILE = 'users.json'
EXPENSES_FILE = 'expenses.json'

# Check if JSON files exist, if not create them
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump({}, f)

if not os.path.exists(EXPENSES_FILE):
    with open(EXPENSES_FILE, 'w') as f:
        json.dump({}, f)

# Load users and expenses from JSON files
with open(USERS_FILE, 'r') as f:
    users = json.load(f)

with open(EXPENSES_FILE, 'r') as f:
    expenses = json.load(f)

# Helper function for login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    user_expenses = expenses.get(session['username'], [])
    return render_template('index.html', expenses=user_expenses)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('Username already exists. Please choose a different one.', 'danger')
        else:
            users[username] = password
            expenses[username] = []
            save_users()
            save_expenses()
            flash('Your account has been created!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users or users[username] != password:
            flash('Login Unsuccessful. Please check username and password', 'danger')
        else:
            session['username'] = username
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        category = request.form['category']
        amount = float(request.form['amount'])
        comments = request.form.get('comments', '')
        new_expense = {
            'category': category,
            'amount': amount,
            'comments': comments,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        expenses[session['username']].append(new_expense)
        save_expenses()
        flash('Your expense has been added!', 'success')
        return redirect(url_for('index'))
    return render_template('add_expense.html')

@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    user_expenses = expenses[session['username']]
    expense = user_expenses[expense_id]
    if request.method == 'POST':
        expense['category'] = request.form['category']
        expense['amount'] = float(request.form['amount'])
        expense['comments'] = request.form.get('comments', '')
        expense['updated_at'] = datetime.utcnow().isoformat()
        save_expenses()
        flash('Your expense has been updated!', 'success')
        return redirect(url_for('index'))
    return render_template('edit_expense.html', expense=expense, expense_id=expense_id)

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    user_expenses = expenses[session['username']]
    user_expenses.pop(expense_id)
    save_expenses()
    flash('Your expense has been deleted!', 'success')
    return redirect(url_for('index'))

# Helper functions to save users and expenses to JSON files
def save_users():
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def save_expenses():
    with open(EXPENSES_FILE, 'w') as f:
        json.dump(expenses, f)

if __name__ == '__main__':
    app.run(debug=True, port=5001)

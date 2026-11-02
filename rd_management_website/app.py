from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'rd_management.db'
app = Flask(__name__)
app.secret_key = 'change-this-local-demo-key'


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            monthly_deposit REAL NOT NULL,
            annual_rate REAL NOT NULL,
            term_months INTEGER NOT NULL,
            start_date TEXT NOT NULL
        )''')


def maturity_value(monthly, annual_rate, months):
    # Approximate recurring deposit maturity: monthly deposits at month-end.
    r = annual_rate / 1200
    if r == 0:
        return monthly * months
    return monthly * (((1 + r) ** months - 1) / r)


@app.route('/')
def dashboard():
    with connect_db() as conn:
        accounts = conn.execute('SELECT * FROM accounts ORDER BY id DESC').fetchall()
        total_accounts = conn.execute('SELECT COUNT(*) FROM accounts').fetchone()[0]
        monthly_total = conn.execute('SELECT COALESCE(SUM(monthly_deposit), 0) FROM accounts').fetchone()[0]
        invested_total = conn.execute('SELECT COALESCE(SUM(monthly_deposit * term_months), 0) FROM accounts').fetchone()[0]
    projected = sum(maturity_value(a['monthly_deposit'], a['annual_rate'], a['term_months']) for a in accounts)
    return render_template('index.html', accounts=accounts, total_accounts=total_accounts,
                           monthly_total=monthly_total, invested_total=invested_total,
                           projected=projected, today=date.today().isoformat(), maturity_value=maturity_value)


@app.route('/accounts/new', methods=['POST'])
def create_account():
    name = request.form.get('customer_name', '').strip()
    phone = request.form.get('phone', '').strip()
    try:
        monthly = float(request.form.get('monthly_deposit', '0'))
        rate = float(request.form.get('annual_rate', '0'))
        months = int(request.form.get('term_months', '0'))
    except ValueError:
        flash('Please enter valid numbers for deposit, rate, and term.', 'error')
        return redirect(url_for('dashboard'))
    if not name or not phone or monthly <= 0 or rate < 0 or months not in (6, 12, 24, 36, 60, 120):
        flash('Check the customer details and choose a valid deposit amount, rate, and term.', 'error')
        return redirect(url_for('dashboard'))
    with connect_db() as conn:
        conn.execute('INSERT INTO accounts (customer_name, phone, monthly_deposit, annual_rate, term_months, start_date) VALUES (?, ?, ?, ?, ?, ?)',
                     (name, phone, monthly, rate, months, date.today().isoformat()))
    flash(f'Recurring deposit account created for {name}.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/accounts/<int:account_id>/delete', methods=['POST'])
def delete_account(account_id):
    with connect_db() as conn:
        conn.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
    flash('Account deleted.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/calculator', methods=['POST'])
def calculator():
    try:
        monthly = float(request.form.get('calc_monthly', '0'))
        rate = float(request.form.get('calc_rate', '0'))
        months = int(request.form.get('calc_months', '0'))
        if monthly <= 0 or rate < 0 or months <= 0:
            raise ValueError
        estimate = maturity_value(monthly, rate, months)
        invested = monthly * months
        interest = estimate - invested
        flash(f"Estimate: maturity ₹{estimate:,.2f} · deposits ₹{invested:,.2f} · estimated interest ₹{interest:,.2f}", 'success')
    except ValueError:
        flash('Enter valid positive values in the calculator.', 'error')
    return redirect(url_for('dashboard') + '#calculator')


init_db()
if __name__ == '__main__':
    app.run(debug=True)

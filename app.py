from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from flask_login import login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config.from_object('config.Config')

mysql = MySQL(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users(first_name, last_name, email, password) VALUES(%s, %s, %s, %s)", 
                       (first_name, last_name, email, password))
        mysql.connection.commit()
        cursor.close()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            login_user(User(user[0]))
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/home')
@login_required
def home():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM expenses WHERE user_id=%s", (current_user.id,))
    expenses = cursor.fetchall()

    # Fetch categories for later use
    cursor.execute("SELECT id, name FROM categories")
    categories = cursor.fetchall()

    cursor.close()
    return render_template('home.html', expenses=expenses, categories=categories)

@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        amount = request.form['amount']
        category_id = request.form['category-id']
        date = request.form['date']
        
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO expenses(amount, category_id, date, user_id) VALUES(%s, %s, %s, %s)", 
                       (amount, category_id, date, current_user.id))
        mysql.connection.commit()
        cursor.close()
        
        flash('Expense added successfully!', 'success')
        return redirect(url_for('home'))
    
    # Fetch categories for dropdown selection (assuming categories are already populated)
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    cursor.close()

    return render_template('add_expense.html', categories=categories)

@app.route('/edit_expense/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_expense(id):
    cursor = mysql.connection.cursor()
    
    if request.method == 'POST':
        amount = request.form['amount']
        category_id = request.form['category_id']
        
        cursor.execute("UPDATE expenses SET amount=%s, category_id=%s WHERE id=%s", 
                       (amount, category_id, id))
        mysql.connection.commit()
        cursor.close()
        
        flash('Expense updated successfully!', 'success')
        return redirect(url_for('home'))
    
    # Fetch expense details and categories for editing
    cursor.execute("SELECT * FROM expenses WHERE id=%s", (id,))
    expense = cursor.fetchone()

    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()

    cursor.close()
    
    return render_template('edit_expense.html', expense=expense, categories=categories)

@app.route('/delete_expense/<int:id>')
@login_required
def delete_expense(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=%s", (id,))
    mysql.connection.commit()
    cursor.close()
    
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/report')
@login_required
def report():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT category_id, SUM(amount) as total FROM expenses WHERE user_id=%s GROUP BY category_id", 
                   (current_user.id,))
    
    report_data = []
    
    for row in cursor.fetchall():
        category_cursor = mysql.connection.cursor()
        category_cursor.execute("SELECT name FROM categories WHERE id=%s", (row[0],))
        category_name = category_cursor.fetchone()[0]
        
        report_data.append((category_name, row[1]))
    
    cursor.close()
    
    return render_template('report.html', report_data=report_data)

if __name__ == '__main__':
    app.run(debug=True)
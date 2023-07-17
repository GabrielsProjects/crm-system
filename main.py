from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

app.debug = True

# Configure secret key for session
app.secret_key = "secret"

# Route for login screen
@app.route('/')
def login():
    return render_template('login.html')

# Route for handling login form submission
@app.route('/login', methods=['POST'])
def login_submit():
    username = request.form['username']
    password = request.form['password']

    # Connect to the database
    conn = sqlite3.connect('db/users.db')
    cursor = conn.cursor()

    # Check if the username and password match in the database
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    if user:
        # If login successful, store username in session
        session['username'] = username
        conn.close()
        return redirect('/home')
    else:
        conn.close()
        return render_template('login.html', error_message='Username/password not found')

    # If login successful, store username in session
    session['username'] = username

    return redirect('/home')

# Route for homepage
@app.route('/home')
def home():
    conn = sqlite3.connect('db/customers.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM customers')
    customers = cursor.fetchall()
    conn.close()

    if 'username' in session:
        username = session['username']
        return render_template('home.html', username=username, customers=customers)
    else:
        return redirect('/')

# Route for Reports
@app.route('/reports')
def reports():
    conn = sqlite3.connect('db/customers.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM customers')
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('reports.html', rows=rows)

# Route for Collaboration Tools
@app.route('/collaboration-tools')
def collaboration_tools():
    return render_template('collaboration_tools.html')

# Route for Sales Dashboard
@app.route('/sales-dashboard')
def sales_dashboard():
    # Connect to the database
    conn = sqlite3.connect('db/customers.db')
    cursor = conn.cursor()

    # Query for average sales per month
    cursor.execute("""
        SELECT strftime('%Y-%m', SalesDate) AS month, AVG(TotalSales) AS average_sales
        FROM sales
        GROUP BY month
        ORDER BY month
    """)
    average_sales_per_month = cursor.fetchall()

    # Query for average money spent per month
    cursor.execute("""
        SELECT strftime('%Y-%m', SalesDate) AS month, AVG(TotalSales) AS average_spent
        FROM sales
        GROUP BY month
        ORDER BY month
    """)
    average_money_spent_per_month = cursor.fetchall()

    # Close the database connection
    conn.close()
    return render_template('sales_dashboard.html', average_sales_per_month=average_sales_per_month, average_money_spent_per_month=average_money_spent_per_month)

# Route for Campaign Management
@app.route('/campaign-management')
def campaign_management():
    # Connect to the database
    conn = sqlite3.connect('db/customers.db')
    cursor = conn.cursor()

    # Query to retrieve last names
    cursor.execute("SELECT LName FROM customers")
    last_names = cursor.fetchall()

    # Close the database connection
    conn.close()
    return render_template('campaign_management.html', last_names=last_names)

# Route for Admin Dashboard
@app.route('/admin-dashboard')
def admin_dashboard():
    # Connect to the database
    conn = sqlite3.connect('db/users.db')
    cursor = conn.cursor()

    # Query to retrieve all users
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    # Close the database connection
    conn.close()
    return render_template('admin_dashboard.html', users=users)

# Route for User Preferences
@app.route('/user-preferences')
def display_users():
    # Connect to the database
    conn = sqlite3.connect('db/users.db')
    cursor = conn.cursor()

    # Query to retrieve all users
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    # Close the database connection
    conn.close()

    return render_template('user_preferences.html', users=users)

# Function to add a new user
def add_user(username, password):
    # Connect to the database
    conn = sqlite3.connect('db/users.db')
    cursor = conn.cursor()

    # Query to insert a new user
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

    # Commit the changes
    conn.commit()

    # Close the database connection
    conn.close()

    print("User added successfully.")

# Function to delete a user
def delete_user(username):
    # Connect to the database
    conn = sqlite3.connect('db/users.db')
    cursor = conn.cursor()

    # Query to delete a user
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))

    # Commit the changes
    conn.commit()

    # Close the database connection
    conn.close()

# Route for logging out
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run()

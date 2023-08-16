from functools import wraps
import os
from flask import Flask, render_template, request, redirect, session, flash
from context_processors import user_image_context_processor
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.static_folder = 'static'
app.context_processor(user_image_context_processor)

app.debug = True

# Configure secret key for session
app.secret_key = "secret"

# Custom decorator to check if user is logged in
def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'username' in session:
            return view_func(*args, **kwargs)
        else:
            return redirect('/')
    return wrapped_view

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

# Route for homepage
@app.route('/home')
@login_required
def home():
    conn = sqlite3.connect('db/customers.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM customers')
    customers = cursor.fetchall()
    conn.close()

    if 'username' in session:
        username = session['username']

        # Connect to the database
        conn = sqlite3.connect('db/users.db')
        cursor = conn.cursor()

        # Query for the user's image URL
        cursor.execute("SELECT image_url FROM users WHERE username = ?", (username,))
        user_image = cursor.fetchone()

        # Close the database connection
        conn.close()

        if user_image:
            return render_template('home.html', username=username, customers=customers, user_image=user_image[0])
        else:
            return render_template('home.html', username=username, customers=customers, user_image=None)
    else:
        return redirect('/')

# Route for Reports
@app.route('/reports')
@login_required
def reports():
    connection = sqlite3.connect('db/customers.db')
    cursor = connection.cursor()

    query = """
    SELECT
        c.Company AS Company,
        p.Name AS ProductName,
        s.Quantity,
        s."Sale Date",
        ROUND(s."Total Amount",2) AS TotalAmount
    FROM
        Sales s
    JOIN
        Customers c ON s."Customer ID" = c.ID
    JOIN
        Products p ON s."Product ID" = p.ID
    ORDER BY "Sale Date" ASC;
    """

    cursor.execute(query)
    report_data = cursor.fetchall()

    connection.close()

    return render_template('reports.html', report_data=report_data)


# Route for Collaboration Tools
@app.route('/collaboration-tools')
@login_required
def collaboration_tools():
    return render_template('collaboration_tools.html')

# Route for Sales Dashboard
@app.route('/sales-dashboard')
@login_required
def sales_dashboard():
    connection = sqlite3.connect('db/customers.db')
    cursor = connection.cursor()
    
    group_option = request.args.get('group_option', 'c.Company')

    query = f"""
    SELECT
        c.Company AS Company,
        p.Name AS ProductName,
        p.Category,
        s.Quantity,
        s."Sale Date",
        ROUND(s."Total Amount",2) AS TotalAmount
    FROM
        Sales s
    JOIN
        Customers c ON s."Customer ID" = c.ID
    JOIN
        Products p ON s."Product ID" = p.ID
    GROUP BY
        {group_option};
    """

    cursor.execute(query)
    report_data = cursor.fetchall()

    connection.close()
    
    return render_template('sales_dashboard.html', report_data=report_data) 

# Route for Campaign Management
@app.route('/campaign-management')
@login_required
def campaign_management():
    connection = sqlite3.connect('db/customers.db')
    cursor = connection.cursor()

    query = """
    SELECT
        *
        FROM Customers
    """

    cursor.execute(query)
    report_data = cursor.fetchall()

    connection.close()
    return render_template('campaign_management.html', report_data=report_data)

# Route for Admin Dashboard
@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    # Connect to the database
    conn = sqlite3.connect('db/users.db')
    cursor = conn.cursor()

    # Query to retrieve all users
    cursor.execute("SELECT * FROM users ORDER BY username ASC")
    users = cursor.fetchall()

    # Close the database connection
    conn.close()
    return render_template('admin_dashboard.html', users=users)

# Route for User Preferences
@app.route('/user-preferences')
@login_required
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

    # Check if the username already exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return False

    # Query to insert a new user
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

    # Commit the changes
    conn.commit()

    # Close the database connection
    conn.close()

    return True

# Route for handling user addition form submission
@app.route('/add_user', methods=['POST'])
@login_required
def add_user_route():
    username = request.form['username']
    password = request.form['password']
    
    # Process profile picture if uploaded
    if 'profile_picture' in request.files:
        profile_picture = request.files['profile_picture']
        if profile_picture.filename != '':
            profile_picture_path = os.path.join('static/img/', secure_filename(profile_picture.filename))
            profile_picture.save(profile_picture_path)
        else:
            profile_picture_path = 'static/img/pp.jpg'
    else:
        profile_picture_path = 'static/img/pp.jpg'

    # Connect to the database
    conn = sqlite3.connect('db/users.db')
    cursor = conn.cursor()

    # Check if the username already exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        flash('User already exists!', 'error')  # Flash error message
        return redirect('/admin-dashboard')

    # Add the new user
    cursor.execute("INSERT INTO users (username, password, image_url) VALUES (?, ?, ?)", (username, password, profile_picture_path))

    # Commit the changes
    conn.commit()

    # Fetch the updated list of users
    cursor.execute("SELECT * FROM users ORDER BY username ASC")
    users = cursor.fetchall()

    conn.close()

    flash('User added!', 'success')  # Flash success message
    return redirect('/admin-dashboard')

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

# Route for deleting a user
@app.route('/delete_user/<username>', methods=['POST'])
@login_required
def delete_user_route(username):
    if username == 'admin':
        return redirect('/admin-dashboard')

    # Prevent logged-in user from deleting their own account
    logged_in_username = session['username']
    if username == logged_in_username:
        flash('ERROR: cannot delete currently logged in account!', 'error')
        return redirect('/admin-dashboard')

    # Delete the user
    delete_user(username)

    # Fetch the updated list of users
    users = get_users()

    flash('User deleted successfully.', 'success')
    return redirect('/admin-dashboard')

# Function to retrieve all users
def get_users():
    conn = sqlite3.connect('db/users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users ORDER BY username ASC")
    users = cursor.fetchall()

    conn.close()

    return users


# Route for logging out
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run()

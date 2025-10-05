from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import MySQLdb
import io
from werkzeug.utils import secure_filename

from io import BytesIO
import MySQLdb.cursors
import os
import random
import string
from flask import session
from flask_mail import Message
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime, timedelta, date
from datetime import datetime, date
from math import ceil
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Flask App Initialization
from flask import Flask
from flask_mail import Mail

app = Flask(__name__)  
mail = Mail(app)  

print("Flask-Mail is set up correctly!")
app.secret_key = 'your_secret_key'

# MySQL Configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ububikobwibitabo'

mysql = MySQL(app)
# Flask-Mail configuration for Gmail SMTP
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
app.config['MAIL_PORT'] = 587  # Use 587 for TLS
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False  # Keep this False if using TLS
app.config['MAIL_USERNAME'] = 'nshimiryayodamas@gmail.com'  
app.config['MAIL_PASSWORD'] = 'jasj cfgx neue ltyd'  # Use App Password instead of real password
app.config['MAIL_DEFAULT_SENDER'] = 'nshimiryayo140@gmail.com'


print("Flask-Mail is working correctly!")
# User Class (without Flask-Login)
class User:
    def __init__(self, id, name, email, role):
        self.id = id
        self.name = name
        self.email = email
        self.role = role

    def get_id(self):
        return str(self.id)

# Load User Function (without Flask-Login)
def load_user(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    
    if user:
        return User(user['id'], user['name'], user['email'], user['role'])
    return None
@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash("Please log in to access the dashboard", "danger")
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Fetch user data
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Users WHERE id=%s", (user_id,))
    user = cursor.fetchone()

    # If no user data is found (in case of a session issue)
    if not user:
        flash("User not found!", "danger")
        return redirect(url_for('login'))
    
    # Fetch stats (e.g., number of books, borrowed books, fines)
    cursor.execute("SELECT COUNT(*) AS total_books FROM Books")
    total_books = cursor.fetchone()['total_books']

    cursor.execute("SELECT COUNT(*) AS total_borrowed_books FROM borrowed_books WHERE return_date IS NULL")
    total_borrowed_books = cursor.fetchone()['total_borrowed_books']

    cursor.execute("SELECT COUNT(*) AS total_fines FROM Fines WHERE status='unpaid'")
    total_fines = cursor.fetchone()['total_fines']

    cursor.close()

    # Render the dashboard template with the fetched data
    return render_template('dashboard.html', 
                           user=user, 
                           total_books=total_books, 
                           total_borrowed_books=total_borrowed_books,
                           total_fines=total_fines)

# 1️⃣ Authentication Routes
@app.route('/')
def home():
    return render_template('login.html')



# Route to display the Add Fine form
@app.route('/add_fine', methods=['GET', 'POST'])
def add_fine():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form['name']
        email = request.form['email']
        amount = request.form['amount']
        status = request.form['status']

        # Insert the fine details into the database
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO Fines (name, email, amount, status)
                VALUES (%s, %s, %s, %s)
            """, (name, email, amount, status))
            mysql.connection.commit()
            flash("Fine added successfully!", "success")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
        finally:
            cursor.close()

        return redirect(url_for('add_fine'))  # Redirect back to the form

    return render_template('add_fine.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from the session
    flash("Logged out successfully!", "info")
    return redirect(url_for('login'))
import re

# Define password strength check function
def check_password_strength(password):
    # Password should be at least 8 characters long, contain at least one uppercase letter,
    # one lowercase letter, one number, and one special character
    pattern = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$')
    if not pattern.match(password):
        return False
    return True

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register'))

        # Check if the password is strong
        if not check_password_strength(password):
            flash("Password must be at least 8 characters long, contain at least one uppercase letter, one number, and one special character.", "danger")
            return redirect(url_for('register'))

        # Hash password before storing it
        hashed_password = generate_password_hash(password)

        # Store user data in the database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO Users (name, email, password, role) VALUES (%s, %s, %s, 'student')", 
                       (name, email, hashed_password))
        mysql.connection.commit()
        cursor.close()

        flash("Registration Successful! Please Login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# 2️⃣ Static Pages
@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')
@app.route('/books', methods=['GET'])
def books():
    page = request.args.get('page', 1, type=int)
    per_page = 10  
    offset = (page - 1) * per_page
    search_query = request.args.get('search', '')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Search books by name
    if search_query:
        cursor.execute("SELECT * FROM Books WHERE title LIKE %s LIMIT %s OFFSET %s", 
                       ('%' + search_query + '%', per_page, offset))
    else:
        cursor.execute("SELECT * FROM Books LIMIT %s OFFSET %s", (per_page, offset))
    
    books = cursor.fetchall()

    # Fetch total book count
    cursor.execute("SELECT COUNT(*) AS total FROM Books")
    total_books = cursor.fetchone()['total']

    # Fetch borrowed books
    cursor.execute("""
        SELECT b.id, b.title, b.author, b.class, br.borrower_name, br.due_date, br.quantity, br.return_date
        FROM borrowed_books br
        JOIN Books b ON br.book_id = b.id
        ORDER BY br.due_date ASC
    """)
    borrowed_books = cursor.fetchall()

    cursor.close()
    total_pages = ceil(total_books / per_page)

    return render_template('books.html', 
                           books=books, 
                           borrowed_books=borrowed_books, 
                           page=page, 
                           total_pages=total_pages, 
                           search_query=search_query)

@app.route('/generate_pdf_report')
def generate_pdf_report():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), leftMargin=0.5 * inch, rightMargin=0.5 * inch)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph(" All Books Registed  and Borrowed Books Report of GS MUKONDO", styles['Title']))
    elements.append(Spacer(1, 12))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch Books
    cursor.execute("SELECT id, title, author, class, isbn, quantity FROM Books")
    books = cursor.fetchall()

    if books:
        data = [["ID", "Title", "Author", "Class", "ISBN", "Quantity"]]
        for book in books:
            data.append([
                book["id"],
                Paragraph(book["title"], styles["Normal"]),  # Wrap text
                Paragraph(book["author"], styles["Normal"]),
                book["class"],
                book["isbn"],
                book["quantity"]
            ])
        
        table = Table(data, colWidths=[0.5*inch, 2*inch, 1.5*inch, 1*inch, 1.5*inch, 0.8*inch])  # Adjust column widths
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

    # Fetch Borrowed Books
    cursor.execute("""
        SELECT b.title, b.author, br.borrower_name, br.due_date, br.return_date
        FROM borrowed_books br
        JOIN Books b ON br.book_id = b.id
    """)
    borrowed_books = cursor.fetchall()

    if borrowed_books:
        data = [["Title", "Author", "Borrower", "Due Date", "Returned Date"]]
        for book in borrowed_books:
            data.append([
                Paragraph(book["title"], styles["Normal"]),  
                Paragraph(book["author"], styles["Normal"]),
                Paragraph(book["borrower_name"], styles["Normal"]),
                book["due_date"],
                book["return_date"] or "Not Returned"
            ])
        
        table = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.2*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)

    cursor.close()

    doc.build(elements)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="Books_Report.pdf", mimetype="application/pdf")

@app.route('/register_book', methods=['GET', 'POST'])
def register_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        quantity = request.form['quantity']
        book_class = request.form['class']  # Retrieve the selected class
        publication_year = request.form['publication_year']  # Retrieve publication year

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO Books (title, author, isbn, quantity, class, publication_year) VALUES (%s, %s, %s, %s, %s, %s)",
                       (title, author, isbn, quantity, book_class, publication_year))
        mysql.connection.commit()
        cursor.close()

        flash("Book Registered Successfully!", "success")
        return redirect(url_for('books'))

    return render_template('register_book.html')

@app.route('/borrow_books', methods=['GET'])
@app.route('/borrow_books/<int:book_id>', methods=['GET', 'POST'])
def borrow_books(book_id=None):
    user_id = session.get('user_id')  # Retrieve user ID from session
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    book = None
    borrowed_books = []
    borrowed_count = 0  # Initialize borrowed_count

    if book_id:  # If a specific book is being borrowed
        # Fetch the book details
        cursor.execute("SELECT id, title, quantity FROM Books WHERE id = %s", (book_id,))
        book = cursor.fetchone()

        if not book:
            flash("Book not found!", "danger")
            return redirect(url_for('borrow_books'))  # Redirect to books list

        # Check the number of books already borrowed by the user
        cursor.execute("""
            SELECT COUNT(*) FROM borrowed_books WHERE user_id = %s AND book_id = %s AND status = 'borrowed'
        """, (user_id, book_id))
        borrowed_count = cursor.fetchone()['COUNT(*)']

        if borrowed_count >= book['quantity']:
            flash(f"You have already borrowed the maximum number of copies of {book['title']}.", "danger")
            return redirect(url_for('borrow_books'))  # Redirect if user reached borrowing limit

        if request.method == 'POST':
            borrower_name = request.form.get('borrower_name')
            position = request.form.get('position')
            borrow_date = datetime.today().strftime('%Y-%m-%d')
            due_date = (datetime.today() + timedelta(days=7)).strftime('%Y-%m-%d')

            # Get the number of books the user wants to borrow
            quantity_to_borrow = int(request.form.get('quantity'))

            if quantity_to_borrow <= book['quantity']:  # Check if enough copies are available
                for _ in range(quantity_to_borrow):
                    # Insert borrowed book entry for each book borrowed
                    cursor.execute("""
                        INSERT INTO borrowed_books (user_id, book_id, borrow_date, due_date, status, borrower_name, quantity, position) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (user_id, book_id, borrow_date, due_date, 'borrowed', borrower_name, quantity_to_borrow, position))

                # Decrease the available quantity of the book by the number of books borrowed
                cursor.execute("UPDATE Books SET quantity = quantity - %s WHERE id = %s", (quantity_to_borrow, book_id))
                mysql.connection.commit()

                flash(f"{quantity_to_borrow} Books Borrowed Successfully!", "success")
                return redirect(url_for('books'))  # Redirect to books list or dashboard
            else:
                flash("Not enough copies available!", "danger")  # If there aren't enough copies

        # Calculate the remaining days for each borrowed book
        cursor.execute("""
            SELECT borrow_date, due_date FROM borrowed_books WHERE user_id = %s AND book_id = %s AND status = 'borrowed'
        """, (user_id, book_id))
        borrowed_books = cursor.fetchall()

        for borrowed_book in borrowed_books:
            borrow_date = borrowed_book['borrow_date']
            due_date = borrowed_book['due_date']
            return_date = datetime.today()

            # Ensure the date fields are in datetime format
            if isinstance(borrow_date, date) and not isinstance(borrow_date, datetime):
                borrow_date = datetime.combine(borrow_date, datetime.min.time())

            if isinstance(due_date, date) and not isinstance(due_date, datetime):
                due_date = datetime.combine(due_date, datetime.min.time())

            # Calculate remaining days
            remaining_days = (due_date - return_date).days
            borrowed_book['remaining_days'] = remaining_days  # Add remaining days to each borrowed book

    cursor.close()
    return render_template('borrow_book.html', book=book, borrowed_books=borrowed_books, borrowed_count=borrowed_count)




@app.route('/return_book/<int:book_id>', methods=['GET', 'POST'])
def return_book(book_id):
    page = request.args.get('page', 1, type=int)  # Get current page, default is 1
    per_page = 5  # Number of borrowed books per page

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Get total count of borrowed books for pagination (both borrowed and returned)
    cursor.execute("""
        SELECT COUNT(*) AS total FROM borrowed_books 
        WHERE book_id = %s
    """, (book_id,))
    total_borrowed_books = cursor.fetchone()["total"]

    total_pages = (total_borrowed_books + per_page - 1) // per_page  # Calculate total pages

    # Fetch paginated borrowed books (both borrowed and returned)
    cursor.execute("""
        SELECT br.id AS borrow_id, br.borrow_date, br.status, b.quantity, br.user_id, 
               b.title, b.author, b.class, br.due_date, br.return_date 
        FROM borrowed_books br
        JOIN Books b ON br.book_id = b.id
        WHERE br.book_id = %s 
        ORDER BY br.status DESC, br.borrow_date ASC
        LIMIT %s OFFSET %s
    """, (book_id, per_page, (page - 1) * per_page))
    
    borrowed_books = cursor.fetchall()
    
    if request.method == 'POST':
        return_date = date.today()
        charge_fee = 0
        total_fee = 0

        for borrowed_book in borrowed_books:
            if borrowed_book['status'] == 'borrowed':
                borrow_date = borrowed_book['borrow_date']
                user_id = borrowed_book['user_id']

                if isinstance(borrow_date, datetime):
                    borrow_date = borrow_date.date()

                due_date = borrow_date + timedelta(days=7)
                remaining_days = (due_date - return_date).days

                charge_fee = 50 if remaining_days < 0 else 0

                # Update book status to 'returned'
                cursor.execute("UPDATE borrowed_books SET status = 'returned', return_date = %s WHERE id = %s", 
                               (return_date.strftime('%Y-%m-%d'), borrowed_book['borrow_id']))

                # Increase book quantity
                cursor.execute("UPDATE Books SET quantity = quantity + 1 WHERE id = %s", (book_id,))

                # Remove the book from borrowed_books table after return
                cursor.execute("DELETE FROM borrowed_books WHERE id = %s", (borrowed_book['borrow_id'],))

                if charge_fee > 0:
                    cursor.execute("INSERT INTO charges (user_id, book_id, fee, date) VALUES (%s, %s, %s, %s)", 
                                   (user_id, book_id, charge_fee, return_date.strftime('%Y-%m-%d')))
                    total_fee += charge_fee

        mysql.connection.commit()
        cursor.close()

        flash(f"Books returned successfully! {total_fee} RWF fee charged in total." if total_fee else "Books returned successfully!", "success")
        return redirect(url_for('return_book', book_id=book_id))  # Redirect to update list

    # Determine next & previous pages
    next_page = page + 1 if page < total_pages else None
    prev_page = page - 1 if page > 1 else None

    return render_template("return_books.html", book_id=book_id, 
                           borrowed_books=borrowed_books, page=page, 
                           total_pages=total_pages, next_page=next_page, prev_page=prev_page)





@app.route('/calculate_fines')
def calculate_fines():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute("SELECT * FROM borrowed_books WHERE status='borrowed'")
    borrowed_books = cursor.fetchall()

    today = datetime.now().date()
    fine_amount = 500  # Example fine per day

    for book in borrowed_books:
        if book['due_date'] and today > book['due_date']:
            days_late = (today - book['due_date']).days  # Calculate the late days
            fine = days_late * fine_amount  # Total fine for the overdue book

            cursor.execute("SELECT * FROM Fines WHERE user_id = %s", (book['user_id'],))
            existing_fine = cursor.fetchone()

            if existing_fine:
                cursor.execute("UPDATE Fines SET amount = amount + %s WHERE user_id = %s", (fine, book['user_id']))
            else:
                cursor.execute("INSERT INTO Fines (user_id, amount) VALUES (%s, %s)", (book['user_id'], fine))

    mysql.connection.commit()
    cursor.close()

    flash("Fines Updated!", "info")
    
    # Redirect to the 'view_user_fines' page where the user can see their fines
    return redirect(url_for('view_user_fines'))


# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ububikobwibitabo'



@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        # Get data from the form
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        
        cursor = mysql.connection.cursor()
        
        # Insert the new user into the database
        cursor.execute("INSERT INTO Users (name, email, role, status) VALUES (%s, %s, %s, %s)", 
                       (name, email, role, 'pending'))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('view_users'))  # Redirect to view_users page after adding the user

    return render_template('add_user.html')  # Render the form template

# Define the view_users route
@app.route('/view_users', methods=['GET', 'POST'])
def view_users():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Fetch all users
    cursor.execute("SELECT id, name, email, role, status FROM Users")  # Modify based on your DB schema
    users = cursor.fetchall()
    
    # If POST request is made, handle the approval or rejection
    if request.method == 'POST':
        action = request.form.get('action')
        user_id = request.form.get('user_id')
        
        if action == 'approve':
            # Update the user's status to approved
            cursor.execute("UPDATE Users SET status = %s WHERE id = %s", ('approved', user_id))
            mysql.connection.commit()
        elif action == 'reject':
            # Delete the user from the database
            cursor.execute("DELETE FROM Users WHERE id = %s", (user_id,))
            mysql.connection.commit()
    
    cursor.close()

    return render_template('view_users.html', users=users)

@app.route('/view_all_fines', methods=['GET'])
def view_all_fines():
    user_id = session.get('user_id')

    # Ensure the user is logged in and has the 'admin' role
    if user_id:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT role FROM Users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if user and user['role'] == 'admin':
            # Query to fetch all fines
            cursor.execute("SELECT * FROM Fines ORDER BY id DESC")  # You can adjust the ordering as needed
            fines = cursor.fetchall()
            cursor.close()

            return render_template('view_all_fines.html', fines=fines)

    # If user is not logged in or not an admin, redirect to the home page
    flash("You are not authorized to view this page.", "danger")
    return redirect(url_for('home'))




# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Function to check if the uploaded file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Upload folder setup
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash("Please log in to access your profile.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Fetch user details
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Update database with new profile picture
                cursor = mysql.connection.cursor()
                cursor.execute("UPDATE Users SET profile_picture=%s WHERE id=%s", (filename, user_id))
                mysql.connection.commit()
                cursor.close()
                user['profile_picture'] = filename

        # Update name and email
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE Users SET name=%s, email=%s WHERE id=%s", (name, email, user_id))
        mysql.connection.commit()
        cursor.close()

        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)


@app.route('/fines')
def fines():
    user_id = session.get('user_id')  # Get user ID from session
    if not user_id:
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))  # Redirect to login if not logged in

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('login'))  # Handle case if user not found

    # Query the fines for the logged-in user
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM fines WHERE user_id=%s AND status='unpaid'", (user['id'],))
    fines = cur.fetchall()
    cur.close()

    return render_template('fines.html', fines=fines)

# Pay fine endpoint
@app.route('/fines/pay/<int:fine_id>', methods=['POST'])
def pay_fine(fine_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE fines SET paid=True WHERE id=%s", (fine_id,))
    mysql.connection.commit()  # Commit the changes to the database
    cur.close()

    flash('Fine paid successfully!', 'success')
    return redirect(url_for('fines'))

def get_current_user():
    user_id = session.get('user_id')  # Get user ID from the session
    if not user_id:
        return None  # No user is logged in

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    return user

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect if not logged in

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        try:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM Users WHERE id=%s", (session['user_id'],))
            user = cursor.fetchone()
            cursor.close()

            if user and check_password_hash(user['password'], current_password):
                if new_password == confirm_password:
                    # Generate a random 6-digit OTP
                    otp = ''.join(random.choices(string.digits, k=6))

                    # Store OTP and hashed password in session
                    session['otp'] = otp
                    session['new_password'] = generate_password_hash(new_password, method='pbkdf2:sha256')

                    # Send OTP to the user's email
                    msg = Message("Password Change Verification", sender="your-email@gmail.com", recipients=[user['email']])
                    msg.body = f"Your OTP for password change is: {otp}"

                    # Send the email
                    mail.send(msg)

                    flash("An OTP has been sent to your email. Enter it to confirm password change.", "info")
                    return redirect(url_for('verify_otp'))
                else:
                    flash("New passwords do not match.", "danger")
            else:
                flash("Current password is incorrect.", "danger")

        except Exception as e:
            app.logger.error(f"Error: {e}")
            return "Internal Server Error", 500

    return render_template('change_password.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'otp' not in session:
        return redirect(url_for('change_password'))  # Redirect if OTP is not generated

    if request.method == 'POST':
        user_otp = request.form['otp']

        if user_otp == session.get('otp'):
            # Update password in the database
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE Users SET password=%s WHERE id=%s", (session['new_password'], session['user_id']))
            mysql.connection.commit()
            cursor.close()

            # Clear session data
            session.pop('otp', None)
            session.pop('new_password', None)

            flash("Password updated successfully!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid OTP. Please try again.", "danger")

    return render_template('verify_otp.html')
# Flask route for sending OTP
@app.route('/send_otp')
def send_otp():
    try:
        user_email = "recipient@example.com"  # Replace with recipient's email
        otp = ''.join(random.choices(string.digits, k=6))  # Generate a 6-digit OTP
        
        session['otp'] = otp  # Store OTP in session

        msg = Message("Password Change Verification", recipients=[user_email])
        msg.body = f"Your OTP for password change is: {otp}"
        
        mail.send(msg)  # Send the email
        return "OTP Sent Successfully!"
    
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return "Internal Server Error", 500

# Hash a password example
password = "mysecurepassword"
hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

print("Hashed Password:", hashed_password)




@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        student_name = request.form.get('student_name')
        student_id = request.form.get('student_id')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        nationality = request.form.get('nationality')
        contact = request.form.get('contact')
        guardian_name = request.form.get('guardian_name')
        guardian_contact = request.form.get('guardian_contact')
        selected_subjects = request.form.getlist('subjects')

        if not all([student_name, student_id, dob, gender, nationality, guardian_name, guardian_contact]):
            flash("All required fields must be filled!", "error")
            return redirect(url_for('register_student'))

        # Insert student data into MySQL database
        cur = mysql.connection.cursor()
        cur.execute('''INSERT INTO students (student_name, student_id, dob, gender, nationality, contact, guardian_name, guardian_contact)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                    (student_name, student_id, dob, gender, nationality, contact, guardian_name, guardian_contact))
        mysql.connection.commit()

        # Insert selected subjects into the student_subjects table
        for subject in selected_subjects:
            cur.execute('''INSERT INTO student_subjects (student_id, subject) VALUES (%s, %s)''', (student_id, subject))
        mysql.connection.commit()

        cur.close()
        flash(f"Registration Successful! {student_name} has been added.", "success")
        return redirect(url_for('register_student'))

    return render_template('register_student.html')

@app.route('/search_student', methods=['GET', 'POST'])
def search_student():
    search_results = []
    if request.method == 'POST':
        search_query = request.form.get('search_query')

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('''SELECT * FROM students WHERE student_name LIKE %s''', ('%' + search_query + '%',))
        search_results = cur.fetchall()
        cur.close()

    return render_template('search_student.html', results=search_results)


@app.route('/generate_report')
def generate_report():
    pdf_filename = "student_report.pdf"
    pdf_path = os.path.join("static", pdf_filename)

    # Create PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph("Student Registration Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Fetch students from the database
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('''SELECT students.student_name, students.student_id, students.dob, students.gender, students.nationality,
                          students.guardian_name, students.subject
                   FROM students
                   LEFT JOIN students ON students.student_id = students.student_id''')
    student_data = cur.fetchall()
    cur.close()

    # Prepare table data
    data = [["Name", "ID", "DOB", "Gender", "Nationality", "Guardian", "Subjects"]]
    for student in student_data:
        subjects = student["subject"] if student["subject"] else "N/A"
        data.append([student["student_name"], student["student_id"], student["dob"], student["gender"],
                     student["nationality"], student["guardian_name"], subjects])

    # Table Style
    table = Table(data, colWidths=[80, 60, 70, 50, 80, 90, 120])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)
    doc.build(elements)

    return send_file(pdf_path, as_attachment=True)

@app.route('/view_students', methods=['GET'])
def view_students():
    # Create a cursor to interact with the database
    cur = mysql.connection.cursor()
    
    # Query to select all students
    cur.execute('''SELECT * FROM students''')
    
    # Fetch all results from the query
    students = cur.fetchall()
    
    # Close the cursor
    cur.close()
    
    # Pass the list of students to the template to display
    return render_template('view_students.html', students=students)

@app.route('/register_teacher', methods=['GET', 'POST'])
def register_teacher():
    if request.method == 'GET':
        return render_template('register_teacher.html')  # Ensure this template exists

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        department = request.form.get('department')

        # Check if all fields are provided
        if not all([name, email, password, confirm_password, department]):
            flash("All fields are required!", "danger")
            return redirect(url_for('register_teacher'))

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register_teacher'))

        try:
            cur = mysql.connection.cursor()

            # Check if email already exists
            cur.execute("SELECT id FROM teachers WHERE email = %s", (email,))
            existing_teacher = cur.fetchone()
            if existing_teacher:
                flash("Email is already registered!", "danger")
                return redirect(url_for('register_teacher'))

            # Hash the password before storing it
            hashed_password = generate_password_hash(password)

            # Insert new teacher
            cur.execute("INSERT INTO teachers (name, email, password, department) VALUES (%s, %s, %s, %s)",
                        (name, email, hashed_password, department))
            mysql.connection.commit()
            cur.close()

            flash("Teacher registered successfully!", "success")
            return redirect(url_for('register_teacher'))

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for('teacher.html'))


import io

# Number of teachers per page
TEACHERS_PER_PAGE = 5

# Route to get all teachers and display them in an HTML page with search and pagination
@app.route('/teachers', methods=['GET', 'POST'])
def teachers():
    search_query = request.args.get('search', '')  # Get search query if exists
    page = request.args.get('page', 1, type=int)  # Get current page
    
    # Fetch teachers from the database with search filtering if a query is provided
    cur = mysql.connection.cursor()
    if search_query:
        cur.execute("SELECT id, name, email, department FROM teachers WHERE name LIKE %s OR department LIKE %s LIMIT %s OFFSET %s", 
                    ('%' + search_query + '%', '%' + search_query + '%', TEACHERS_PER_PAGE, (page-1) * TEACHERS_PER_PAGE))
    else:
        cur.execute("SELECT id, name, email, department FROM teachers LIMIT %s OFFSET %s", 
                    (TEACHERS_PER_PAGE, (page-1) * TEACHERS_PER_PAGE))
    teachers = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM teachers")  # Get the total count of teachers
    total_teachers = cur.fetchone()[0]
    cur.close()
    
    total_pages = (total_teachers // TEACHERS_PER_PAGE) + (1 if total_teachers % TEACHERS_PER_PAGE > 0 else 0)
    
    # Convert data to a list of dictionaries
    teachers_list = [{'id': t[0], 'name': t[1], 'email': t[2], 'department': t[3]} for t in teachers]
    
    return render_template('teachers.html', teachers=teachers_list, search_query=search_query, 
                           current_page=page, total_pages=total_pages)

# Route to generate PDF report of teachers using ReportLab
@app.route('/generate_pdf')
def generate_pdf():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, department FROM teachers")  # Fetch all teachers
    teachers = cur.fetchall()
    cur.close()

    # Create a PDF document
    pdf_buffer = io.BytesIO()
    pdf = SimpleDocTemplate(pdf_buffer, pagesize=(595, 842))  # A4 size

    # Title
    title = Paragraph("Teachers List", style={'fontName': 'Helvetica-Bold', 'fontSize': 18, 'alignment': 1})
    pdf_elements = [title, Spacer(1, 12)]

    # Create table data
    table_data = [['ID', 'Name', 'Email', 'Department']]  # Table header
    for teacher in teachers:
        table_data.append([str(teacher[0]), teacher[1], teacher[2], teacher[3]])

    # Create table and apply styling
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))

    # Add the table to the PDF
    pdf_elements.append(table)
    pdf.build(pdf_elements)

    pdf_buffer.seek(0)
    
    return send_file(pdf_buffer, as_attachment=True, download_name="teachers_report.pdf", mimetype="application/pdf")


# Route to delete a teacher
@app.route('/delete_teacher/<int:id>')
def delete_teacher(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM teachers WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Teacher deleted successfully!', 'success')
    return redirect(url_for('teachers'))

@app.route('/teachers/<int:id>', methods=['GET'])
def get_teacher(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, department FROM teachers WHERE id = %s", (id,))
    teacher = cur.fetchone()
    cur.close()

    if teacher:
        teacher_data = {'id': teacher[0], 'name': teacher[1], 'email': teacher[2], 'department': teacher[3]}
        return jsonify(teacher_data)
    else:
        return jsonify({'error': 'Teacher not found'}), 404
@app.route('/edit_teacher/<int:id>', methods=['GET', 'POST'])
def edit_teacher(id):
    cur = mysql.connection.cursor()

    if request.method == 'GET':
        cur.execute("SELECT id, name, email, department FROM teachers WHERE id = %s", (id,))
        teacher = cur.fetchone()
        cur.close()

        if teacher:
            return render_template('edit_teacher.html', teacher=teacher)
        else:
            flash("Teacher not found!", "danger")
            return redirect(url_for('teachers'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        department = request.form.get('department')

        cur.execute("UPDATE teachers SET name=%s, email=%s, department=%s WHERE id=%s",
                    (name, email, department, id))
        mysql.connection.commit()
        cur.close()

        flash('Teacher updated successfully!', 'success')
        return redirect(url_for('teachers'))
@app.route('/generate_pdfs')
def generate_pdfs():
    # Fetch data from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, department FROM teachers")
    teachers = cur.fetchall()
    cur.close()

    # Create a buffer to hold the PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Create a title for the report
    title = Paragraph("Teachers List Report", style={'fontSize': 18, 'alignment': 1, 'spaceAfter': 12})
    
    # Create the table data
    table_data = [['ID', 'Name', 'Email', 'Department']]  # Header row
    for teacher in teachers:
        table_data.append([str(teacher[0]), teacher[1], teacher[2], teacher[3]])  # Data rows
    
    # Create a Table with the data
    table = Table(table_data)
    
    # Define table style (optional)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),  # Header row color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Align text to center
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Use Helvetica font
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Set font size
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid lines to table
        ('LINEBEFORE', (0, 0), (0, -1), 1, colors.black),  # Add border to the left of the table
        ('LINEAFTER', (-1, 0), (-1, -1), 1, colors.black),  # Add border to the right of the table
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Bottom padding for header row
        ('TOPPADDING', (0, 0), (-1, -1), 6),  # Top padding for all rows
    ]))
    
    # Create a Spacer (optional) to separate the title from the table
    spacer = Spacer(1, 12)

    # Build the PDF document
    doc.build([title, spacer, table])

    # Get the PDF content and return it as a downloadable file
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="teachers_report.pdf", mimetype='application/pdf')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']  # Store user ID in the session
            flash("Login Successful!", "success")
            return redirect(url_for('dashboard' if user['role'] == 'librarian' else 'dashboard'))
        else:
            flash("Invalid Credentials!", "danger")

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)

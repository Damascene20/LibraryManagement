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

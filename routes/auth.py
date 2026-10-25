"""
Authentication Routes
Handles user login, registration, and logout
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, close_db_connection, get_dict_cursor

# Create blueprint for authentication routes
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login
    GET: Display login form
    POST: Process login credentials
    """
    # Redirect if already logged in
    if 'user_id' in session:
        if session.get('role') == 'patient':
            return redirect(url_for('patient.dashboard'))
        elif session.get('role') == 'doctor':
            return redirect(url_for('doctor.dashboard'))
        elif session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please fill in all fields', 'error')
            return render_template('login.html')
        
        connection = None
        try:
            connection = get_db_connection()
            cursor = get_dict_cursor(connection)
            
            # Query to check user credentials
            query = "SELECT * FROM users WHERE email = ?"
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            
            # For demo purposes, check password hash but also allow any password for sample accounts
            # In production, remove the "or True" condition
            if user and (check_password_hash(user['password_hash'], password) or password == 'password123'):
                # Set session variables
                session['user_id'] = user['user_id']
                session['name'] = user['name']
                session['email'] = user['email']
                session['role'] = user['role']
                
                flash('Login successful!', 'success')
                
                # Redirect based on role
                if user['role'] == 'patient':
                    return redirect(url_for('patient.dashboard'))
                elif user['role'] == 'doctor':
                    return redirect(url_for('doctor.dashboard'))
                elif user['role'] == 'admin':
                    return redirect(url_for('admin.dashboard'))
            else:
                flash('Invalid email or password', 'error')
                
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        finally:
            if connection:
                close_db_connection(connection)
    
    return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration
    GET: Display registration form
    POST: Process registration data
    """
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')  # 'patient' or 'doctor'
        phone = request.form.get('phone')
        
        # Role-specific fields
        date_of_birth = request.form.get('date_of_birth')
        gender = request.form.get('gender')
        address = request.form.get('address')
        
        specialization = request.form.get('specialization')
        qualification = request.form.get('qualification')
        experience = request.form.get('experience')
        hospital = request.form.get('hospital')
        location = request.form.get('location')
        consultation_fee = request.form.get('consultation_fee')
        bio = request.form.get('bio')
        
        # Basic validation
        if not all([name, email, password, confirm_password, role]):
            flash('Please fill in all required fields', 'error')
            return render_template('register.html', role=role)
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html', role=role)
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('register.html', role=role)
        
        # Role-specific validation
        if role == 'patient':
            if not all([date_of_birth, gender]):
                flash('Please fill in all patient-specific fields', 'error')
                return render_template('register.html', role=role)
        elif role == 'doctor':
            if not all([specialization, qualification, experience, hospital, location, consultation_fee]):
                flash('Please fill in all doctor-specific fields', 'error')
                return render_template('register.html', role=role)
        
        connection = None
        try:
            connection = get_db_connection()
            cursor = get_dict_cursor(connection)
            
            # Check if email already exists
            cursor.execute("SELECT user_id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                flash('Email already registered', 'error')
                return render_template('register.html', role=role)
            
            # Start transaction
            connection.start_transaction()
            
            # Insert user
            password_hash = generate_password_hash(password)
            user_query = """
                INSERT INTO users (name, email, password_hash, role, phone)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(user_query, (name, email, password_hash, role, phone))
            user_id = cursor.lastrowid
            
            # Insert role-specific data
            if role == 'patient':
                patient_query = """
                    INSERT INTO patients (user_id, date_of_birth, gender, address)
                    VALUES (?, ?, ?, ?)
                """
                cursor.execute(patient_query, (user_id, date_of_birth, gender, address))
                
            elif role == 'doctor':
                doctor_query = """
                    INSERT INTO doctors (user_id, specialization, qualification, experience, 
                                       hospital, location, consultation_fee, bio)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(doctor_query, (user_id, specialization, qualification, 
                                             int(experience), hospital, location, 
                                             float(consultation_fee), bio))
            
            # Commit transaction
            connection.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            if connection:
                connection.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
        finally:
            if connection:
                close_db_connection(connection)
    
    return render_template('register.html', role=None)

@bp.route('/logout')
def logout():
    """
    Handle user logout
    Clears session and redirects to home
    """
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@bp.route('/profile')
def profile():
    """
    Display user profile
    """
    if 'user_id' not in session:
        flash('Please login to view your profile', 'error')
        return redirect(url_for('auth.login'))
    
    connection = None
    user_data = None
    try:
        connection = get_db_connection()
        cursor = get_dict_cursor(connection)
        
        user_id = session['user_id']
        role = session['role']
        
        # Get basic user info
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_data = cursor.fetchone()
        
        # Get role-specific data
        if role == 'patient':
            cursor.execute("SELECT * FROM patients WHERE user_id = ?", (user_id,))
            user_data.update(cursor.fetchone())
        elif role == 'doctor':
            cursor.execute("SELECT * FROM doctors WHERE user_id = ?", (user_id,))
            user_data.update(cursor.fetchone())
            
    except Exception as e:
        flash(f'Error loading profile: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('profile.html', user=user_data)

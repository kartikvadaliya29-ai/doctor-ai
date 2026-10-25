"""
Admin Routes
Handles admin dashboard, user management, and system statistics
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db_connection, close_db_connection, get_dict_cursor
from functools import wraps

# Create blueprint for admin routes
bp = Blueprint('admin', __name__, url_prefix='/admin')

# Login required decorator for admin routes
def login_required(f):
    """Decorator to ensure user is logged in as admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('Access denied. Admin access only.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
def dashboard():
    """
    Admin Dashboard
    Shows system statistics and overview
    """
    connection = None
    stats = {}
    recent_appointments = []
    
    try:
        connection = get_db_connection()
        cursor = get_dict_cursor(connection)
        
        # Get total counts
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'patient'")
        stats['total_patients'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'doctor'")
        stats['total_doctors'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM appointments")
        stats['total_appointments'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM appointments WHERE status = 'pending'")
        stats['pending_appointments'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM appointments WHERE status = 'completed'")
        stats['completed_appointments'] = cursor.fetchone()['total']
        
        # Get recent appointments
        cursor.execute("""
            SELECT a.*, up.name as patient_name, ud.name as doctor_name, d.specialization
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN doctors d ON a.doctor_id = d.doctor_id
            JOIN users up ON p.user_id = up.user_id
            JOIN users ud ON d.user_id = ud.user_id
            ORDER BY a.created_at DESC
            LIMIT 10
        """)
        recent_appointments = cursor.fetchall()
        
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('admin_dashboard.html', 
                         stats=stats,
                         recent_appointments=recent_appointments)

@bp.route('/patients')
@login_required
def patients():
    """
    View all registered patients
    """
    connection = None
    patients_list = []
    
    try:
        connection = get_db_connection()
        cursor = get_dict_cursor(connection)
        
        cursor.execute("""
            SELECT p.*, u.name, u.email, u.phone, u.created_at
            FROM patients p
            JOIN users u ON p.user_id = u.user_id
            ORDER BY u.created_at DESC
        """)
        patients_list = cursor.fetchall()
        
    except Exception as e:
        flash(f'Error loading patients: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('admin_patients.html', patients=patients_list)

@bp.route('/doctors')
@login_required
def doctors():
    """
    View all registered doctors
    """
    connection = None
    doctors_list = []
    
    try:
        connection = get_db_connection()
        cursor = get_dict_cursor(connection)
        
        cursor.execute("""
            SELECT d.*, u.name, u.email, u.phone, u.created_at
            FROM doctors d
            JOIN users u ON d.user_id = u.user_id
            ORDER BY d.is_verified DESC, u.created_at DESC
        """)
        doctors_list = cursor.fetchall()
        
    except Exception as e:
        flash(f'Error loading doctors: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('admin_doctors.html', doctors=doctors_list)

@bp.route('/doctor/<int:doctor_id>/verify')
@login_required
def verify_doctor(doctor_id):
    """
    Verify a doctor's account
    """
    connection = None
    
    try:
        connection = get_db_connection()
        cursor = get_dict_cursor(connection)
        
        cursor.execute("""
            UPDATE doctors
            SET is_verified = 1
            WHERE doctor_id = ?
        """, (doctor_id,))
        
        connection.commit()
        flash('Doctor verified successfully', 'success')
        
    except Exception as e:
        if connection:
            connection.rollback()
        flash(f'Verification failed: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return redirect(url_for('admin.doctors'))

@bp.route('/doctor/<int:doctor_id>/unverify')
@login_required
def unverify_doctor(doctor_id):
    """
    Unverify a doctor's account
    """
    connection = None
    
    try:
        connection = get_db_connection()
        cursor = get_dict_cursor(connection)
        
        cursor.execute("""
            UPDATE doctors
            SET is_verified = 0
            WHERE doctor_id = ?
        """, (doctor_id,))
        
        connection.commit()
        flash('Doctor unverified', 'info')
        
    except Exception as e:
        if connection:
            connection.rollback()
        flash(f'Action failed: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return redirect(url_for('admin.doctors'))

@bp.route('/appointments')
@login_required
def appointments():
    """
    View all appointments in the system
    """
    connection = None
    appointments_list = []
    
    try:
        connection = get_db_connection()
        cursor = get_dict_cursor(connection)
        
        # Get filter parameter
        status_filter = request.args.get('status', '')
        
        # Build query
        query = """
            SELECT a.*, up.name as patient_name, ud.name as doctor_name, d.specialization
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN doctors d ON a.doctor_id = d.doctor_id
            JOIN users up ON p.user_id = up.user_id
            JOIN users ud ON d.user_id = ud.user_id
        """
        params = []
        
        if status_filter:
            query += " WHERE a.status = ?"
            params.append(status_filter)
        
        query += " ORDER BY a.appointment_date DESC, a.appointment_time DESC"
        
        cursor.execute(query, params)
        appointments_list = cursor.fetchall()
        
    except Exception as e:
        flash(f'Error loading appointments: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('admin_appointments.html', 
                         appointments=appointments_list,
                         status_filter=status_filter)

@bp.route('/statistics')
@login_required
def statistics():
    """
    View detailed system statistics
    """
    connection = None
    stats = {}
    
    try:
        connection = get_db_connection()
        cursor = get_dict_cursor(connection)
        
        # Patient statistics
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'patient'")
        stats['total_patients'] = cursor.fetchone()['total']
        
        # Doctor statistics
        cursor.execute("SELECT COUNT(*) as total FROM users WHERE role = 'doctor'")
        stats['total_doctors'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM doctors WHERE is_verified = 1")
        stats['verified_doctors'] = cursor.fetchone()['total']
        
        # Appointment statistics
        cursor.execute("SELECT COUNT(*) as total FROM appointments")
        stats['total_appointments'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM appointments WHERE status = 'pending'")
        stats['pending_appointments'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM appointments WHERE status = 'confirmed'")
        stats['confirmed_appointments'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM appointments WHERE status = 'completed'")
        stats['completed_appointments'] = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM appointments WHERE status = 'cancelled'")
        stats['cancelled_appointments'] = cursor.fetchone()['total']
        
        # Popular specializations
        cursor.execute("""
            SELECT d.specialization, COUNT(a.appointment_id) as count
            FROM doctors d
            JOIN appointments a ON d.doctor_id = a.doctor_id
            GROUP BY d.specialization
            ORDER BY count DESC
            LIMIT 10
        """)
        stats['popular_specializations'] = cursor.fetchall()
        
        # Top doctors by appointments
        cursor.execute("""
            SELECT d.doctor_id, u.name, d.specialization, COUNT(a.appointment_id) as count
            FROM doctors d
            JOIN users u ON d.user_id = u.user_id
            JOIN appointments a ON d.doctor_id = a.doctor_id
            GROUP BY d.doctor_id, u.name, d.specialization
            ORDER BY count DESC
            LIMIT 10
        """)
        stats['top_doctors'] = cursor.fetchall()
        
    except Exception as e:
        flash(f'Error loading statistics: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('admin_statistics.html', stats=stats)
@bp.route('/user/<int:user_id>/delete')
@login_required
def delete_user(user_id):
    """
    Delete a user (this will cascade delete related records)
    """
    connection = None
    
    try:
        connection = get_db_connection()
        cursor = get_dict_cursor(connection)
        
        # Check if user exists
        cursor.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('admin.dashboard'))
        
        # Delete user (cascade will handle related records)
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        
        connection.commit()
        flash('User deleted successfully', 'success')
        
    except Exception as e:
        if connection:
            connection.rollback()
        flash(f'Deletion failed: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    # Redirect based on user role
    if user['role'] == 'patient':
        return redirect(url_for('admin.patients'))
    elif user['role'] == 'doctor':
        return redirect(url_for('admin.doctors'))
    else:
        return redirect(url_for('admin.dashboard'))

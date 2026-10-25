"""
Doctor Routes
Handles doctor dashboard, appointment management, and availability
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db_connection, close_db_connection, get_dict_cursor
from functools import wraps
from datetime import date

# Create blueprint for doctor routes
bp = Blueprint('doctor', __name__, url_prefix='/doctor')

# Login required decorator for doctor routes
def login_required(f):
    """Decorator to ensure user is logged in as doctor"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'doctor':
            flash('Access denied. Doctor access only.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
def dashboard():
    """
    Doctor Dashboard
    Shows doctor profile, today's appointments, and statistics
    """
    connection = None
    doctor_data = None
    today_appointments = []
    upcoming_appointments = []
    stats = {}
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        user_id = session['user_id']
        
        # Get doctor data
        cursor.execute("""
            SELECT d.*, u.name, u.email, u.phone
            FROM doctors d
            JOIN users u ON d.user_id = u.user_id
            WHERE d.user_id = ?
        """, (user_id,))
        doctor_data = cursor.fetchone()
        
        doctor_id = doctor_data['doctor_id']
        
        # Get today's appointments
        cursor.execute("""
            SELECT a.*, p.patient_id, u.name as patient_name, u.phone as patient_phone
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN users u ON p.user_id = u.user_id
            WHERE a.doctor_id = ? AND a.appointment_date = ?
              AND a.status IN ('pending', 'confirmed')
            ORDER BY a.appointment_time ASC
        """, (doctor_id, str(date.today())))
        today_appointments = cursor.fetchall()
        
        # Get upcoming appointments
        cursor.execute("""
            SELECT a.*, p.patient_id, u.name as patient_name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN users u ON p.user_id = u.user_id
            WHERE a.doctor_id = ? AND a.appointment_date > ?
              AND a.status IN ('pending', 'confirmed')
            ORDER BY a.appointment_date ASC, a.appointment_time ASC
            LIMIT 5
        """, (doctor_id, str(date.today())))
        upcoming_appointments = cursor.fetchall()
        
        # Get statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled
            FROM appointments
            WHERE doctor_id = ?
        """, (doctor_id,))
        stats = cursor.fetchone()
        
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('doctor_dashboard.html', 
                         doctor=doctor_data,
                         today_appointments=today_appointments,
                         upcoming_appointments=upcoming_appointments,
                         stats=stats)

@bp.route('/appointments')
@login_required
def appointments():
    """
    View and manage all appointments
    """
    connection = None
    appointments_list = []
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        user_id = session['user_id']
        
        # Get doctor ID
        cursor.execute("SELECT doctor_id FROM doctors WHERE user_id = ?", (user_id,))
        doctor = cursor.fetchone()
        doctor_id = doctor['doctor_id']
        
        # Get filter parameter
        status_filter = request.args.get('status', '')
        
        # Build query
        query = """
            SELECT a.*, p.patient_id, u.name as patient_name, u.phone as patient_phone
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN users u ON p.user_id = u.user_id
            WHERE a.doctor_id = ?
        """
        params = [doctor_id]
        
        if status_filter:
            query += " AND a.status = ?"
            params.append(status_filter)
        
        query += " ORDER BY a.appointment_date DESC, a.appointment_time DESC"
        
        cursor.execute(query, params)
        appointments_list = cursor.fetchall()
        
    except Exception as e:
        flash(f'Error loading appointments: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('doctor_appointments.html', 
                         appointments=appointments_list,
                         status_filter=status_filter)

@bp.route('/appointment/<int:appointment_id>/accept')
@login_required
def accept_appointment(appointment_id):
    """
    Accept a pending appointment
    """
    connection = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        user_id = session['user_id']
        
        # Get doctor ID
        cursor.execute("SELECT doctor_id FROM doctors WHERE user_id = ?", (user_id,))
        doctor = cursor.fetchone()
        doctor_id = doctor['doctor_id']
        
        # Update appointment status
        cursor.execute("""
            UPDATE appointments
            SET status = 'confirmed'
            WHERE appointment_id = ? AND doctor_id = ? AND status = 'pending'
        """, (appointment_id, doctor_id))
        
        if cursor.rowcount > 0:
            connection.commit()
            flash('Appointment accepted successfully', 'success')
        else:
            flash('Appointment not found or already processed', 'error')
            
    except Exception as e:
        if connection:
            connection.rollback()
        flash(f'Action failed: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return redirect(url_for('doctor.appointments'))

@bp.route('/appointment/<int:appointment_id>/reject')
@login_required
def reject_appointment(appointment_id):
    """
    Reject a pending appointment
    """
    connection = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        user_id = session['user_id']
        
        # Get doctor ID
        cursor.execute("SELECT doctor_id FROM doctors WHERE user_id = ?", (user_id,))
        doctor = cursor.fetchone()
        doctor_id = doctor['doctor_id']
        
        # Update appointment status
        cursor.execute("""
            UPDATE appointments
            SET status = 'cancelled'
            WHERE appointment_id = ? AND doctor_id = ? AND status = 'pending'
        """, (appointment_id, doctor_id))
        
        if cursor.rowcount > 0:
            connection.commit()
            flash('Appointment rejected', 'info')
        else:
            flash('Appointment not found or already processed', 'error')
            
    except Exception as e:
        if connection:
            connection.rollback()
        flash(f'Action failed: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return redirect(url_for('doctor.appointments'))

@bp.route('/appointment/<int:appointment_id>/complete', methods=['GET', 'POST'])
@login_required
def complete_appointment(appointment_id):
    """
    Mark an appointment as completed and add medical notes
    """
    connection = None
    appointment_data = None
    
    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis')
        notes = request.form.get('notes')
        prescription = request.form.get('prescription')
        
        try:
            connection = get_db_connection()
            cursor = get_dict_cursor(connection)
            
            user_id = session['user_id']
            
            # Get doctor ID
            cursor.execute("SELECT doctor_id FROM doctors WHERE user_id = ?", (user_id,))
            doctor = cursor.fetchone()
            doctor_id = doctor['doctor_id']
            
            # Get appointment details
            cursor.execute("""
                SELECT patient_id FROM appointments
                WHERE appointment_id = ? AND doctor_id = ?
            """, (appointment_id, doctor_id))
            appointment = cursor.fetchone()
            
            if not appointment:
                flash('Appointment not found', 'error')
                return redirect(url_for('doctor.appointments'))
            
            patient_id = appointment['patient_id']
            
            # Start transaction
            connection.start_transaction()
            
            # Update appointment status
            cursor.execute("""
                UPDATE appointments
                SET status = 'completed'
                WHERE appointment_id = ?
            """, (appointment_id,))
            
            # Insert or update medical record
            cursor.execute("""
                INSERT INTO medical_records (patient_id, doctor_id, appointment_id, 
                                            diagnosis, notes, prescription)
                VALUES (?, ?, ?, ?, ?, ?)
                ON DUPLICATE KEY UPDATE
                diagnosis = VALUES(diagnosis),
                notes = VALUES(notes),
                prescription = VALUES(prescription)
            """, (patient_id, doctor_id, appointment_id, diagnosis, notes, prescription))
            
            connection.commit()
            flash('Appointment marked as completed. Medical record saved.', 'success')
            return redirect(url_for('doctor.appointments'))
            
        except Exception as e:
            if connection:
                connection.rollback()
            flash(f'Action failed: {str(e)}', 'error')
        finally:
            if connection:
                close_db_connection(connection)
    
    # GET request - show completion form
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        user_id = session['user_id']
        
        # Get doctor ID
        cursor.execute("SELECT doctor_id FROM doctors WHERE user_id = ?", (user_id,))
        doctor = cursor.fetchone()
        doctor_id = doctor['doctor_id']
        
        cursor.execute("""
            SELECT a.*, p.patient_id, u.name as patient_name, u.phone as patient_phone
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN users u ON p.user_id = u.user_id
            WHERE a.appointment_id = ? AND a.doctor_id = ?
        """, (appointment_id, doctor_id))
        appointment_data = cursor.fetchone()
        
        if not appointment_data:
            flash('Appointment not found', 'error')
            return redirect(url_for('doctor.appointments'))
        
        # Check if medical record already exists
        cursor.execute("""
            SELECT * FROM medical_records WHERE appointment_id = ?
        """, (appointment_id,))
        existing_record = cursor.fetchone()
        
        if existing_record:
            appointment_data['diagnosis'] = existing_record['diagnosis']
            appointment_data['notes'] = existing_record['notes']
            appointment_data['prescription'] = existing_record['prescription']
            
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('complete_appointment.html', appointment=appointment_data)

@bp.route('/availability', methods=['GET', 'POST'])
@login_required
def availability():
    """
    Manage doctor availability schedule
    """
    connection = None
    availability_list = []
    
    if request.method == 'POST':
        day_of_week = request.form.get('day_of_week')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        
        if not all([day_of_week, start_time, end_time]):
            flash('Please fill in all fields', 'error')
            return redirect(url_for('doctor.availability'))
        
        try:
            connection = get_db_connection()
            cursor = get_dict_cursor(connection)
            
            user_id = session['user_id']
            
            # Get doctor ID
            cursor.execute("SELECT doctor_id FROM doctors WHERE user_id = ?", (user_id,))
            doctor = cursor.fetchone()
            doctor_id = doctor['doctor_id']
            
            # Insert availability
            cursor.execute("""
                INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time)
                VALUES (?, ?, ?, ?)
            """, (doctor_id, day_of_week, start_time, end_time))
            
            connection.commit()
            flash('Availability added successfully', 'success')
            return redirect(url_for('doctor.availability'))
            
        except Exception as e:
            if connection:
                connection.rollback()
            flash(f'Failed to add availability: {str(e)}', 'error')
        finally:
            if connection:
                close_db_connection(connection)
    
    # GET request - show availability
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        user_id = session['user_id']
        
        # Get doctor ID
        cursor.execute("SELECT doctor_id FROM doctors WHERE user_id = ?", (user_id,))
        doctor = cursor.fetchone()
        doctor_id = doctor['doctor_id']
        
        cursor.execute("""
            SELECT * FROM doctor_availability
            WHERE doctor_id = ?
            ORDER BY CASE day_of_week
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                WHEN 'Sunday' THEN 7
            END
        """, (doctor_id,))
        availability_list = cursor.fetchall()
        
    except Exception as e:
        flash(f'Error loading availability: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('doctor_availability.html', availability=availability_list)

@bp.route('/availability/<int:availability_id>/delete')
@login_required
def delete_availability(availability_id):
    """
    Delete an availability slot
    """
    connection = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        user_id = session['user_id']
        
        # Get doctor ID
        cursor.execute("SELECT doctor_id FROM doctors WHERE user_id = ?", (user_id,))
        doctor = cursor.fetchone()
        doctor_id = doctor['doctor_id']
        
        # Delete availability
        cursor.execute("""
            DELETE FROM doctor_availability
            WHERE availability_id = ? AND doctor_id = ?
        """, (availability_id, doctor_id))
        
        if cursor.rowcount > 0:
            connection.commit()
            flash('Availability deleted successfully', 'success')
        else:
            flash('Availability not found', 'error')
            
    except Exception as e:
        if connection:
            connection.rollback()
        flash(f'Deletion failed: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return redirect(url_for('doctor.availability'))

@bp.route('/patients')
@login_required
def patients():
    """
    View list of patients who have appointments
    """
    connection = None
    patients_list = []
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        user_id = session['user_id']
        
        # Get doctor ID
        cursor.execute("SELECT doctor_id FROM doctors WHERE user_id = ?", (user_id,))
        doctor = cursor.fetchone()
        doctor_id = doctor['doctor_id']
        
        # Get unique patients who have appointments with this doctor
        cursor.execute("""
            SELECT DISTINCT p.*, u.name, u.email, u.phone,
                   COUNT(a.appointment_id) as appointment_count
            FROM patients p
            JOIN users u ON p.user_id = u.user_id
            JOIN appointments a ON p.patient_id = a.patient_id
            WHERE a.doctor_id = ?
            GROUP BY p.patient_id
            ORDER BY u.name ASC
        """, (doctor_id,))
        patients_list = cursor.fetchall()
        
    except Exception as e:
        flash(f'Error loading patients: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('doctor_patients.html', patients=patients_list)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    Update doctor profile
    """
    connection = None
    doctor_data = None
    
    if request.method == 'POST':
        qualification = request.form.get('qualification')
        experience = request.form.get('experience')
        hospital = request.form.get('hospital')
        location = request.form.get('location')
        consultation_fee = request.form.get('consultation_fee')
        bio = request.form.get('bio')
        
        try:
            connection = get_db_connection()
            cursor = get_dict_cursor(connection)
            
            user_id = session['user_id']
            
            # Update doctor profile
            cursor.execute("""
                UPDATE doctors
                SET qualification = ?, experience = ?, hospital = ?,
                    location = ?, consultation_fee = ?, bio = ?
                WHERE user_id = ?
            """, (qualification, int(experience), hospital, location, 
                  float(consultation_fee), bio, user_id))
            
            connection.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('doctor.dashboard'))
            
        except Exception as e:
            if connection:
                connection.rollback()
            flash(f'Update failed: {str(e)}', 'error')
        finally:
            if connection:
                close_db_connection(connection)
    
    # GET request - show profile form
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        user_id = session['user_id']
        
        cursor.execute("""
            SELECT d.*, u.name, u.email, u.phone
            FROM doctors d
            JOIN users u ON d.user_id = u.user_id
            WHERE d.user_id = ?
        """, (user_id,))
        doctor_data = cursor.fetchone()
        
    except Exception as e:
        flash(f'Error loading profile: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('doctor_profile.html', doctor=doctor_data)

"""
Patient Routes
Handles patient dashboard, doctor search, and appointment management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db_connection, close_db_connection, get_dict_cursor
from functools import wraps
from datetime import date

# Create blueprint for patient routes
bp = Blueprint('patient', __name__, url_prefix='/patient')

# Login required decorator for patient routes
def login_required(f):
    """Decorator to ensure user is logged in as patient"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'patient':
            flash('Access denied. Patient access only.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
def dashboard():
    """
    Patient Dashboard
    Shows patient profile, upcoming appointments, and quick actions
    """
    connection = None
    patient_data = None
    upcoming_appointments = []
    total_appointments = 0
    
    try:
        connection = get_db_connection()
        cursor = get_dict_cursor(connection)
        
        user_id = session['user_id']
        
        # Get patient data
        cursor.execute("""
            SELECT p.*, u.name, u.email, u.phone
            FROM patients p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.user_id = ?
        """, (user_id,))
        patient_data = cursor.fetchone()
        
        # Get upcoming appointments
        cursor.execute("""
            SELECT a.*, d.specialization, d.location, d.consultation_fee,
                   u.name as doctor_name
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            JOIN users u ON d.user_id = u.user_id
            WHERE a.patient_id = ? AND a.status IN ('pending', 'confirmed')
              AND a.appointment_date >= ?
            ORDER BY a.appointment_date ASC, a.appointment_time ASC
            LIMIT 5
        """, (patient_data['patient_id'], str(date.today())))
        upcoming_appointments = cursor.fetchall()
        
        # Get total appointments count
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM appointments
            WHERE patient_id = ?
        """, (patient_data['patient_id'],))
        total_appointments = cursor.fetchone()['total']
        
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('patient_dashboard.html', 
                         patient=patient_data,
                         upcoming_appointments=upcoming_appointments,
                         total_appointments=total_appointments)

@bp.route('/doctors')
@login_required
def doctors():
    """
    Search and browse doctors
    Allows filtering by specialization, location, etc.
    """
    connection = None
    doctors_list = []
    specializations = []
    
    # Get filter parameters
    search_name = request.args.get('search', '')
    specialization = request.args.get('specialization', '')
    location = request.args.get('location', '')
    
    try:
        connection = get_db_connection()
        cursor = get_dict_cursor(connection)
        
        # Get all specializations for filter dropdown
        cursor.execute("SELECT DISTINCT specialization FROM doctors WHERE is_verified = 1")
        specializations = [row['specialization'] for row in cursor.fetchall()]
        
        # Build query with filters
        query = """
            SELECT d.*, u.name, u.email, u.phone
            FROM doctors d
            JOIN users u ON d.user_id = u.user_id
            WHERE d.is_verified = 1
        """
        params = []
        
        if search_name:
            query += " AND u.name LIKE ?"
            params.append(f'%{search_name}%')
        
        if specialization:
            query += " AND d.specialization = ?"
            params.append(specialization)
        
        if location:
            query += " AND d.location LIKE ?"
            params.append(f'%{location}%')
        
        query += " ORDER BY d.experience DESC"
        
        cursor.execute(query, params)
        doctors_list = cursor.fetchall()
        
    except Exception as e:
        flash(f'Error loading doctors: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('doctors.html', 
                         doctors=doctors_list,
                         specializations=specializations,
                         search_name=search_name,
                         selected_specialization=specialization,
                         selected_location=location)

@bp.route('/doctor/<int:doctor_id>')
@login_required
def doctor_profile(doctor_id):
    """
    View doctor profile and availability
    """
    connection = None
    doctor_data = None
    availability = []
    
    try:
        connection = get_db_connection()
        cursor = get_dict_cursor(connection)
        
        # Get doctor details
        cursor.execute("""
            SELECT d.*, u.name, u.email, u.phone
            FROM doctors d
            JOIN users u ON d.user_id = u.user_id
            WHERE d.doctor_id = ?
        """, (doctor_id,))
        doctor_data = cursor.fetchone()
        
        if not doctor_data:
            flash('Doctor not found', 'error')
            return redirect(url_for('patient.doctors'))
        
        # Get doctor availability
        cursor.execute("""
            SELECT * FROM doctor_availability
            WHERE doctor_id = ? AND is_available = 1
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
        availability = cursor.fetchall()
        
    except Exception as e:
        flash(f'Error loading doctor profile: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('doctor_profile.html', 
                         doctor=doctor_data,
                         availability=availability)

@bp.route('/book/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def book_appointment(doctor_id):
    """
    Book an appointment with a doctor
    GET: Show booking form
    POST: Process booking
    """
    connection = None
    doctor_data = None
    
    if request.method == 'POST':
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        reason = request.form.get('reason')
        
        if not all([appointment_date, appointment_time, reason]):
            flash('Please fill in all fields', 'error')
            return redirect(url_for('patient.book_appointment', doctor_id=doctor_id))
        
        try:
            connection = get_db_connection()
            cursor = get_dict_cursor(connection)
            
            # Get patient ID
            cursor.execute("SELECT patient_id FROM patients WHERE user_id = ?", (session['user_id'],))
            patient = cursor.fetchone()
            patient_id = patient['patient_id']
            
            # Check if slot is already booked
            cursor.execute("""
                SELECT appointment_id FROM appointments
                WHERE doctor_id = ? AND appointment_date = ? AND appointment_time = ?
                AND status != 'cancelled'
            """, (doctor_id, appointment_date, appointment_time))
            
            if cursor.fetchone():
                flash('This time slot is already booked. Please choose another.', 'error')
                return redirect(url_for('patient.book_appointment', doctor_id=doctor_id))
            
            # Insert appointment
            cursor.execute("""
                INSERT INTO appointments (patient_id, doctor_id, appointment_date, 
                                         appointment_time, reason, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
            """, (patient_id, doctor_id, appointment_date, appointment_time, reason))
            
            connection.commit()
            flash('Appointment booked successfully! Waiting for doctor confirmation.', 'success')
            return redirect(url_for('patient.appointments'))
            
        except Exception as e:
            if connection:
                connection.rollback()
            flash(f'Booking failed: {str(e)}', 'error')
        finally:
            if connection:
                close_db_connection(connection)
    
    # GET request - show booking form
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT d.*, u.name
            FROM doctors d
            JOIN users u ON d.user_id = u.user_id
            WHERE d.doctor_id = ?
        """, (doctor_id,))
        doctor_data = cursor.fetchone()
        
        if not doctor_data:
            flash('Doctor not found', 'error')
            return redirect(url_for('patient.doctors'))
            
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('book_appointment.html', doctor=doctor_data)

@bp.route('/appointments')
@login_required
def appointments():
    """
    View patient's appointment history
    """
    connection = None
    appointments_list = []
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get patient ID
        cursor.execute("SELECT patient_id FROM patients WHERE user_id = ?", (session['user_id'],))
        patient = cursor.fetchone()
        patient_id = patient['patient_id']
        
        # Get filter parameter
        status_filter = request.args.get('status', '')
        
        # Build query
        query = """
            SELECT a.*, d.specialization, d.location, d.consultation_fee,
                   u.name as doctor_name
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            JOIN users u ON d.user_id = u.user_id
            WHERE a.patient_id = ?
        """
        params = [patient_id]
        
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
    
    return render_template('appointments.html', 
                         appointments=appointments_list,
                         status_filter=status_filter)

@bp.route('/cancel/<int:appointment_id>')
@login_required
def cancel_appointment(appointment_id):
    """
    Cancel an appointment
    """
    connection = None
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Get patient ID
        cursor.execute("SELECT patient_id FROM patients WHERE user_id = ?", (session['user_id'],))
        patient = cursor.fetchone()
        patient_id = patient['patient_id']
        
        # Update appointment status
        cursor.execute("""
            UPDATE appointments
            SET status = 'cancelled'
            WHERE appointment_id = ? AND patient_id = ?
        """, (appointment_id, patient_id))
        
        if cursor.rowcount > 0:
            connection.commit()
            flash('Appointment cancelled successfully', 'success')
        else:
            flash('Appointment not found or already cancelled', 'error')
            
    except Exception as e:
        if connection:
            connection.rollback()
        flash(f'Cancellation failed: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return redirect(url_for('patient.appointments'))

@bp.route('/reschedule/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def reschedule_appointment(appointment_id):
    """
    Reschedule an appointment
    """
    connection = None
    appointment_data = None
    
    if request.method == 'POST':
        new_date = request.form.get('appointment_date')
        new_time = request.form.get('appointment_time')
        
        if not all([new_date, new_time]):
            flash('Please select new date and time', 'error')
            return redirect(url_for('patient.reschedule_appointment', appointment_id=appointment_id))
        
        try:
            connection = get_db_connection()
            cursor = get_dict_cursor(connection)
            
            # Get patient ID and appointment details
            cursor.execute("SELECT patient_id FROM patients WHERE user_id = ?", (session['user_id'],))
            patient = cursor.fetchone()
            patient_id = patient['patient_id']
            
            cursor.execute("""
                SELECT doctor_id FROM appointments
                WHERE appointment_id = ? AND patient_id = ?
            """, (appointment_id, patient_id))
            appointment = cursor.fetchone()
            
            if not appointment:
                flash('Appointment not found', 'error')
                return redirect(url_for('patient.appointments'))
            
            doctor_id = appointment['doctor_id']
            
            # Check if new slot is available
            cursor.execute("""
                SELECT appointment_id FROM appointments
                WHERE doctor_id = ? AND appointment_date = ? AND appointment_time = ?
                AND status != 'cancelled' AND appointment_id != ?
            """, (doctor_id, new_date, new_time, appointment_id))
            
            if cursor.fetchone():
                flash('This time slot is already booked. Please choose another.', 'error')
                return redirect(url_for('patient.reschedule_appointment', appointment_id=appointment_id))
            
            # Update appointment
            cursor.execute("""
                UPDATE appointments
                SET appointment_date = ?, appointment_time = ?, status = 'pending'
                WHERE appointment_id = ?
            """, (new_date, new_time, appointment_id))
            
            connection.commit()
            flash('Appointment rescheduled successfully', 'success')
            return redirect(url_for('patient.appointments'))
            
        except Exception as e:
            if connection:
                connection.rollback()
            flash(f'Rescheduling failed: {str(e)}', 'error')
        finally:
            if connection:
                close_db_connection(connection)
    
    # GET request - show reschedule form
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT patient_id FROM patients WHERE user_id = ?", (session['user_id'],))
        patient = cursor.fetchone()
        patient_id = patient['patient_id']
        
        cursor.execute("""
            SELECT a.*, d.specialization, u.name as doctor_name
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            JOIN users u ON d.user_id = u.user_id
            WHERE a.appointment_id = ? AND a.patient_id = ?
        """, (appointment_id, patient_id))
        appointment_data = cursor.fetchone()
        
        if not appointment_data:
            flash('Appointment not found', 'error')
            return redirect(url_for('patient.appointments'))
            
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('reschedule_appointment.html', appointment=appointment_data)

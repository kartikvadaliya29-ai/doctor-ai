"""
AI Assistant Routes
Handles the Doctor AI symptom checker and medical suggestions
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db_connection, close_db_connection, get_dict_cursor
from functools import wraps

# Create blueprint for AI routes
bp = Blueprint('ai', __name__, url_prefix='/ai')

# Login required decorator for patient routes
def login_required(f):
    """Decorator to ensure user is logged in as patient"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this feature', 'error')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'patient':
            flash('Access denied. Patient access only.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Simple rule-based symptom analysis
def analyze_symptoms(symptoms):
    """
    Analyze symptoms and suggest appropriate doctor specialization
    This is a simple rule-based system for demonstration purposes
    
    Args:
        symptoms (str): Patient's symptoms description
        
    Returns:
        dict: Contains suggested specialization and general advice
    """
    symptoms_lower = symptoms.lower()
    
    # Define symptom patterns and corresponding specializations
    symptom_patterns = {
        'cardiologist': [
            'chest pain', 'chest discomfort', 'heart', 'palpitation', 
            'shortness of breath', 'high blood pressure', 'heart attack'
        ],
        'dermatologist': [
            'skin', 'rash', 'acne', 'itch', 'eczema', 'psoriasis', 
            'fungal', 'dermatitis', 'allergy'
        ],
        'dentist': [
            'tooth', 'dental', 'gum', 'jaw', 'mouth', 'teeth', 
            'cavity', 'toothache', 'bleeding gum'
        ],
        'neurologist': [
            'headache', 'migraine', 'dizziness', 'seizure', 'memory', 
            'numbness', 'tingling', 'stroke', 'brain'
        ],
        'ophthalmologist': [
            'eye', 'vision', 'sight', 'blurry', 'red eye', 'eye pain',
            'cataract', 'glaucoma'
        ],
        'orthopedic': [
            'bone', 'joint', 'fracture', 'arthritis', 'back pain', 
            'neck pain', 'muscle', 'sprain', 'injury'
        ],
        'general physician': [
            'fever', 'cold', 'flu', 'cough', 'throat', 'vomiting', 
            'diarrhea', 'stomach', 'nausea', 'fatigue', 'weakness'
        ],
        'gynecologist': [
            'menstrual', 'period', 'pregnancy', 'women', 'female',
            'uterine', 'ovarian'
        ],
        'pediatrician': [
            'child', 'baby', 'infant', 'kid', 'toddler'
        ],
        'psychiatrist': [
            'depression', 'anxiety', 'stress', 'mental', 'mood',
            'insomnia', 'sleep'
        ]
    }
    
    # Check for matches
    matched_specializations = []
    for specialization, patterns in symptom_patterns.items():
        for pattern in patterns:
            if pattern in symptoms_lower:
                if specialization not in matched_specializations:
                    matched_specializations.append(specialization)
                break
    
    # Default to general physician if no specific match
    if not matched_specializations:
        matched_specializations = ['general physician']
    
    # General advice based on symptoms
    general_advice = []
    
    if 'fever' in symptoms_lower or 'temperature' in symptoms_lower:
        general_advice.append("Monitor your temperature regularly")
        general_advice.append("Stay hydrated and rest")
    
    if 'pain' in symptoms_lower:
        general_advice.append("If pain is severe, seek immediate medical attention")
    
    if 'bleeding' in symptoms_lower:
        general_advice.append("Apply pressure to stop bleeding")
        general_advice.append("Seek medical help if bleeding doesn't stop")
    
    if 'breathing' in symptoms_lower or 'breath' in symptoms_lower:
        general_advice.append("Difficulty breathing requires immediate medical attention")
    
    if any(symptom in symptoms_lower for symptom in ['chest', 'heart', 'stroke']):
        general_advice.append("These symptoms may require emergency care")
        general_advice.append("Call emergency services if symptoms are severe")
    
    # Default advice
    if not general_advice:
        general_advice.append("Rest and stay hydrated")
        general_advice.append("Monitor your symptoms")
        general_advice.append("If symptoms persist or worsen, consult a doctor")
    
    return {
        'specializations': matched_specializations,
        'advice': general_advice,
        'disclaimer': (
            "This AI assistant is for educational and demonstration purposes only. "
            "It is NOT a replacement for professional medical advice, diagnosis, or treatment. "
            "Always consult a qualified healthcare provider for medical concerns. "
            "In case of emergency, call emergency services immediately."
        )
    }

@bp.route('/assistant')
@login_required
def assistant():
    """
    Display the AI assistant interface
    """
    connection = None
    query_history = []
    
    try:
        connection = get_db_connection()
        cursor = get_dict_cursor(connection)
        
        # Get patient ID
        cursor.execute("SELECT patient_id FROM patients WHERE user_id = ?", (session['user_id'],))
        patient = cursor.fetchone()
        
        if patient:
            # Get query history
            cursor.execute("""
                SELECT * FROM ai_queries
                WHERE patient_id = ?
                ORDER BY created_at DESC
                LIMIT 10
            """, (patient['patient_id'],))
            query_history = cursor.fetchall()
        
    except Exception as e:
        flash(f'Error loading query history: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('ai_assistant.html', query_history=query_history)

@bp.route('/query', methods=['POST'])
@login_required
def submit_query():
    """
    Process symptom query and provide AI suggestions
    """
    symptoms = request.form.get('symptoms')
    
    if not symptoms:
        flash('Please describe your symptoms', 'error')
        return redirect(url_for('ai.assistant'))
    
    # Analyze symptoms
    analysis = analyze_symptoms(symptoms)
    
    # Save query to database
    connection = None
    try:
        connection = get_db_connection()
        cursor = get_dict_cursor(connection)
        
        # Get patient ID
        cursor.execute("SELECT patient_id FROM patients WHERE user_id = ?", (session['user_id'],))
        patient = cursor.fetchone()
        
        if patient:
            # Save query
            cursor.execute("""
                INSERT INTO ai_queries (patient_id, symptoms, response, suggested_specialization)
                VALUES (?, ?, ?, ?)
            """, (
                patient['patient_id'],
                symptoms,
                str(analysis['advice']),
                ', '.join(analysis['specializations'])
            ))
            
            connection.commit()
        
    except Exception as e:
        if connection:
            connection.rollback()
        flash(f'Error saving query: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('ai_result.html', 
                         symptoms=symptoms,
                         analysis=analysis)

@bp.route('/history')
@login_required
def query_history():
    """
    View complete query history
    """
    connection = None
    query_history = []
    
    try:
        connection = get_db_connection()
        cursor = get_dict_cursor(connection)
        
        # Get patient ID
        cursor.execute("SELECT patient_id FROM patients WHERE user_id = ?", (session['user_id'],))
        patient = cursor.fetchone()
        
        if patient:
            # Get all query history
            cursor.execute("""
                SELECT * FROM ai_queries
                WHERE patient_id = ?
                ORDER BY created_at DESC
            """, (patient['patient_id'],))
            query_history = cursor.fetchall()
        
    except Exception as e:
        flash(f'Error loading query history: {str(e)}', 'error')
    finally:
        if connection:
            close_db_connection(connection)
    
    return render_template('ai_history.html', query_history=query_history)

"""
Doctor AI - Hospital Appointment Management System
Main Flask Application
"""

from flask import Flask, render_template, session, redirect, url_for
from config import Config
from datetime import datetime
import os

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Custom Jinja2 filter for date formatting
@app.template_filter('format_date')
def format_date(date_value):
    """Format date for display - handles both datetime objects and strings"""
    if not date_value:
        return ''
    
    if isinstance(date_value, str):
        try:
            # Try to parse date string
            if len(date_value) == 10 and date_value.count('-') == 2:
                date_obj = datetime.strptime(date_value, '%Y-%m-%d')
                return date_obj.strftime('%Y-%m-%d')
            elif len(date_value) == 8 and date_value.count(':') == 2:
                time_obj = datetime.strptime(date_value, '%H:%M:%S')
                return time_obj.strftime('%H:%M')
            elif 'T' in date_value:
                dt_obj = datetime.strptime(date_value, '%Y-%m-%dT%H:%M:%S')
                return dt_obj.strftime('%Y-%m-%d %H:%M')
            elif ' ' in date_value:
                dt_obj = datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S')
                return dt_obj.strftime('%Y-%m-%d %H:%M')
        except ValueError:
            return date_value
    elif hasattr(date_value, 'strftime'):
        return date_value.strftime('%Y-%m-%d')
    
    return str(date_value)

@app.template_filter('format_time')
def format_time(time_value):
    """Format time for display - handles both datetime objects and strings"""
    if not time_value:
        return ''
    
    if isinstance(time_value, str):
        try:
            if len(time_value) == 8 and time_value.count(':') == 2:
                time_obj = datetime.strptime(time_value, '%H:%M:%S')
                return time_obj.strftime('%H:%M')
        except ValueError:
            return time_value
    elif hasattr(time_value, 'strftime'):
        return time_value.strftime('%H:%M')
    
    return str(time_value)

# Import route modules
from routes import auth, patient, doctor, admin, ai

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(patient.bp)
app.register_blueprint(doctor.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(ai.bp)

# Main route - Landing page
@app.route('/')
def index():
    """Render the landing page"""
    return render_template('index.html')

@app.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Run the Flask application
    # Debug mode for development (disable in production)
    app.run(debug=True, host='0.0.0.0', port=5000)

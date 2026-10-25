"""
Configuration file for Doctor AI application
Contains database connection settings and Flask configuration
"""
import os
import sqlite3

class Config:
    """Application configuration class"""
    
    # Secret key for session management (in production, use environment variable)
    SECRET_KEY = 'your-secret-key-change-this-in-production'
    
    # Database configuration - Using SQLite (no MySQL required)
    DB_TYPE = 'sqlite'  # Change to 'mysql' if you want to use MySQL
    DB_NAME = 'doctor_ai.db'
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'doctor_ai.db')    
    # MySQL configuration (only used if DB_TYPE = 'mysql')
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = ''  # Add your MySQL password here

"""
Database connection handler for Doctor AI application
Handles SQLite and MySQL database connections and cursor management
"""

import sqlite3
from config import Config

# Try to import MySQL connector if available
try:
    import mysql.connector
    from mysql.connector import Error
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

def get_db_connection():
    """
    Create and return a database connection
    
    Returns:
        Database connection object (SQLite or MySQL)
        
    Raises:
        Exception: If connection fails
    """
    try:
        if Config.DB_TYPE == 'sqlite' or not MYSQL_AVAILABLE:
            # Use SQLite
            connection = sqlite3.connect(Config.DB_PATH)
            connection.row_factory = sqlite3.Row  # This makes rows behave like dictionaries
            return connection
        else:
            # Use MySQL
            connection = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME
            )
            return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise Exception("Database connection failed. Please check your database configuration.")

def get_dict_cursor(connection):
    """
    Create and return a dictionary cursor
    
    Args:
        connection: Database connection object
        
    Returns:
        Dictionary cursor object
    """
    if Config.DB_TYPE == 'sqlite' or not MYSQL_AVAILABLE:
        # SQLite already has row_factory set to sqlite3.Row
        return connection.cursor()
    else:
        # MySQL needs dictionary cursor
        return connection.cursor(dictionary=True)

def close_db_connection(connection):
    """
    Close the database connection
    
    Args:
        connection: Database connection object to close
    """
    try:
        if Config.DB_TYPE == 'sqlite' or not MYSQL_AVAILABLE:
            if connection:
                connection.close()
        else:
            if connection and connection.is_connected():
                connection.close()
    except:
        pass

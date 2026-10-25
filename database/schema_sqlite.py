"""
SQLite Database Schema and Sample Data for Doctor AI
Run this script to create the SQLite database with sample data
"""

import sqlite3
from datetime import datetime, timedelta
import random

def create_sqlite_database():
    """Create SQLite database with all tables and sample data"""
    
    # Connect to SQLite database
    conn = sqlite3.connect('doctor_ai.db')
    cursor = conn.cursor()
    
    print("Creating SQLite database for Doctor AI...")
    
    # Drop existing tables if they exist
    cursor.execute("DROP TABLE IF EXISTS ai_queries")
    cursor.execute("DROP TABLE IF EXISTS notifications")
    cursor.execute("DROP TABLE IF EXISTS medical_records")
    cursor.execute("DROP TABLE IF EXISTS appointments")
    cursor.execute("DROP TABLE IF EXISTS doctor_availability")
    cursor.execute("DROP TABLE IF EXISTS doctors")
    cursor.execute("DROP TABLE IF EXISTS patients")
    cursor.execute("DROP TABLE IF EXISTS users")
    
    # Create users table
    cursor.execute("""
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('patient', 'doctor', 'admin')),
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create patients table
    cursor.execute("""
        CREATE TABLE patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            date_of_birth DATE,
            gender TEXT CHECK(gender IN ('male', 'female', 'other')),
            address TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
    # Create doctors table
    cursor.execute("""
        CREATE TABLE doctors (
            doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            specialization TEXT NOT NULL,
            qualification TEXT,
            experience INTEGER,
            hospital TEXT,
            location TEXT,
            consultation_fee REAL,
            bio TEXT,
            is_verified BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
    # Create doctor_availability table
    cursor.execute("""
        CREATE TABLE doctor_availability (
            availability_id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER NOT NULL,
            day_of_week TEXT NOT NULL CHECK(day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            is_available BOOLEAN DEFAULT 1,
            FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
        )
    """)
    
    # Create appointments table
    cursor.execute("""
        CREATE TABLE appointments (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            appointment_date DATE NOT NULL,
            appointment_time TEXT NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'confirmed', 'completed', 'cancelled')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
            FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
        )
    """)
    
    # Create medical_records table
    cursor.execute("""
        CREATE TABLE medical_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            appointment_id INTEGER UNIQUE NOT NULL,
            diagnosis TEXT,
            notes TEXT,
            prescription TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
            FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE,
            FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE
        )
    """)
    
    # Create notifications table
    cursor.execute("""
        CREATE TABLE notifications (
            notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)
    
    # Create ai_queries table
    cursor.execute("""
        CREATE TABLE ai_queries (
            query_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            symptoms TEXT NOT NULL,
            response TEXT,
            suggested_specialization TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
        )
    """)
    
    print("Tables created successfully!")
    
    # Insert sample data
    print("Inserting sample data...")
    
    # Sample patients
    patients_data = [
        ('John Smith', 'john.smith@email.com', 'pbkdf2:sha256:260000$random_salt$password123', 'patient', '555-0101',
         '1990-05-15', 'male', '123 Main St, City'),
        ('Sarah Johnson', 'sarah.j@email.com', 'pbkdf2:sha256:260000$random_salt$password123', 'patient', '555-0102',
         '1985-08-22', 'female', '456 Oak Ave, Town'),
        ('Michael Brown', 'michael.b@email.com', 'pbkdf2:sha256:260000$random_salt$password123', 'patient', '555-0103',
         '1992-03-10', 'male', '789 Pine Rd, Village'),
        ('Emily Davis', 'emily.d@email.com', 'pbkdf2:sha256:260000$random_salt$password123', 'patient', '555-0104',
         '1988-11-30', 'female', '321 Elm St, Metro'),
        ('David Wilson', 'david.w@email.com', 'pbkdf2:sha256:260000$random_salt$password123', 'patient', '555-0105',
         '1995-07-18', 'male', '654 Maple Dr, County'),
    ]
    
    for patient in patients_data:
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role, phone)
            VALUES (?, ?, ?, ?, ?)
        """, (patient[0], patient[1], patient[2], patient[3], patient[4]))
        user_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO patients (user_id, date_of_birth, gender, address)
            VALUES (?, ?, ?, ?)
        """, (user_id, patient[5], patient[6], patient[7]))
    
    # Sample doctors
    doctors_data = [
        ('Dr. Amanda Martinez', 'dr.martinez@email.com', 'pbkdf2:sha256:260000$random_salt$password123', 'doctor', '555-1001',
         'General Physician', 'MBBS, MD', 15, 'City General Hospital', 'New York', 100.00,
         'Experienced general physician with expertise in primary care and preventive medicine.', 1),
        ('Dr. James Rodriguez', 'dr.rodriguez@email.com', 'pbkdf2:sha256:260000$random_salt$password123', 'doctor', '555-1002',
         'Cardiologist', 'MBBS, MD (Cardiology)', 12, 'Heart Care Center', 'Los Angeles', 250.00,
         'Specialist in heart diseases and cardiovascular conditions.', 1),
        ('Dr. Emily Chen', 'dr.chen@email.com', 'pbkdf2:sha256:260000$random_salt$password123', 'doctor', '555-1003',
         'Dermatologist', 'MBBS, MD (Dermatology)', 8, 'Skin Health Clinic', 'Chicago', 150.00,
         'Expert in treating skin conditions and dermatological disorders.', 1),
    ]
    
    for doctor in doctors_data:
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role, phone)
            VALUES (?, ?, ?, ?, ?)
        """, (doctor[0], doctor[1], doctor[2], doctor[3], doctor[4]))
        user_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO doctors (user_id, specialization, qualification, experience, hospital, location, consultation_fee, bio, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, doctor[5], doctor[6], doctor[7], doctor[8], doctor[9], doctor[10], doctor[11], doctor[12]))
    
    # Sample doctor availability
    availability_data = [
        (1, 'Monday', '09:00', '17:00'),
        (1, 'Tuesday', '09:00', '17:00'),
        (1, 'Wednesday', '09:00', '17:00'),
        (1, 'Thursday', '09:00', '17:00'),
        (1, 'Friday', '09:00', '15:00'),
        (2, 'Monday', '10:00', '18:00'),
        (2, 'Wednesday', '10:00', '18:00'),
        (2, 'Friday', '10:00', '18:00'),
        (3, 'Tuesday', '09:00', '16:00'),
        (3, 'Thursday', '09:00', '16:00'),
        (3, 'Saturday', '09:00', '14:00'),
    ]
    
    for avail in availability_data:
        cursor.execute("""
            INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time, is_available)
            VALUES (?, ?, ?, ?, 1)
        """, avail)
    
    # Sample appointments
    appointments_data = [
        (1, 1, '2026-09-28', '10:00', 'Routine checkup', 'confirmed'),
        (1, 2, '2026-10-05', '14:00', 'Heart palpitations', 'pending'),
        (2, 3, '2026-09-29', '11:00', 'Skin rash', 'confirmed'),
        (3, 1, '2026-09-30', '09:00', 'Fever and body ache', 'pending'),
        (4, 2, '2026-10-02', '15:00', 'Migraine', 'confirmed'),
    ]
    
    for appt in appointments_data:
        cursor.execute("""
            INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, appt)
    
    # Sample medical records
    medical_records_data = [
        (2, 1, 10, 'General health good', 'Patient shows normal vital signs. Annual physical completed successfully.', 'Vitamin D supplements, continue regular exercise'),
        (3, 3, 11, 'Acne vulgaris', 'Moderate acne on face and back. Recommend topical treatment.', 'Benzoyl peroxide gel, salicylic acid wash'),
    ]
    
    for record in medical_records_data:
        cursor.execute("""
            INSERT INTO medical_records (patient_id, doctor_id, appointment_id, diagnosis, notes, prescription)
            VALUES (?, ?, ?, ?, ?, ?)
        """, record)
    
    # Admin user
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, role, phone)
        VALUES ('Admin User', 'admin@doctorai.com', 'pbkdf2:sha256:260000$random_salt$password123', 'admin', '555-0000')
    """)
    
    # Commit all changes
    conn.commit()
    print("Sample data inserted successfully!")
    
    # Verify data
    print("\nVerifying data...")
    cursor.execute("SELECT COUNT(*) FROM users")
    print(f"Total users: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM patients")
    print(f"Total patients: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM doctors")
    print(f"Total doctors: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM appointments")
    print(f"Total appointments: {cursor.fetchone()[0]}")
    
    conn.close()
    print("\nSQLite database created successfully!")
    print("Database location: doctor_ai.db")
    print("Password for all accounts: password123")

if __name__ == "__main__":
    create_sqlite_database()

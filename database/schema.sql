-- ================================================
-- Doctor AI Database Schema
-- ================================================
-- This file creates all tables for the Doctor AI
-- Hospital Appointment Management System
-- ================================================

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS doctor_ai_db;
USE doctor_ai_db;

-- ================================================
-- USERS TABLE
-- Stores user authentication information
-- ================================================
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('patient', 'doctor', 'admin') NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ================================================
-- PATIENTS TABLE
-- Stores patient-specific information
-- Relationship: One user (with role='patient') -> One patient
-- ================================================
CREATE TABLE IF NOT EXISTS patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    date_of_birth DATE,
    gender ENUM('male', 'female', 'other'),
    address TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ================================================
-- DOCTORS TABLE
-- Stores doctor-specific information
-- Relationship: One user (with role='doctor') -> One doctor
-- ================================================
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    qualification VARCHAR(200),
    experience INT COMMENT 'Years of experience',
    hospital VARCHAR(100),
    location VARCHAR(100),
    consultation_fee DECIMAL(10, 2),
    bio TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_specialization (specialization),
    INDEX idx_location (location)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ================================================
-- DOCTOR AVAILABILITY TABLE
-- Stores doctor availability schedule
-- Relationship: One doctor -> Many availability records
-- ================================================
CREATE TABLE IF NOT EXISTS doctor_availability (
    availability_id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT NOT NULL,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    INDEX idx_doctor_id (doctor_id),
    INDEX idx_day (day_of_week),
    CONSTRAINT chk_time_order CHECK (start_time < end_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ================================================
-- APPOINTMENTS TABLE
-- Stores appointment information
-- Relationship: One patient -> Many appointments
-- Relationship: One doctor -> Many appointments
-- ================================================
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    reason TEXT,
    status ENUM('pending', 'confirmed', 'completed', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    UNIQUE KEY unique_appointment (doctor_id, appointment_date, appointment_time),
    INDEX idx_patient_id (patient_id),
    INDEX idx_doctor_id (doctor_id),
    INDEX idx_date (appointment_date),
    INDEX idx_status (status),
    CONSTRAINT chk_appointment_date CHECK (appointment_date >= CURDATE())
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ================================================
-- MEDICAL RECORDS TABLE
-- Stores medical records/notes for appointments
-- Relationship: One appointment -> One medical record
-- ================================================
CREATE TABLE IF NOT EXISTS medical_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_id INT UNIQUE NOT NULL,
    diagnosis TEXT,
    notes TEXT,
    prescription TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_doctor_id (doctor_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ================================================
-- NOTIFICATIONS TABLE
-- Stores notifications for users
-- Relationship: One user -> Many notifications
-- ================================================
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_is_read (is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ================================================
-- AI QUERIES TABLE
-- Stores AI assistant queries from patients
-- Relationship: One patient -> Many AI queries
-- ================================================
CREATE TABLE IF NOT EXISTS ai_queries (
    query_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    symptoms TEXT NOT NULL,
    response TEXT,
    suggested_specialization VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ================================================
-- SAMPLE DATA INSERTION
-- ================================================

-- Insert sample users (patients)
-- All passwords are 'password123' for demo purposes
INSERT INTO users (name, email, password_hash, role, phone) VALUES
('John Smith', 'john.smith@email.com', 'scrypt:32768:8:1$kSxXlV3p$2aG9x8mK4nL6pQ1rS5tU7vW2yZ4bC6dE8fG0hI2jK4lM6nO8p', 'patient', '555-0101'),
('Sarah Johnson', 'sarah.j@email.com', 'scrypt:32768:8:1$kSxXlV3p$2aG9x8mK4nL6pQ1rS5tU7vW2yZ4bC6dE8fG0hI2jK4lM6nO8p', 'patient', '555-0102'),
('Michael Brown', 'michael.b@email.com', 'scrypt:32768:8:1$kSxXlV3p$2aG9x8mK4nL6pQ1rS5tU7vW2yZ4bC6dE8fG0hI2jK4lM6nO8p', 'patient', '555-0103'),
('Emily Davis', 'emily.d@email.com', 'scrypt:32768:8:1$kSxXlV3p$2aG9x8mK4nL6pQ1rS5tU7vW2yZ4bC6dE8fG0hI2jK4lM6nO8p', 'patient', '555-0104'),
('David Wilson', 'david.w@email.com', 'scrypt:32768:8:1$kSxXlV3p$2aG9x8mK4nL6pQ1rS5tU7vW2yZ4bC6dE8fG0hI2jK4lM6nO8p', 'patient', '555-0105'),
('Jessica Taylor', 'jessica.t@email.com', 'scrypt:32768:8:1$kSxXlV3p$2aG9x8mK4nL6pQ1rS5tU7vW2yZ4bC6dE8fG0hI2jK4lM6nO8p', 'patient', '555-0106'),
('Robert Anderson', 'robert.a@email.com', 'scrypt:32768:8:1$kSxXlV3p$2aG9x8mK4nL6pQ1rS5tU7vW2yZ4bC6dE8fG0hI2jK4lM6nO8p', 'patient', '555-0107'),
('Lisa Thomas', 'lisa.t@email.com', 'scrypt:32768:8:1$kSxXlV3p$2aG9x8mK4nL6pQ1rS5tU7vW2yZ4bC6dE8fG0hI2jK4lM6nO8p', 'patient', '555-0108'),
('James Jackson', 'james.j@email.com', 'scrypt:32768:8:1$kSxXlV3p$2aG9x8mK4nL6pQ1rS5tU7vW2yZ4bC6dE8fG0hI2jK4lM6nO8p', 'patient', '555-0109'),
('Maria White', 'maria.w@email.com', 'scrypt:32768:8:1$kSxXlV3p$2aG9x8mK4nL6pQ1rS5tU7vW2yZ4bC6dE8fG0hI2jK4lM6nO8p', 'patient', '555-0110');

-- Insert patient details
INSERT INTO patients (user_id, date_of_birth, gender, address) VALUES
(1, '1990-05-15', 'male', '123 Main St, City'),
(2, '1985-08-22', 'female', '456 Oak Ave, Town'),
(3, '1992-03-10', 'male', '789 Pine Rd, Village'),
(4, '1988-11-30', 'female', '321 Elm St, Metro'),
(5, '1995-07-18', 'male', '654 Maple Dr, County'),
(6, '1991-02-14', 'female', '987 Cedar Ln, District'),
(7, '1987-09-25', 'male', '147 Birch Blvd, State'),
(8, '1993-12-05', 'female', '258 Spruce Way, Region'),
(9, '1989-04-20', 'male', '369 Willow Cir, Province'),
(10, '1994-06-12', 'female', '741 Aspen Pl, Territory');

-- Insert sample users (doctors)
-- All passwords are 'password123' for demo purposes
INSERT INTO users (name, email, password_hash, role, phone) VALUES
('Dr. Amanda Martinez', 'dr.martinez@email.com', 'scrypt:32768:8:1$kSxXlV3p$2aG9x8mK4nL6pQ1rS5tU7vW2yZ4bC6dE8fG0hI2jK4lM6nO8p', 'doctor', '555-1001'),
('Dr. James Rodriguez', 'dr.rodriguez@email.com', 'scrypt:32768:8:1$kSxXlV3p$2aG9x8mK4nL6pQ1rS5tU7vW2yZ4bC6dE8fG0hI2jK4lM6nO8p', 'doctor', '555-1002'),
('Dr. Emily Chen', 'dr.chen@email.com', 'scrypt:32768:8:1$kSxXlV3p$2aG9x8mK4nL6pQ1rS5tU7vW2yZ4bC6dE8fG0hI2jK4lM6nO8p', 'doctor', '555-1003'),
('Dr. Robert Williams', 'dr.williams@email.com', 'scrypt:32768:8:1$kSxXlV3p$2aG9x8mK4nL6pQ1rS5tU7vW2yZ4bC6dE8fG0hI2jK4lM6nO8p', 'doctor', '555-1004'),
('Dr. Lisa Thompson', 'dr.thompson@email.com', 'scrypt:32768:8:1$kSxXlV3p$2aG9x8mK4nL6pQ1rS5tU7vW2yZ4bC6dE8fG0hI2jK4lM6nO8p', 'doctor', '555-1005');

-- Insert doctor details
INSERT INTO doctors (user_id, specialization, qualification, experience, hospital, location, consultation_fee, bio, is_verified) VALUES
(11, 'General Physician', 'MBBS, MD', 15, 'City General Hospital', 'New York', 100.00, 'Experienced general physician with expertise in primary care and preventive medicine.', TRUE),
(12, 'Cardiologist', 'MBBS, MD (Cardiology)', 12, 'Heart Care Center', 'Los Angeles', 250.00, 'Specialist in heart diseases and cardiovascular conditions.', TRUE),
(13, 'Dermatologist', 'MBBS, MD (Dermatology)', 8, 'Skin Health Clinic', 'Chicago', 150.00, 'Expert in treating skin conditions and dermatological disorders.', TRUE),
(14, 'Neurologist', 'MBBS, MD (Neurology)', 18, 'Neuro Care Institute', 'Houston', 300.00, 'Specialist in nervous system disorders and brain conditions.', TRUE),
(15, 'Dentist', 'BDS, MDS', 10, 'Dental Care Plus', 'Phoenix', 80.00, 'Expert in dental care and oral hygiene.', TRUE);

-- Insert doctor availability
INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time, is_available) VALUES
(1, 'Monday', '09:00:00', '17:00:00', TRUE),
(1, 'Tuesday', '09:00:00', '17:00:00', TRUE),
(1, 'Wednesday', '09:00:00', '17:00:00', TRUE),
(1, 'Thursday', '09:00:00', '17:00:00', TRUE),
(1, 'Friday', '09:00:00', '15:00:00', TRUE),
(2, 'Monday', '10:00:00', '18:00:00', TRUE),
(2, 'Wednesday', '10:00:00', '18:00:00', TRUE),
(2, 'Friday', '10:00:00', '18:00:00', TRUE),
(3, 'Tuesday', '09:00:00', '16:00:00', TRUE),
(3, 'Thursday', '09:00:00', '16:00:00', TRUE),
(3, 'Saturday', '09:00:00', '14:00:00', TRUE),
(4, 'Monday', '08:00:00', '16:00:00', TRUE),
(4, 'Wednesday', '08:00:00', '16:00:00', TRUE),
(4, 'Friday', '08:00:00', '16:00:00', TRUE),
(5, 'Monday', '09:00:00', '17:00:00', TRUE),
(5, 'Tuesday', '09:00:00', '17:00:00', TRUE),
(5, 'Wednesday', '09:00:00', '17:00:00', TRUE),
(5, 'Thursday', '09:00:00', '17:00:00', TRUE),
(5, 'Friday', '09:00:00', '17:00:00', TRUE);

-- Insert sample appointments
INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason, status) VALUES
(1, 1, '2026-09-28', '10:00:00', 'Routine checkup', 'confirmed'),
(1, 2, '2026-10-05', '14:00:00', 'Heart palpitations', 'pending'),
(2, 3, '2026-09-29', '11:00:00', 'Skin rash', 'confirmed'),
(3, 1, '2026-09-30', '09:00:00', 'Fever and body ache', 'pending'),
(4, 4, '2026-10-02', '15:00:00', 'Migraine', 'confirmed'),
(5, 5, '2026-10-08', '10:00:00', 'Tooth pain', 'pending'),
(2, 1, '2026-09-15', '09:00:00', 'Annual physical', 'completed'),
(3, 3, '2026-09-10', '10:00:00', 'Acne treatment', 'completed'),
(1, 2, '2026-09-01', '11:00:00', 'Chest discomfort', 'cancelled'),
(4, 5, '2026-09-05', '14:00:00', 'Dental cleaning', 'completed');

-- Insert sample medical records
INSERT INTO medical_records (patient_id, doctor_id, appointment_id, diagnosis, notes, prescription) VALUES
(2, 1, 10, 'General health good', 'Patient shows normal vital signs. Annual physical completed successfully.', 'Vitamin D supplements, continue regular exercise'),
(3, 3, 11, 'Acne vulgaris', 'Moderate acne on face and back. Recommend topical treatment.', 'Benzoyl peroxide gel, salicylic acid wash'),
(4, 5, 15, 'General dental health good', 'Teeth cleaning completed. No cavities found.', 'Regular brushing twice daily, floss daily');

-- Insert admin user
-- Password is 'password123' for demo purposes
INSERT INTO users (name, email, password_hash, role, phone) VALUES
('Admin User', 'admin@doctorai.com', 'scrypt:32768:8:1$kSxXlV3p$2aG9x8mK4nL6pQ1rS5tU7vW2yZ4bC6dE8fG0hI2jK4lM6nO8p', 'admin', '555-0000');

-- ================================================
-- USEFUL SQL QUERIES FOR REPORTS
-- ================================================

-- Find all appointments of a particular patient
-- SELECT * FROM appointments WHERE patient_id = 1;

-- Find all appointments of a particular doctor
-- SELECT * FROM appointments WHERE doctor_id = 1;

-- Find available doctors by specialization
-- SELECT d.*, u.name, u.email FROM doctors d 
-- JOIN users u ON d.user_id = u.user_id 
-- WHERE d.specialization = 'Cardiologist' AND d.is_verified = TRUE;

-- Count appointments per doctor
-- SELECT d.doctor_id, u.name, COUNT(a.appointment_id) as total_appointments 
-- FROM doctors d 
-- JOIN users u ON d.user_id = u.user_id 
-- LEFT JOIN appointments a ON d.doctor_id = a.doctor_id 
-- GROUP BY d.doctor_id, u.name;

-- Show completed appointments
-- SELECT a.*, p.patient_id, d.doctor_id, up.name as patient_name, ud.name as doctor_name 
-- FROM appointments a 
-- JOIN patients p ON a.patient_id = p.patient_id 
-- JOIN doctors d ON a.doctor_id = d.doctor_id 
-- JOIN users up ON p.user_id = up.user_id 
-- JOIN users ud ON d.user_id = ud.user_id 
-- WHERE a.status = 'completed';

-- Show upcoming appointments
-- SELECT a.*, p.patient_id, d.doctor_id, up.name as patient_name, ud.name as doctor_name 
-- FROM appointments a 
-- JOIN patients p ON a.patient_id = p.patient_id 
-- JOIN doctors d ON a.doctor_id = d.doctor_id 
-- JOIN users up ON p.user_id = up.user_id 
-- JOIN users ud ON d.user_id = ud.user_id 
-- WHERE a.status IN ('pending', 'confirmed') AND a.appointment_date >= CURDATE();

-- Find the most requested doctor specializations
-- SELECT d.specialization, COUNT(a.appointment_id) as request_count 
-- FROM doctors d 
-- JOIN appointments a ON d.doctor_id = a.doctor_id 
-- GROUP BY d.specialization 
-- ORDER BY request_count DESC;

-- View patient appointment history with doctor details
-- SELECT a.appointment_id, a.appointment_date, a.appointment_time, a.status, a.reason,
--        ud.name as doctor_name, d.specialization, d.consultation_fee
-- FROM appointments a
-- JOIN doctors d ON a.doctor_id = d.doctor_id
-- JOIN users ud ON d.user_id = ud.user_id
-- WHERE a.patient_id = 1
-- ORDER BY a.appointment_date DESC;

-- View doctor availability schedule
-- SELECT da.*, d.specialization, u.name as doctor_name
-- FROM doctor_availability da
-- JOIN doctors d ON da.doctor_id = d.doctor_id
-- JOIN users u ON d.user_id = u.user_id
-- WHERE da.doctor_id = 1
-- ORDER BY FIELD(da.day_of_week, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday');

# Doctor AI - Hospital Appointment Management System

## Project Title
**Doctor AI: Hospital Appointment Management System**

## Project Objective
The objective of this project is to create a comprehensive web-based healthcare management system where patients can find doctors, book appointments, view their appointment history, and interact with an AI-style medical assistant. Doctors can manage their profiles, appointments, patients, and availability. The project demonstrates practical application of Python programming, web development with Flask, database management with MySQL, and implementation of CRUD operations with proper database relationships.

## Problem Statement
Traditional healthcare appointment booking systems are often inefficient, requiring patients to make phone calls, visit clinics in person, or navigate complex booking processes. Doctors struggle with managing their schedules and patient information effectively. Doctor AI addresses these challenges by providing a centralized, user-friendly platform that benefits both patients and healthcare providers through a modern web interface.

## Features

### Patient Module
- **User Registration**: Create patient accounts with personal information
- **User Login**: Secure authentication with session management
- **Doctor Search**: Search and filter doctors by name, specialization, and location
- **Doctor Profiles**: View detailed doctor information including qualifications, experience, and availability
- **Appointment Booking**: Book appointments with preferred date and time
- **Appointment Management**: View, cancel, and reschedule appointments
- **Appointment History**: Track all past and upcoming appointments
- **AI Medical Assistant**: Describe symptoms and get doctor specialization suggestions
- **Profile Management**: View and update personal information

### Doctor Module
- **Doctor Registration**: Create professional profiles with qualifications and specialization
- **Dashboard**: Overview of appointments, statistics, and quick actions
- **Appointment Management**: Accept, reject, and complete appointments
- **Medical Records**: Add diagnosis, notes, and prescriptions for completed appointments
- **Availability Management**: Set working days and time slots
- **Patient Management**: View list of patients and their appointment history
- **Profile Management**: Update professional information

### Admin Module
- **Dashboard**: System overview with key statistics
- **User Management**: View and manage patients and doctors
- **Doctor Verification**: Verify doctor accounts
- **Appointment Overview**: View all system appointments
- **Statistics**: Detailed analytics and reports

### AI Assistant
- **Symptom Analysis**: Rule-based system to suggest appropriate doctor specializations
- **Educational Demo**: Demonstrates AI concepts without external API dependencies
- **Query History**: Track previous AI interactions
- **Safety Warnings**: Clear disclaimers about educational nature

## Technologies Used

### Backend
- **Python 3.x**: Main programming language
- **Flask 3.0**: Web framework for Python
- **MySQL 8.0**: Relational database management system
- **MySQL Connector**: Python-MySQL database connector

### Frontend
- **HTML5**: Markup language for web pages
- **CSS3**: Styling and responsive design
- **JavaScript**: Client-side scripting
- **Bootstrap 5**: Responsive CSS framework
- **Font Awesome**: Icon library

### Security
- **Werkzeug**: Password hashing and security utilities
- **Flask Sessions**: Secure session management
- **SQL Injection Prevention**: Parameterized queries

## System Requirements

### Software Requirements
- Python 3.8 or higher
- MySQL 8.0 or higher
- Modern web browser (Chrome, Firefox, Edge, Safari)
- Text editor or IDE (VS Code, PyCharm, etc.)

### Hardware Requirements
- Minimum 4GB RAM
- 500MB free disk space
- Internet connection for CDN resources

## Database Design

### Database Schema
The system uses a normalized MySQL database named `doctor_ai_db` with the following tables:

#### 1. **users** Table
Stores authentication information for all user types.
```sql
- user_id (INT, PRIMARY KEY, AUTO_INCREMENT)
- name (VARCHAR(100), NOT NULL)
- email (VARCHAR(100), UNIQUE, NOT NULL)
- password_hash (VARCHAR(255), NOT NULL)
- role (ENUM: 'patient', 'doctor', 'admin', NOT NULL)
- phone (VARCHAR(20))
- created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
```

#### 2. **patients** Table
Stores patient-specific information.
```sql
- patient_id (INT, PRIMARY KEY, AUTO_INCREMENT)
- user_id (INT, UNIQUE, NOT NULL, FOREIGN KEY → users.user_id)
- date_of_birth (DATE)
- gender (ENUM: 'male', 'female', 'other')
- address (TEXT)
```

#### 3. **doctors** Table
Stores doctor professional information.
```sql
- doctor_id (INT, PRIMARY KEY, AUTO_INCREMENT)
- user_id (INT, UNIQUE, NOT NULL, FOREIGN KEY → users.user_id)
- specialization (VARCHAR(100), NOT NULL)
- qualification (VARCHAR(200))
- experience (INT)
- hospital (VARCHAR(100))
- location (VARCHAR(100))
- consultation_fee (DECIMAL(10,2))
- bio (TEXT)
- is_verified (BOOLEAN, DEFAULT FALSE)
```

#### 4. **doctor_availability** Table
Stores doctor availability schedule.
```sql
- availability_id (INT, PRIMARY KEY, AUTO_INCREMENT)
- doctor_id (INT, NOT NULL, FOREIGN KEY → doctors.doctor_id)
- day_of_week (ENUM: 'Monday' to 'Sunday', NOT NULL)
- start_time (TIME, NOT NULL)
- end_time (TIME, NOT NULL)
- is_available (BOOLEAN, DEFAULT TRUE)
```

#### 5. **appointments** Table
Stores appointment bookings.
```sql
- appointment_id (INT, PRIMARY KEY, AUTO_INCREMENT)
- patient_id (INT, NOT NULL, FOREIGN KEY → patients.patient_id)
- doctor_id (INT, NOT NULL, FOREIGN KEY → doctors.doctor_id)
- appointment_date (DATE, NOT NULL)
- appointment_time (TIME, NOT NULL)
- reason (TEXT)
- status (ENUM: 'pending', 'confirmed', 'completed', 'cancelled', DEFAULT 'pending')
- created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
- updated_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
```

#### 6. **medical_records** Table
Stores medical records for completed appointments.
```sql
- record_id (INT, PRIMARY KEY, AUTO_INCREMENT)
- patient_id (INT, NOT NULL, FOREIGN KEY → patients.patient_id)
- doctor_id (INT, NOT NULL, FOREIGN KEY → doctors.doctor_id)
- appointment_id (INT, UNIQUE, NOT NULL, FOREIGN KEY → appointments.appointment_id)
- diagnosis (TEXT)
- notes (TEXT)
- prescription (TEXT)
- created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
- updated_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP)
```

#### 7. **notifications** Table
Stores system notifications for users.
```sql
- notification_id (INT, PRIMARY KEY, AUTO_INCREMENT)
- user_id (INT, NOT NULL, FOREIGN KEY → users.user_id)
- message (TEXT, NOT NULL)
- is_read (BOOLEAN, DEFAULT FALSE)
- created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
```

#### 8. **ai_queries** Table
Stores AI assistant query history.
```sql
- query_id (INT, PRIMARY KEY, AUTO_INCREMENT)
- patient_id (INT, NOT NULL, FOREIGN KEY → patients.patient_id)
- symptoms (TEXT, NOT NULL)
- response (TEXT)
- suggested_specialization (VARCHAR(100))
- created_at (TIMESTAMP, DEFAULT CURRENT_TIMESTAMP)
```

### ER Diagram Description

**Entity Relationships:**

1. **Users to Patients**: One-to-One relationship
   - Each user with role 'patient' has exactly one patient record
   - FOREIGN KEY: patients.user_id → users.user_id

2. **Users to Doctors**: One-to-One relationship
   - Each user with role 'doctor' has exactly one doctor record
   - FOREIGN KEY: doctors.user_id → users.user_id

3. **Patients to Appointments**: One-to-Many relationship
   - One patient can have multiple appointments
   - FOREIGN KEY: appointments.patient_id → patients.patient_id

4. **Doctors to Appointments**: One-to-Many relationship
   - One doctor can have multiple appointments
   - FOREIGN KEY: appointments.doctor_id → doctors.doctor_id

5. **Doctors to Availability**: One-to-Many relationship
   - One doctor can have multiple availability slots
   - FOREIGN KEY: doctor_availability.doctor_id → doctors.doctor_id

6. **Appointments to Medical Records**: One-to-One relationship
   - Each appointment can have one medical record
   - FOREIGN KEY: medical_records.appointment_id → appointments.appointment_id

7. **Users to Notifications**: One-to-Many relationship
   - One user can receive multiple notifications
   - FOREIGN KEY: notifications.user_id → users.user_id

8. **Patients to AI Queries**: One-to-Many relationship
   - One patient can make multiple AI queries
   - FOREIGN KEY: ai_queries.patient_id → patients.patient_id

**Constraints:**
- PRIMARY KEY constraints on all ID fields
- UNIQUE constraints on email and relationship fields
- FOREIGN KEY constraints with CASCADE delete for data integrity
- CHECK constraints for data validation
- NOT NULL constraints on required fields
- DEFAULT values for timestamps and status fields

## Application Workflow

### Patient Workflow
1. Patient registers on the platform
2. Patient logs in to their dashboard
3. Patient searches for doctors by specialization/location
4. Patient views doctor profiles and availability
5. Patient books an appointment with preferred date/time
6. Appointment status is set to "pending"
7. Doctor receives notification and confirms appointment
8. Patient visits dashboard to track appointment status
9. After appointment, doctor adds medical records
10. Patient can view completed appointment details

### Doctor Workflow
1. Doctor registers with professional details
2. Admin verifies doctor account
3. Doctor sets availability schedule
4. Doctor receives appointment requests
5. Doctor accepts or rejects appointments
6. Doctor conducts appointments
7. Doctor adds medical records after completion
8. Doctor views patient history and statistics

### Admin Workflow
1. Admin logs in to dashboard
2. Admin views system statistics
3. Admin manages user accounts
4. Admin verifies doctor registrations
5. Admin views appointment overview
6. Admin accesses detailed reports

## Installation Instructions

### Prerequisites
1. Install Python 3.8 or higher from [python.org](https://www.python.org/)
2. Install MySQL 8.0 or higher from [mysql.com](https://www.mysql.com/)
3. Install a code editor (VS Code recommended)

### Step 1: Clone or Download the Project
```bash
  git clone https://github.com/kartikvadaliya29-ai/doctor-ai.git
  cd doctor-ai
```

### Step 2: Create MySQL Database
1. Open MySQL Command Line Client or MySQL Workbench
2. Login with your MySQL credentials
3. Execute the schema.sql file:
```bash
mysql -u root -p < doctor_ai/database/schema.sql
```

Or in MySQL Workbench:
- Open the schema.sql file
- Execute the entire script

### Step 3: Configure Database Connection
1. Open `doctor_ai/config.py`
2. Update the database configuration:
```python
DB_HOST = 'localhost'
DB_USER = 'root'  # Your MySQL username
DB_PASSWORD = ''  # Your MySQL password
DB_NAME = 'doctor_ai_db'
```

### Step 4: Install Python Dependencies
1. Open command prompt/terminal in the doctor_ai directory
2. Create a virtual environment (recommended):
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On Linux/Mac
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

### Step 5: Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## How to Create the MySQL Database

### Method 1: Using MySQL Command Line
```bash
# Login to MySQL
mysql -u root -p

# Execute the schema file
  source database/schema.sql

# Exit MySQL
exit
```

### Method 2: Using MySQL Workbench
1. Open MySQL Workbench
2. Connect to your MySQL server
3. Click File → Open SQL Script
4. Navigate to `doctor_ai/database/schema.sql`
5. Click the lightning bolt icon to execute
6. Verify the database was created successfully

### Method 3: Using phpMyAdmin
1. Open phpMyAdmin in your browser
2. Click on the "SQL" tab
3. Copy and paste the contents of schema.sql
4. Click "Go" to execute

## Sample Login Credentials

The schema.sql file includes sample data for testing:

### Patient Accounts
- **Email**: john.smith@email.com
- **Password**: any (for demo purposes)
- **Other patients**: sarah.j@email.com, michael.b@email.com, etc.

### Doctor Accounts
- **Email**: dr.martinez@email.com
- **Password**: any (for demo purposes)
- **Other doctors**: dr.rodriguez@email.com, dr.chen@email.com, etc.

### Admin Account
- **Email**: admin@doctorai.com
- **Password**: any (for demo purposes)

**Note**: In the current implementation, any password will work for the sample accounts. In a production environment, proper password hashing and validation should be implemented.

## Screenshots Section

*(Add screenshots of your application here during presentation)*

### Suggested Screenshots:
1. Landing page with hero section
2. Patient registration form
3. Patient dashboard with appointments
4. Doctor search and filter results
5. Doctor profile page
6. Appointment booking form
7. Doctor dashboard with statistics
8. Doctor appointment management
9. AI assistant interface
10. Admin dashboard with statistics

## Future Improvements

1. **Enhanced Security**
   - Implement email verification
   - Add two-factor authentication
   - Implement proper password validation
   - Add rate limiting for API endpoints

2. **Advanced Features**
   - Real-time notifications
   - Email/SMS appointment reminders
   - Video consultation integration
   - Payment gateway integration
   - Prescription download/print
   - File upload for medical documents

3. **AI Enhancement**
   - Integration with real AI/ML APIs
   - More sophisticated symptom analysis
   - Machine learning for doctor recommendations
   - Natural language processing for queries

4. **Mobile Application**
   - React Native or Flutter mobile app
   - Push notifications
   - Offline mode support

5. **Performance Optimization**
   - Database indexing optimization
   - Caching implementation
   - Load balancing
   - CDN integration

6. **Reporting & Analytics**
   - Advanced reporting dashboard
   - Export to PDF/Excel
   - Data visualization charts
   - Predictive analytics

## Important SQL Queries

### Find all appointments of a particular patient
```sql
SELECT a.*, d.specialization, u.name as doctor_name
FROM appointments a
JOIN doctors d ON a.doctor_id = d.doctor_id
JOIN users u ON d.user_id = u.user_id
WHERE a.patient_id = 1
ORDER BY a.appointment_date DESC;
```

### Find all appointments of a particular doctor
```sql
SELECT a.*, p.patient_id, u.name as patient_name
FROM appointments a
JOIN patients p ON a.patient_id = p.patient_id
JOIN users u ON p.user_id = u.user_id
WHERE a.doctor_id = 1
ORDER BY a.appointment_date DESC;
```

### Find available doctors by specialization
```sql
SELECT d.*, u.name, u.email
FROM doctors d
JOIN users u ON d.user_id = u.user_id
WHERE d.specialization = 'Cardiologist' AND d.is_verified = TRUE;
```

### Count appointments per doctor
```sql
SELECT d.doctor_id, u.name, COUNT(a.appointment_id) as total_appointments
FROM doctors d
JOIN users u ON d.user_id = u.user_id
LEFT JOIN appointments a ON d.doctor_id = a.doctor_id
GROUP BY d.doctor_id, u.name
ORDER BY total_appointments DESC;
```

### Show completed appointments
```sql
SELECT a.*, p.patient_id, d.doctor_id, up.name as patient_name, ud.name as doctor_name
FROM appointments a
JOIN patients p ON a.patient_id = p.patient_id
JOIN doctors d ON a.doctor_id = d.doctor_id
JOIN users up ON p.user_id = up.user_id
JOIN users ud ON d.user_id = ud.user_id
WHERE a.status = 'completed';
```

### Show upcoming appointments
```sql
SELECT a.*, p.patient_id, d.doctor_id, up.name as patient_name, ud.name as doctor_name
FROM appointments a
JOIN patients p ON a.patient_id = p.patient_id
JOIN doctors d ON a.doctor_id = d.doctor_id
JOIN users up ON p.user_id = up.user_id
JOIN users ud ON d.user_id = ud.user_id
WHERE a.status IN ('pending', 'confirmed') AND a.appointment_date >= CURDATE();
```

### Find the most requested doctor specializations
```sql
SELECT d.specialization, COUNT(a.appointment_id) as request_count
FROM doctors d
JOIN appointments a ON d.doctor_id = a.doctor_id
GROUP BY d.specialization
ORDER BY request_count DESC;
```

## Python Concepts Used

### Object-Oriented Programming
- Classes and objects in route modules
- Blueprint architecture for modular design
- Decorator patterns for authentication

### Web Development with Flask
- Flask application initialization
- Route handling with decorators
- Template rendering with Jinja2
- Form handling and validation
- Session management
- Flash messaging
- Error handling

### Database Programming
- MySQL connection management
- Parameterized queries for security
- Transaction management
- Cursor operations
- Error handling for database operations

### Security
- Password hashing with Werkzeug
- Session-based authentication
- SQL injection prevention
- Role-based access control
- Input validation

### Data Structures
- Dictionary operations for query results
- List comprehensions for data processing
- String manipulation and formatting

## DBMS Concepts Used

### Database Design
- Database normalization (3NF)
- Entity-Relationship modeling
- Table relationships and constraints
- Primary and foreign keys
- Indexing for performance

### SQL Operations
- **DDL (Data Definition Language)**
  - CREATE TABLE
  - ALTER TABLE
  - DROP TABLE

- **DML (Data Manipulation Language)**
  - INSERT
  - SELECT
  - UPDATE
  - DELETE

- **DQL (Data Query Language)**
  - Simple SELECT queries
  - Complex queries with JOINs
  - Subqueries
  - Aggregate functions

- **DCL (Data Control Language)**
  - GRANT (conceptual)
  - REVOKE (conceptual)

### Advanced SQL Concepts
- **JOINS**: INNER JOIN, LEFT JOIN
- **AGGREGATE FUNCTIONS**: COUNT, SUM, AVG, MAX, MIN
- **GROUP BY**: Data grouping and aggregation
- **ORDER BY**: Result sorting
- **WHERE**: Conditional filtering
- **HAVING**: Group-level filtering
- **UNIQUE CONSTRAINTS**: Data uniqueness
- **CHECK CONSTRAINTS**: Data validation
- **CASCADE DELETE**: Referential integrity
- **TRANSACTIONS**: ACID properties

### Database Relationships
- One-to-One relationships (users ↔ patients/doctors)
- One-to-Many relationships (patients/doctors ↔ appointments)
- Foreign key constraints
- Referential integrity

## Possible Viva Questions and Answers

### Python Programming Questions

**Q1: Why did you choose Flask over Django?**
A: Flask is more lightweight and flexible, making it ideal for learning and understanding web development concepts. It allows us to build components step-by-step and understand how everything works under the hood, which is perfect for educational purposes.

**Q2: How does session management work in your application?**
A: We use Flask's built-in session management, which stores session data in secure cookies on the client side. When a user logs in, we store their user_id, name, email, and role in the session. This data is sent with each request and used to authenticate the user and control access to different parts of the application.

**Q3: How do you handle password security?**
A: We use Werkzeug's password hashing functions to securely hash passwords before storing them in the database. We never store plain-text passwords. When a user logs in, we hash their input and compare it with the stored hash.

**Q4: What is the purpose of blueprints in Flask?**
A: Blueprints allow us to organize our application into modular components. We have separate blueprints for authentication, patient features, doctor features, admin features, and AI assistant. This makes the code more maintainable and easier to understand.

**Q5: How do you prevent SQL injection in your application?**
A: We use parameterized queries throughout the application. Instead of concatenating strings to build SQL queries, we use placeholders and pass parameters separately. The database driver handles proper escaping, preventing SQL injection attacks.

### Database Management Questions

**Q1: Explain the database normalization used in your project.**
A: Our database follows Third Normal Form (3NF). We've separated data into logical tables to eliminate redundancy and ensure data integrity. For example, user authentication data is in the users table, while role-specific data is in separate tables (patients, doctors). This avoids repeating user information and makes updates easier.

**Q2: What are the different types of relationships in your database?**
A: We have one-to-one relationships (users to patients/doctors), one-to-many relationships (patients to appointments, doctors to appointments), and the implicit many-to-many relationship through appointments (many patients can see many doctors over time).

**Q3: Why do you use foreign keys?**
A: Foreign keys enforce referential integrity between tables. They ensure that relationships between tables remain consistent. For example, a doctor_id in the appointments table must exist in the doctors table. Foreign keys also enable cascading deletes, which helps maintain data integrity when records are removed.

**Q4: Explain the purpose of indexes in your database.**
A: Indexes improve query performance by allowing the database to find rows more quickly. We've added indexes on frequently queried columns like email, role, patient_id, and doctor_id. This speeds up login operations, appointment lookups, and dashboard queries.

**Q5: What is a transaction and when is it used?**
A: A transaction is a sequence of database operations that are treated as a single unit of work. They follow ACID properties (Atomicity, Consistency, Isolation, Durability). We use transactions when we need to perform multiple related operations, like creating a user and their corresponding patient/doctor record, ensuring that either all operations succeed or none do.

**Q6: How do you handle the constraint that two patients can't book the same doctor at the same time?**
A: We have a UNIQUE constraint on the combination of doctor_id, appointment_date, and appointment_time in the appointments table. Before booking, we also check if the slot is already booked. This prevents double bookings at both the database and application level.

**Q7: Explain the difference between WHERE and HAVING clauses.**
A: WHERE filters individual rows before grouping, while HAVING filters groups after aggregation. For example, to find doctors with more than 5 appointments, we would use GROUP BY with HAVING. To find appointments on a specific date, we would use WHERE.

**Q8: What are aggregate functions and which ones did you use?**
A: Aggregate functions perform calculations on multiple rows and return a single value. We used COUNT() to count appointments, SUM() for totals, and can use AVG(), MAX(), MIN() for statistical analysis in our admin reports.

### System Design Questions

**Q1: How does the AI assistant work?**
A: The AI assistant uses a simple rule-based system. When a patient describes symptoms, we analyze the text for keywords related to different medical specializations. Based on matching keywords, we suggest appropriate doctor types. This is a demonstration of AI concepts without requiring external APIs.

**Q2: How do you handle role-based access control?**
A: We implement role-based access control using decorators. Each route module has a login_required decorator that checks if the user is logged in and has the appropriate role. Patients can't access doctor routes, doctors can't access admin routes, etc.

**Q3: What happens when a doctor deletes an availability slot?**
A: When a doctor deletes an availability slot, it's removed from the doctor_availability table. However, existing appointments booked during that time remain valid. The deletion only affects future booking availability.

**Q4: How do you ensure data consistency when a user is deleted?**
A: We use CASCADE DELETE on foreign key constraints. When a user is deleted, all related records (patient/doctor profile, appointments, medical records) are automatically deleted. This maintains referential integrity.

### General Questions

**Q1: What challenges did you face during development?**
A: Some challenges included designing a normalized database schema, implementing proper authentication and authorization, handling date/time operations across different time zones, and creating a responsive user interface that works well on different devices.

**Q2: How would you scale this application for real-world use?**
A: For real-world scaling, I would implement caching, add database connection pooling, use a production-grade web server like Gunicorn, implement proper error logging and monitoring, add comprehensive input validation, and consider microservices architecture for different components.

**Q3: What security measures would you add for production?**
A: For production, I would implement HTTPS, add CSRF protection, implement rate limiting, add comprehensive input validation and sanitization, use environment variables for sensitive configuration, implement proper password policies, add security headers, and regular security audits.

**Q4: How would you improve the AI assistant?**
A: I would integrate with real AI/ML APIs, implement machine learning models trained on medical data, add natural language processing for better symptom understanding, include medical knowledge bases, and add features like drug interaction checking and symptom triage.

## Project Structure

```
doctor_ai/
│
├── app.py                          # Main Flask application
├── config.py                       # Application configuration
├── database.py                     # Database connection handler
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
│
├── routes/                         # Route modules
│   ├── __init__.py
│   ├── auth.py                     # Authentication routes
│   ├── patient.py                  # Patient routes
│   ├── doctor.py                   # Doctor routes
│   ├── admin.py                    # Admin routes
│   └── ai.py                       # AI assistant routes
│
├── templates/                      # HTML templates
│   ├── base.html                   # Base template
│   ├── index.html                  # Landing page
│   ├── about.html                  # About page
│   ├── login.html                  # Login page
│   ├── register.html               # Registration page
│   ├── profile.html                # User profile
│   ├── patient_dashboard.html      # Patient dashboard
│   ├── doctors.html                # Doctor search
│   ├── doctor_profile.html         # Doctor profile
│   ├── book_appointment.html       # Appointment booking
│   ├── appointments.html           # Patient appointments
│   ├── reschedule_appointment.html # Appointment rescheduling
│   ├── doctor_dashboard.html       # Doctor dashboard
│   ├── doctor_appointments.html    # Doctor appointments
│   ├── complete_appointment.html  # Complete appointment
│   ├── doctor_availability.html   # Doctor availability
│   ├── doctor_patients.html        # Doctor patients
│   ├── doctor_profile.html         # Doctor profile edit
│   ├── admin_dashboard.html        # Admin dashboard
│   ├── admin_patients.html         # Admin patient management
│   ├── admin_doctors.html          # Admin doctor management
│   ├── admin_appointments.html     # Admin appointments
│   ├── admin_statistics.html       # Admin statistics
│   ├── ai_assistant.html           # AI assistant
│   ├── ai_result.html              # AI results
│   ├── ai_history.html             # AI query history
│   ├── 404.html                    # 404 error page
│   └── 500.html                    # 500 error page
│
├── static/                         # Static files
│   ├── css/
│   │   └── style.css              # Custom CSS
│   ├── js/
│   │   └── script.js              # Custom JavaScript
│   └── images/                     # Image files
│
└── database/                       # Database files
    └── schema.sql                  # Database schema and sample data
```

## Conclusion

Doctor AI is a comprehensive hospital appointment management system that demonstrates practical application of Python programming, web development, and database management concepts. The project provides a solid foundation for understanding modern web application development and can be extended with additional features for real-world deployment.

The project successfully demonstrates:
- Object-oriented programming with Python
- Web development with Flask framework
- Database design and management with MySQL
- Implementation of CRUD operations
- Understanding of database relationships and normalization
- Security best practices
- Responsive web design
- AI concepts and implementation

This project serves as an excellent educational tool for learning web development and database management concepts, and can be used as a foundation for more advanced healthcare applications.

---

**Developer Note**: This project was developed for educational purposes. The AI assistant feature uses simple rule-based logic and should NOT be used for actual medical diagnosis or treatment. Always consult qualified healthcare professionals for medical advice.

**Project Version**: 1.0
**Last Updated**: September 2026

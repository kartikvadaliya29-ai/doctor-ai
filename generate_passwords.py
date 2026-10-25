"""
Utility script to generate password hashes for sample data
Run this script to generate proper password hashes
"""

from werkzeug.security import generate_password_hash

# Generate hash for default password 'password123'
password = 'password123'
password_hash = generate_password_hash(password)

print(f"Password: {password}")
print(f"Hash: {password_hash}")
print("\nCopy this hash and update the schema.sql file")

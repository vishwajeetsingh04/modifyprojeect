"""
Script to recreate the database with the updated schema.
This will delete the existing database and create a new one with all tables.
WARNING: This will delete all existing data!
"""
import os
from app import app, db
from database_models import User, InterviewSession, PerformanceMetrics, QuestionBank, ResumeData

def recreate_database():
    """Recreate the database with updated schema"""
    with app.app_context():
        # Delete existing database file
        db_file = 'instance/interview_system.db'
        if os.path.exists(db_file):
            print(f"Deleting existing database: {db_file}")
            os.remove(db_file)
        
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        print("Database recreated successfully!")
        print("You can now start the server with: python app.py")

if __name__ == '__main__':
    response = input("This will delete all existing data. Continue? (yes/no): ")
    if response.lower() == 'yes':
        recreate_database()
    else:
        print("Cancelled.")


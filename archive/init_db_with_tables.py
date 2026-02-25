#!/usr/bin/env python3
"""
Database initialization with proper model imports
"""
import sys
sys.path.append('backend')

# Import all models to register them with SQLModel
from app.models.employee import Employee
from app.models.absence import Absence
from app.models.absence_type import AbsenceType
from app.models.vacation_allowance import VacationAllowance
from app.models.federal_state import FederalState
from app.models.holiday import Holiday

# Import any additional models
try:
    from app.models.school_holiday_notification import SchoolHolidayNotification
    from app.models.employee_school_holiday_preferences import EmployeeSchoolHolidayPreferences
    print("School holiday models imported successfully")
except ImportError as e:
    print(f"School holiday models not available: {e}")

from app.core.database import create_db_and_tables
import sqlite3
from pathlib import Path

def main():
    print("=== Creating Database with All Tables ===")
    
    # Create database and tables
    create_db_and_tables()
    print("Database and tables created!")
    
    # Check tables
    db_path = Path("data/gynorg.db")
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables created: {[table[0] for table in tables]}")
        conn.close()
    else:
        print("Database file not found!")

if __name__ == "__main__":
    main()

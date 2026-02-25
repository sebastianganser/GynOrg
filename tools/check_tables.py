from sqlmodel import create_engine, inspect, SQLModel
from app.core.config import settings
from app.models import * # Import all models to register them
# Import explicitly to be sure
from app.models.employee_school_holiday_preferences import EmployeeSchoolHolidayPreferences

# Assuming sqlite for this environment as seen in file list 'gynorg.db'
sqlite_url = "sqlite:///./gynorg.db"
engine = create_engine(sqlite_url)

def check_tables():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables in database:")
    for table in tables:
        print(f" - {table}")
    
    if "employee_school_holiday_preferences" in tables:
        print("\n✅ Table 'employee_school_holiday_preferences' exists.")
    else:
        print("\n❌ Table 'employee_school_holiday_preferences' DOES NOT exist.")

if __name__ == "__main__":
    check_tables()

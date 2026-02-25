import argparse
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def check_vacation_data(employee_id=None):
    """
    Check vacation allowance and entitlement data directly via SQL/Engine
    similar to how the old SQLite script did it, but using SQLAlchemy for Postgres.
    """
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    print(f"Connecting to database: {settings.DATABASE_URL}")
    print("-" * 50)
    
    try:
        # Check employees
        employees = session.execute(text("SELECT id, first_name, last_name FROM employees")).fetchall()
        if not employees:
            print("No employees found.")
            return
            
        print(f"Found {len(employees)} employees.")
        
        # Check specific employee or all
        for emp in employees:
            if employee_id and str(emp.id) != str(employee_id):
                continue
                
            print(f"\nEmployee: {emp.first_name} {emp.last_name} (ID: {emp.id})")
            
            # Allowances
            print("  Allowances (Urlaubsanspruch):")
            allowances = session.execute(
                text("SELECT id, year, base_allowance, total_allowance, remaining_allowance FROM vacation_allowances WHERE employee_id = :emp_id ORDER BY year DESC"),
                {"emp_id": emp.id}
            ).fetchall()
            
            if allowances:
                for a in allowances:
                    print(f"    - Year: {a.year} | Base: {a.base_allowance} | Total: {a.total_allowance} | Remaining: {a.remaining_allowance}")
            else:
                print("    - None found")
                
            # Entitlements
            print("  Entitlements (Tatsächlicher Anspruch/Berechnung):")
            entitlements = session.execute(
                text("SELECT id, year, entitlement_type, days FROM vacation_entitlements WHERE employee_id = :emp_id ORDER BY year DESC"),
                {"emp_id": emp.id}
            ).fetchall()
            
            if entitlements:
                for e in entitlements:
                    print(f"    - Year: {e.year} | Type: {e.entitlement_type} | Days: {e.days}")
            else:
                print("    - None found")
                
            # Absences (Vacation only)
            print("  Vacation Taken (Urlaubsabwesenheiten):")
            absences = session.execute(
                text("""
                    SELECT a.start_date, a.end_date, a.status 
                    FROM absences a
                    JOIN absence_types t ON a.absence_type_id = t.id
                    WHERE a.employee_id = :emp_id AND t.category = 'VACATION'
                    ORDER BY a.start_date DESC
                """),
                {"emp_id": emp.id}
            ).fetchall()
            
            if absences:
                for ab in absences:
                    print(f"    - From: {ab.start_date} To: {ab.end_date} | Status: {ab.status}")
            else:
                print("    - None found")
                
    except Exception as e:
        print(f"Error executing queries: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check vacation data in PostgreSQL database")
    parser.add_argument("--employee", type=int, help="Optional: Filter by employee ID")
    args = parser.parse_args()
    
    check_vacation_data(employee_id=args.employee)

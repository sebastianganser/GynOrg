import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

try:
    print("Testing imports...")
    from app.core.config import settings
    from app.models.employee import Employee
    from app.models.federal_state import FederalState
    from sqlmodel import Session, select
    print(f"DEBUG: FederalState members: {list(FederalState.__members__.keys())}")
    print(f"DEBUG: FederalState ST value: {FederalState.SACHSEN_ANHALT.value}")
    print(f"DEBUG: 'ST' in allowed values? {'ST' in [e.value for e in FederalState]}")
    print(f"DEBUG: DATABASE_URL = {settings.DATABASE_URL}")
    print("✅ Imports successful.")

    # Override engine for testing ensure we use the correct DB
    from sqlmodel import create_engine
    actual_db_path = "backend/app.db"
    if not os.path.exists(actual_db_path):
        # Maybe absolute path
        actual_db_path = os.path.join(os.getcwd(), "backend", "app.db")
    
    print(f"DEBUG: Using actual DB at {actual_db_path}")
    test_engine = create_engine(f"sqlite:///{actual_db_path}")

    print("Testing database access...")
    # Inspect raw values first
    with test_engine.connect() as conn:
        from sqlalchemy import text
        # Check constraints
        schema = conn.execute(text("SELECT sql FROM sqlite_master WHERE name='employees'")).fetchone()
        print(f"DEBUG: Schema: {schema[0]}")
        
        result = conn.execute(text("SELECT id, federal_state FROM employees LIMIT 5"))
        for row in result:
            print(f"DEBUG: Raw DB Row: {row}")
            val = row[1]
            print(f"DEBUG: Value: '{val}', Type: {type(val)}")
            if isinstance(val, str):
                print(f"DEBUG: 'ST' == val? {'ST' == val}")
                try:
                    fs = FederalState(val)
                    print(f"DEBUG: Converted to Enum: {fs}")
                except Exception as e:
                    print(f"DEBUG: Conversion failed: {e}")

    with Session(test_engine) as session:
        statement = select(Employee).limit(1)
        results = session.exec(statement).all()
        print(f"✅ Database query successful. Found {len(results)} employees (limit 1).")
        
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Runtime Error: {e}")
    sys.exit(1)

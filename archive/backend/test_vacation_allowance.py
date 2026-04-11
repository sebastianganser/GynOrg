import pytest
from datetime import datetime
from sqlmodel import Session, select, create_engine
from app.models import Employee, VacationAllowance, FederalState
from app.schemas.vacation_allowance import VacationAllowanceCreate, VacationAllowanceUpdate
from app.core.database import create_db_and_tables


# Test-Engine für isolierte Tests
test_engine = create_engine("sqlite:///:memory:", echo=False)


@pytest.fixture
def session():
    """Test-Session mit frischer In-Memory-Datenbank"""
    # Tabellen erstellen
    from app.models import Employee, VacationAllowance
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(test_engine)
    
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def sample_employee(session):
    """Erstellt einen Test-Mitarbeiter"""
    employee = Employee(
        first_name="Max",
        last_name="Mustermann",
        email="max.mustermann@test.de",
        federal_state=FederalState.NW
    )
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee


def test_vacation_allowance_creation():
    """Test VacationAllowance Model Erstellung"""
    vacation = VacationAllowance(
        employee_id=1,
        year=2024,
        annual_allowance=30,
        carryover_days=5
    )
    
    assert vacation.year == 2024
    assert vacation.annual_allowance == 30
    assert vacation.carryover_days == 5
    assert vacation.total_allowance == 35
    assert vacation.employee_id == 1


def test_vacation_allowance_base_creation():
    """Test VacationAllowanceBase Model"""
    vacation_base = VacationAllowanceCreate(
        employee_id=1,
        year=2024,
        annual_allowance=25,
        carryover_days=3
    )
    
    assert vacation_base.year == 2024
    assert vacation_base.annual_allowance == 25
    assert vacation_base.carryover_days == 3
    assert vacation_base.employee_id == 1
    # total_allowance is only available in VacationAllowanceRead, not Create


def test_vacation_allowance_default_values():
    """Test Standard-Werte"""
    vacation = VacationAllowance(
        employee_id=1,
        year=2024,
        annual_allowance=30
        # carryover_days sollte default 0 sein
    )
    
    assert vacation.carryover_days == 0
    assert vacation.total_allowance == 30


def test_vacation_allowance_year_validation():
    """Test Jahr-Validierung"""
    from pydantic_core import ValidationError
    
    # Jahr zu niedrig (Schema erlaubt 2020-2050)
    with pytest.raises(ValidationError):
        VacationAllowanceCreate.model_validate({
            "employee_id": 1, 
            "year": 2019, 
            "annual_allowance": 30
        })
    
    # Jahr zu hoch (Schema erlaubt 2020-2050)
    with pytest.raises(ValidationError):
        VacationAllowanceCreate.model_validate({
            "employee_id": 1, 
            "year": 2051, 
            "annual_allowance": 30
        })
    
    # Gültige Jahre
    vacation_2020 = VacationAllowanceCreate.model_validate({
        "employee_id": 1, 
        "year": 2020, 
        "annual_allowance": 30
    })
    vacation_2050 = VacationAllowanceCreate.model_validate({
        "employee_id": 1, 
        "year": 2050, 
        "annual_allowance": 30
    })
    assert vacation_2020.year == 2020
    assert vacation_2050.year == 2050


def test_vacation_allowance_annual_allowance_validation():
    """Test Jahresurlaubsanspruch-Validierung"""
    from pydantic_core import ValidationError
    
    # Negative Urlaubstage (Schema erlaubt 0-365)
    with pytest.raises(ValidationError):
        VacationAllowanceCreate.model_validate({
            "employee_id": 1, 
            "year": 2024, 
            "annual_allowance": -5
        })
    
    # Zu viele Urlaubstage (Schema erlaubt 0-365)
    with pytest.raises(ValidationError):
        VacationAllowanceCreate.model_validate({
            "employee_id": 1, 
            "year": 2024, 
            "annual_allowance": 366
        })
    
    # Gültige Werte
    vacation_0 = VacationAllowanceCreate.model_validate({
        "employee_id": 1, 
        "year": 2024, 
        "annual_allowance": 0
    })
    vacation_365 = VacationAllowanceCreate.model_validate({
        "employee_id": 1, 
        "year": 2024, 
        "annual_allowance": 365
    })
    assert vacation_0.annual_allowance == 0
    assert vacation_365.annual_allowance == 365


def test_vacation_allowance_carryover_validation():
    """Test Übertragstage-Validierung"""
    from pydantic_core import ValidationError
    
    # Negative Übertragstage (Schema erlaubt 0-365)
    with pytest.raises(ValidationError):
        VacationAllowanceCreate.model_validate({
            "employee_id": 1, 
            "year": 2024, 
            "annual_allowance": 30, 
            "carryover_days": -2
        })
    
    # Zu viele Übertragstage (Schema erlaubt 0-365)
    with pytest.raises(ValidationError):
        VacationAllowanceCreate.model_validate({
            "employee_id": 1, 
            "year": 2024, 
            "annual_allowance": 30, 
            "carryover_days": 366
        })
    
    # Gültige Werte
    vacation_0 = VacationAllowanceCreate.model_validate({
        "employee_id": 1, 
        "year": 2024, 
        "annual_allowance": 30, 
        "carryover_days": 0
    })
    vacation_365 = VacationAllowanceCreate.model_validate({
        "employee_id": 1, 
        "year": 2024, 
        "annual_allowance": 30, 
        "carryover_days": 365
    })
    assert vacation_0.carryover_days == 0
    assert vacation_365.carryover_days == 365


def test_vacation_allowance_update_validation():
    """Test VacationAllowanceUpdate Validierungen"""
    from pydantic_core import ValidationError
    
    # Jahr-Validierung (Schema erlaubt 2020-2050)
    with pytest.raises(ValidationError):
        VacationAllowanceUpdate.model_validate({"year": 2019})
    
    with pytest.raises(ValidationError):
        VacationAllowanceUpdate.model_validate({"year": 2051})
    
    # Jahresurlaubsanspruch-Validierung (Schema erlaubt 0-365)
    with pytest.raises(ValidationError):
        VacationAllowanceUpdate.model_validate({"annual_allowance": -1})
    
    with pytest.raises(ValidationError):
        VacationAllowanceUpdate.model_validate({"annual_allowance": 366})
    
    # Übertragstage-Validierung (Schema erlaubt 0-365)
    with pytest.raises(ValidationError):
        VacationAllowanceUpdate.model_validate({"carryover_days": -1})
    
    with pytest.raises(ValidationError):
        VacationAllowanceUpdate.model_validate({"carryover_days": 366})
    
    # Gültige Updates
    update = VacationAllowanceUpdate.model_validate({
        "year": 2024, 
        "annual_allowance": 28, 
        "carryover_days": 5
    })
    assert update.year == 2024
    assert update.annual_allowance == 28
    assert update.carryover_days == 5


def test_vacation_allowance_total_allowance_property():
    """Test total_allowance Property"""
    vacation1 = VacationAllowance(employee_id=1, year=2024, annual_allowance=30, carryover_days=0)
    assert vacation1.total_allowance == 30
    
    vacation2 = VacationAllowance(employee_id=1, year=2024, annual_allowance=25, carryover_days=5)
    assert vacation2.total_allowance == 30
    
    vacation3 = VacationAllowance(employee_id=1, year=2024, annual_allowance=20, carryover_days=15)
    assert vacation3.total_allowance == 35


def test_vacation_allowance_database_integration(session, sample_employee):
    """Test Datenbank-Integration mit Employee"""
    # VacationAllowance erstellen
    vacation = VacationAllowance(
        employee_id=sample_employee.id,
        year=2024,
        annual_allowance=30,
        carryover_days=5
    )
    session.add(vacation)
    session.commit()
    session.refresh(vacation)
    
    # Prüfe dass VacationAllowance gespeichert wurde
    assert vacation.id is not None
    assert vacation.employee_id == sample_employee.id
    assert vacation.created_at is not None
    assert vacation.updated_at is not None
    
    # Prüfe Relationship von Employee zu VacationAllowance
    session.refresh(sample_employee)
    assert len(sample_employee.vacation_allowances) == 1
    assert sample_employee.vacation_allowances[0].id == vacation.id
    assert sample_employee.vacation_allowances[0].total_allowance == 35


def test_vacation_allowance_multiple_years(session, sample_employee):
    """Test mehrere VacationAllowances für verschiedene Jahre"""
    # Erstelle VacationAllowances für 2023 und 2024
    vacation_2023 = VacationAllowance(
        employee_id=sample_employee.id,
        year=2023,
        annual_allowance=28,
        carryover_days=2
    )
    vacation_2024 = VacationAllowance(
        employee_id=sample_employee.id,
        year=2024,
        annual_allowance=30,
        carryover_days=5
    )
    
    session.add(vacation_2023)
    session.add(vacation_2024)
    session.commit()
    
    # Prüfe dass beide gespeichert wurden
    session.refresh(sample_employee)
    assert len(sample_employee.vacation_allowances) == 2
    
    # Prüfe Jahre
    years = [va.year for va in sample_employee.vacation_allowances]
    assert 2023 in years
    assert 2024 in years


def test_vacation_allowance_query_by_year(session, sample_employee):
    """Test Abfrage nach Jahr"""
    # Erstelle VacationAllowances für verschiedene Jahre
    vacation_2023 = VacationAllowance(
        employee_id=sample_employee.id,
        year=2023,
        annual_allowance=28
    )
    vacation_2024 = VacationAllowance(
        employee_id=sample_employee.id,
        year=2024,
        annual_allowance=30
    )
    
    session.add(vacation_2023)
    session.add(vacation_2024)
    session.commit()
    
    # Abfrage für 2024
    vacation_2024_query = session.exec(
        select(VacationAllowance).where(
            VacationAllowance.employee_id == sample_employee.id,
            VacationAllowance.year == 2024
        )
    ).first()
    
    assert vacation_2024_query is not None
    assert vacation_2024_query.year == 2024
    assert vacation_2024_query.annual_allowance == 30


def test_vacation_allowance_relationship_back_populates(session, sample_employee):
    """Test bidirektionale Relationship"""
    vacation = VacationAllowance(
        employee_id=sample_employee.id,
        year=2024,
        annual_allowance=30,
        carryover_days=5
    )
    session.add(vacation)
    session.commit()
    session.refresh(vacation)
    
    # Prüfe Relationship von VacationAllowance zu Employee
    assert vacation.employee is not None
    assert vacation.employee.id == sample_employee.id
    assert vacation.employee.first_name == "Max"
    assert vacation.employee.last_name == "Mustermann"

"""Tests für die calendar_color Funktionalität im Employee Model"""

import pytest
from app.models.employee import Employee, EmployeeCreate, EmployeeUpdate
from app.core.colors import get_next_color, validate_hex_color, get_color_name, DEFAULT_CALENDAR_COLORS


def test_employee_has_default_calendar_color():
    """Test dass neue Mitarbeiter eine Standard-Farbe erhalten"""
    employee = EmployeeCreate(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        federal_state="Berlin"
    )
    # calendar_color sollte den Standardwert haben
    assert employee.calendar_color == "#3B82F6"


def test_employee_custom_calendar_color():
    """Test dass benutzerdefinierte Farben gesetzt werden können"""
    employee = EmployeeCreate(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        federal_state="Berlin",
        calendar_color="#FF5733"
    )
    assert employee.calendar_color == "#FF5733"


def test_calendar_color_validation_valid():
    """Test dass gültige Hex-Farben akzeptiert werden"""
    valid_colors = ["#FF5733", "#3B82F6", "#10B981", "#FFFFFF", "#000000"]
    
    for i, color in enumerate(valid_colors):
        employee = EmployeeCreate(
            first_name="Test",
            last_name="User",
            email=f"test{i}@example.com",
            federal_state="Berlin",
            calendar_color=color
        )
        assert employee.calendar_color == color


def test_calendar_color_validation_invalid():
    """Test dass ungültige Farben einen Fehler werfen"""
    from pydantic import ValidationError
    
    invalid_colors = [
        "red",           # Kein Hex
        "#FF57",         # Zu kurz
        "FF5733",        # Fehlendes #
        "#GG5733",       # Ungültige Hex-Zeichen
    ]
    
    for i, color in enumerate(invalid_colors):
        with pytest.raises((ValueError, ValidationError)):
            EmployeeCreate(
                first_name="Test",
                last_name="User",
                email=f"test{i}@example.com",
                federal_state="Berlin",
                calendar_color=color
            )


def test_employee_update_calendar_color():
    """Test dass calendar_color über EmployeeUpdate geändert werden kann"""
    update = EmployeeUpdate(calendar_color="#10B981")
    assert update.calendar_color == "#10B981"


def test_employee_update_calendar_color_validation():
    """Test dass EmployeeUpdate auch Farben validiert"""
    with pytest.raises(ValueError, match="Kalenderfarbe muss im Hex-Format sein"):
        EmployeeUpdate(calendar_color="invalid")


def test_get_next_color_empty_list():
    """Test dass die erste Farbe zurückgegeben wird bei leerer Liste"""
    next_color = get_next_color([])
    assert next_color == DEFAULT_CALENDAR_COLORS[0]


def test_get_next_color_with_existing():
    """Test der Farbauswahl-Logik mit bestehenden Farben"""
    existing = ["#3B82F6", "#10B981"]
    next_color = get_next_color(existing)
    assert next_color == "#F59E0B"  # Dritte Farbe in der Palette


def test_get_next_color_all_used():
    """Test dass die Palette wiederholt wird wenn alle Farben verwendet wurden"""
    # Verwende alle Farben
    existing = DEFAULT_CALENDAR_COLORS.copy()
    next_color = get_next_color(existing)
    # Sollte die erste Farbe wieder zurückgeben
    assert next_color == DEFAULT_CALENDAR_COLORS[0]


def test_get_next_color_cycle():
    """Test dass die Palette zyklisch durchlaufen wird"""
    # Verwende mehr Farben als in der Palette
    existing = DEFAULT_CALENDAR_COLORS + ["#AAAAAA", "#BBBBBB"]
    next_color = get_next_color(existing)
    # Sollte die dritte Farbe zurückgeben (Index 2)
    assert next_color == DEFAULT_CALENDAR_COLORS[2]


def test_validate_hex_color_valid():
    """Test der Hex-Farb-Validierung mit gültigen Farben"""
    assert validate_hex_color("#3B82F6") is True
    assert validate_hex_color("#FFFFFF") is True
    assert validate_hex_color("#000000") is True
    assert validate_hex_color("#abc123") is True


def test_validate_hex_color_invalid():
    """Test der Hex-Farb-Validierung mit ungültigen Farben"""
    assert validate_hex_color("red") is False
    assert validate_hex_color("#FF57") is False
    assert validate_hex_color("FF5733") is False
    assert validate_hex_color("#GG5733") is False


def test_get_color_name_known():
    """Test dass bekannte Farben einen Namen erhalten"""
    assert get_color_name("#3B82F6") == "Blau"
    assert get_color_name("#10B981") == "Grün"
    assert get_color_name("#EF4444") == "Rot"


def test_get_color_name_unknown():
    """Test dass unbekannte Farben als 'Benutzerdefiniert' markiert werden"""
    assert get_color_name("#AABBCC") == "Benutzerdefiniert"
    assert get_color_name("#123456") == "Benutzerdefiniert"


def test_get_color_name_case_insensitive():
    """Test dass Farbnamen case-insensitive sind"""
    assert get_color_name("#3b82f6") == "Blau"
    assert get_color_name("#3B82F6") == "Blau"
    assert get_color_name("#3B82f6") == "Blau"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

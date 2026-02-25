"""Standard-Farbpalette für Mitarbeiter-Kalender

Dieses Modul definiert eine Palette von Farben für die Kalenderansicht
und stellt Hilfsfunktionen zur Farbauswahl bereit.
"""

from typing import List

# Standard-Farbpalette für Mitarbeiter-Kalender
# Farben sind so gewählt, dass sie gut unterscheidbar und zugänglich sind
DEFAULT_CALENDAR_COLORS = [
    "#3B82F6",  # Blau (Blue-500)
    "#10B981",  # Grün (Emerald-500)
    "#F59E0B",  # Amber (Amber-500)
    "#EF4444",  # Rot (Red-500)
    "#8B5CF6",  # Lila (Violet-500)
    "#EC4899",  # Pink (Pink-500)
    "#14B8A6",  # Türkis (Teal-500)
    "#F97316",  # Orange (Orange-500)
    "#6366F1",  # Indigo (Indigo-500)
    "#84CC16",  # Lime (Lime-500)
    "#06B6D4",  # Cyan (Cyan-500)
    "#F43F5E",  # Rose (Rose-500)
]


def get_next_color(existing_colors: List[str]) -> str:
    """Gibt die nächste verfügbare Farbe aus der Palette zurück.
    
    Args:
        existing_colors: Liste der bereits verwendeten Farben
        
    Returns:
        Die nächste verfügbare Farbe im Hex-Format
        
    Example:
        >>> existing = ["#3B82F6", "#10B981"]
        >>> get_next_color(existing)
        '#F59E0B'
    """
    # Finde die erste Farbe, die noch nicht verwendet wird
    for color in DEFAULT_CALENDAR_COLORS:
        if color not in existing_colors:
            return color
    
    # Wenn alle Farben verwendet wurden, wiederhole die Palette
    # Verwende Modulo, um zyklisch durch die Palette zu gehen
    index = len(existing_colors) % len(DEFAULT_CALENDAR_COLORS)
    return DEFAULT_CALENDAR_COLORS[index]


def validate_hex_color(color: str) -> bool:
    """Validiert, ob ein String eine gültige Hex-Farbe ist.
    
    Args:
        color: Zu validierende Farbe
        
    Returns:
        True wenn gültig, False sonst
        
    Example:
        >>> validate_hex_color("#3B82F6")
        True
        >>> validate_hex_color("blue")
        False
    """
    import re
    return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))


def get_color_name(hex_color: str) -> str:
    """Gibt einen lesbaren Namen für eine Hex-Farbe zurück.
    
    Args:
        hex_color: Farbe im Hex-Format
        
    Returns:
        Lesbarer Farbname oder "Benutzerdefiniert"
    """
    color_names = {
        "#3B82F6": "Blau",
        "#10B981": "Grün",
        "#F59E0B": "Amber",
        "#EF4444": "Rot",
        "#8B5CF6": "Lila",
        "#EC4899": "Pink",
        "#14B8A6": "Türkis",
        "#F97316": "Orange",
        "#6366F1": "Indigo",
        "#84CC16": "Lime",
        "#06B6D4": "Cyan",
        "#F43F5E": "Rose",
    }
    return color_names.get(hex_color.upper(), "Benutzerdefiniert")

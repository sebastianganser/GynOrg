from enum import Enum
from typing import Dict


class FederalState(str, Enum):
    """Deutsche Bundesländer mit Kürzeln als Values für API-Kompatibilität"""
    
    # Bundesländer mit offiziellen Kürzeln als Values
    BADEN_WUERTTEMBERG = "BW"
    BAYERN = "BY"
    BERLIN = "BE"
    BRANDENBURG = "BB"
    BREMEN = "HB"
    HAMBURG = "HH"
    HESSEN = "HE"
    MECKLENBURG_VORPOMMERN = "MV"
    NIEDERSACHSEN = "NI"
    NORDRHEIN_WESTFALEN = "NW"
    RHEINLAND_PFALZ = "RP"
    SAARLAND = "SL"
    SACHSEN = "SN"
    SACHSEN_ANHALT = "ST"
    SCHLESWIG_HOLSTEIN = "SH"
    THUERINGEN = "TH"

# Mapping für Vollnamen
FEDERAL_STATE_FULL_NAMES = {
    "BW": "Baden-Württemberg",
    "BY": "Bayern",
    "BE": "Berlin",
    "BB": "Brandenburg",
    "HB": "Bremen",
    "HH": "Hamburg",
    "HE": "Hessen",
    "MV": "Mecklenburg-Vorpommern",
    "NI": "Niedersachsen",
    "NW": "Nordrhein-Westfalen",
    "RP": "Rheinland-Pfalz",
    "SL": "Saarland",
    "SN": "Sachsen",
    "ST": "Sachsen-Anhalt",
    "SH": "Schleswig-Holstein",
    "TH": "Thüringen"
}

class FederalStateHelpers:
    @staticmethod
    def get_choices() -> Dict[str, str]:
        """Gibt alle Bundesländer als Dict zurück (Kürzel: Vollname)"""
        return {state.value: FEDERAL_STATE_FULL_NAMES[state.value] for state in FederalState}
    
    @staticmethod
    def get_display_name(code: str) -> str:
        """Gibt den Vollnamen für ein Kürzel zurück"""
        return FEDERAL_STATE_FULL_NAMES.get(code, code)
    
    @staticmethod
    def get_all_states() -> list:
        """Gibt alle Bundesländer als Liste zurück für API-Endpoints"""
        return [
            {"code": state.value, "name": FEDERAL_STATE_FULL_NAMES[state.value]} 
            for state in FederalState
        ]

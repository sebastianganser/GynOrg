#!/usr/bin/env python3
"""
Performance Test Configuration
Zentrale Konfiguration für alle Performance-Tests
"""

import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class APIConfig:
    """API-Konfiguration"""
    base_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    auth_username: str = os.environ.get("ADMIN_USERNAME", "admin")
    auth_password: str = os.environ.get("ADMIN_PASSWORD", "admin")
    timeout: int = 30

@dataclass
class LoadTestConfig:
    """Load Test Konfiguration"""
    # User-Zahlen für verschiedene Test-Szenarien
    baseline_users: int = 1
    light_load_users: int = 5
    medium_load_users: int = 10
    heavy_load_users: int = 25
    peak_load_users: int = 50
    
    # Test-Dauern (in Sekunden)
    baseline_duration: int = 120  # 2 Min
    light_load_duration: int = 300  # 5 Min
    medium_load_duration: int = 300  # 5 Min
    heavy_load_duration: int = 300  # 5 Min
    peak_load_duration: int = 180  # 3 Min
    test_duration: int = 180  # Alias für peak_load_duration für Kompatibilität
    
    # Spawn-Rate (Users pro Sekunde)
    spawn_rate: int = 2
    
    # Wait-Time zwischen Requests (Sekunden)
    min_wait: int = 1
    max_wait: int = 3

@dataclass
class PerformanceTargets:
    """Performance-Ziele und Erfolgs-Kriterien"""
    # API Response Times (Millisekunden)
    api_response_time_95th: int = 200
    api_response_time_avg: int = 100
    api_response_time_max: int = 1000
    
    # Error Rates (Prozent)
    max_error_rate: float = 1.0
    
    # Frontend Performance (Core Web Vitals) - Desktop-optimiert
    lcp_target: float = 2.0  # Largest Contentful Paint (Sekunden) - schärfer für Desktop
    fid_target: float = 0.05  # First Input Delay (Sekunden) - schärfer für Desktop
    cls_target: float = 0.05  # Cumulative Layout Shift - schärfer für Desktop
    
    # Bundle Size (KB) - Desktop kann mehr handhaben
    max_bundle_size: int = 800
    
    # Database Performance
    db_query_time_95th: int = 50  # Millisekunden
    db_connection_pool_max: int = 20
    
    # Memory & Resources
    max_memory_usage_mb: int = 512
    max_cpu_usage_percent: float = 80.0

@dataclass
class DesktopPerformanceTargets:
    """Desktop-spezifische Performance-Ziele"""
    # Moderne Desktop-Auflösungen (nur FHD und QHD)
    desktop_viewports = [
        {"width": 1920, "height": 1080, "name": "Full HD", "primary": True},
        {"width": 2560, "height": 1440, "name": "QHD Desktop", "primary": False}
    ]
    
    # Desktop-spezifische Performance Budgets
    performance_budgets = {
        "1920x1080": {  # Standard Desktop - Hauptzielgruppe
            "lcp_target": 1.8,
            "fid_target": 0.05,
            "cls_target": 0.05,
            "bundle_size": 800,
            "priority": "high"
        },
        "2560x1440": {  # High-End Desktop
            "lcp_target": 1.5,  # Noch schärfer (bessere Hardware)
            "fid_target": 0.04,
            "cls_target": 0.04,
            "bundle_size": 900,  # Mehr Bandbreite verfügbar
            "priority": "medium"
        }
    }
    
    # Desktop-optimierte Lighthouse-Konfiguration
    lighthouse_desktop_config = {
        "extends": "lighthouse:default",
        "settings": {
            "formFactor": "desktop",
            "throttling": {
                "rttMs": 40,
                "throughputKbps": 10240,
                "cpuSlowdownMultiplier": 1,
                "requestLatencyMs": 0,
                "downloadThroughputKbps": 0,
                "uploadThroughputKbps": 0
            },
            "screenEmulation": {
                "disabled": False,
                "width": 1920,
                "height": 1080,
                "deviceScaleFactor": 1,
                "mobile": False
            },
            "emulatedUserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    }

@dataclass
class TestDataConfig:
    """Test-Daten Konfiguration"""
    # Anzahl der zu erstellenden Testdaten
    employee_count: int = 1000
    vacation_allowance_entries_per_employee: int = 3
    
    # Cleanup nach Tests
    cleanup_after_tests: bool = True
    
    # Backup vor Tests
    backup_before_tests: bool = True

class TestScenarios:
    """Test-Szenarien Definition"""
    
    # API Endpunkte für Load Tests
    API_ENDPOINTS = {
        "employees": {
            "list": "/api/v1/employees",
            "create": "/api/v1/employees",
            "detail": "/api/v1/employees/{id}",
            "update": "/api/v1/employees/{id}",
            "delete": "/api/v1/employees/{id}",
            "search": "/api/v1/employees?search={query}"
        },
        "vacation_allowances": {
            "list": "/api/v1/vacation-allowances",
            "create": "/api/v1/vacation-allowances",
            "detail": "/api/v1/vacation-allowances/{id}",
            "update": "/api/v1/vacation-allowances/{id}",
            "delete": "/api/v1/vacation-allowances/{id}",
            "by_employee": "/api/v1/vacation-allowances?employee_id={id}"
        },
        "auth": {
            "login": "/api/v1/auth/login",
            "refresh": "/api/v1/auth/refresh",
            "logout": "/api/v1/auth/logout"
        },
        "federal_states": {
            "list": "/api/v1/federal-states"
        }
    }
    
    # Task-Gewichtung für Load Tests (höhere Zahl = häufiger ausgeführt)
    TASK_WEIGHTS = {
        "get_employees_list": 5,
        "get_employee_detail": 3,
        "search_employees": 2,
        "create_employee": 1,
        "update_employee": 1,
        "get_vacation_allowances": 3,
        "create_vacation_allowance": 1,
        "update_vacation_allowance": 1,
        "login": 1,
        "get_federal_states": 2
    }
    
    # Frontend-Seiten für Performance-Tests
    FRONTEND_PAGES = [
        "/",
        "/employees",
        "/employees?page=2",
        "/employees?search=test"
    ]
    
    # Database Query Test-Szenarien
    DB_TEST_SCENARIOS = [
        {
            "name": "simple_employee_query",
            "description": "Einzelner Employee by ID",
            "complexity": "low"
        },
        {
            "name": "employee_list_pagination",
            "description": "Employee Liste mit Pagination",
            "complexity": "medium"
        },
        {
            "name": "employee_search",
            "description": "Employee Suche mit LIKE",
            "complexity": "medium"
        },
        {
            "name": "employee_vacation_join",
            "description": "Employee mit VacationAllowances JOIN",
            "complexity": "high"
        },
        {
            "name": "vacation_aggregation",
            "description": "Vacation Allowance Aggregationen",
            "complexity": "high"
        }
    ]

class ReportConfig:
    """Report-Konfiguration"""
    
    # Output-Verzeichnisse
    REPORTS_DIR = "tests/performance/reports"
    SCREENSHOTS_DIR = "tests/performance/screenshots"
    LOGS_DIR = "tests/performance/logs"
    
    # Report-Formate
    GENERATE_HTML = True
    GENERATE_JSON = True
    GENERATE_CSV = True
    
    # Lighthouse Konfiguration
    LIGHTHOUSE_CONFIG = {
        "extends": "lighthouse:default",
        "settings": {
            "onlyCategories": ["performance", "accessibility"],
            "skipAudits": ["uses-http2"]
        }
    }

# Globale Konfiguration
config = APIConfig()
load_config = LoadTestConfig()
targets = PerformanceTargets()
desktop_targets = DesktopPerformanceTargets()
test_data_config = TestDataConfig()
scenarios = TestScenarios()
report_config = ReportConfig()

# Environment-spezifische Overrides
if os.getenv("PERFORMANCE_TEST_ENV") == "ci":
    # CI-spezifische Anpassungen
    load_config.baseline_duration = 60
    load_config.light_load_duration = 120
    load_config.medium_load_duration = 120
    load_config.heavy_load_duration = 120
    load_config.peak_load_duration = 60
    test_data_config.employee_count = 100
    test_data_config.vacation_allowance_entries_per_employee = 2

elif os.getenv("PERFORMANCE_TEST_ENV") == "local":
    # Lokale Entwicklung - schnellere Tests
    load_config.baseline_duration = 30
    load_config.light_load_duration = 60
    load_config.medium_load_duration = 60
    load_config.heavy_load_duration = 60
    load_config.peak_load_duration = 30
    test_data_config.employee_count = 50
    test_data_config.vacation_allowance_entries_per_employee = 2

def get_test_config() -> Dict:
    """Gibt die komplette Test-Konfiguration zurück"""
    return {
        "api": config,
        "load_test": load_config,
        "targets": targets,
        "desktop_targets": desktop_targets,
        "test_data": test_data_config,
        "scenarios": scenarios,
        "reports": report_config
    }

def load_test_config() -> Dict:
    """Lädt die Konfiguration - Alias für get_test_config()"""
    return get_test_config()

def validate_config() -> bool:
    """Validiert die Konfiguration"""
    try:
        # API-Erreichbarkeit prüfen
        import requests
        response = requests.get(f"{config.base_url}/api/v1/docs", timeout=5)
        if response.status_code != 200:
            print(f"API not reachable: {config.base_url}")
            return False
        
        # Frontend-Erreichbarkeit prüfen
        response = requests.get(config.frontend_url, timeout=5)
        if response.status_code != 200:
            print(f"Frontend not reachable: {config.frontend_url}")
            return False
        
        print("Configuration validation successful")
        return True
        
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Performance Test Configuration ===")
    print(f"API Base URL: {config.base_url}")
    print(f"Frontend URL: {config.frontend_url}")
    print(f"Test Data: {test_data_config.employee_count} employees")
    print(f"Max Users: {load_config.peak_load_users}")
    print(f"Target Response Time: {targets.api_response_time_95th}ms")
    
    print("\nValidating configuration...")
    if validate_config():
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration validation failed")

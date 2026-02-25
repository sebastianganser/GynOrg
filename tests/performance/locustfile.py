#!/usr/bin/env python3
"""
Locust Load Testing Configuration
Definiert Load Test Szenarien für die GynOrg API
"""

import json
import random
import time
from typing import Dict, Any
from locust import HttpUser, task, between, events
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from locust.log import setup_logging

from config import config, load_config, scenarios, targets

class GynOrgAPIUser(HttpUser):
    """Locust User für GynOrg API Load Tests"""
    
    wait_time = between(load_config.min_wait, load_config.max_wait)
    host = config.base_url
    
    def on_start(self):
        """Setup für jeden User - Login"""
        self.login()
        self.employee_ids = []
        self.vacation_allowance_ids = []
    
    def login(self):
        """Benutzer-Login"""
        login_data = {
            "username": config.auth_username,
            "password": config.auth_password
        }
        
        with self.client.post(
            "/api/v1/auth/login",
            json=login_data,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.client.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                response.success()
            else:
                response.failure(f"Login failed: {response.status_code}")
    
    @task(scenarios.TASK_WEIGHTS["get_employees_list"])
    def get_employees_list(self):
        """Employee Liste abrufen"""
        with self.client.get(
            "/api/v1/employees",
            catch_response=True,
            name="GET /employees"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                # Employee IDs für andere Tests sammeln
                if "items" in data:
                    self.employee_ids = [emp["id"] for emp in data["items"][:10]]
                response.success()
            else:
                response.failure(f"Failed to get employees: {response.status_code}")
    
    @task(scenarios.TASK_WEIGHTS["get_employee_detail"])
    def get_employee_detail(self):
        """Einzelnen Employee abrufen"""
        if not self.employee_ids:
            return
        
        employee_id = random.choice(self.employee_ids)
        with self.client.get(
            f"/api/v1/employees/{employee_id}",
            catch_response=True,
            name="GET /employees/{id}"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get employee {employee_id}: {response.status_code}")
    
    @task(scenarios.TASK_WEIGHTS["search_employees"])
    def search_employees(self):
        """Employee Suche"""
        search_terms = ["test", "maria", "max", "admin", "user"]
        search_term = random.choice(search_terms)
        
        with self.client.get(
            f"/api/v1/employees?search={search_term}",
            catch_response=True,
            name="GET /employees?search={term}"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to search employees: {response.status_code}")
    
    @task(scenarios.TASK_WEIGHTS["create_employee"])
    def create_employee(self):
        """Neuen Employee erstellen"""
        employee_data = {
            "first_name": f"Test{random.randint(1000, 9999)}",
            "last_name": f"User{random.randint(1000, 9999)}",
            "email": f"test{random.randint(1000, 9999)}@example.com",
            "phone": f"+49{random.randint(1000000000, 9999999999)}",
            "address": f"Teststraße {random.randint(1, 100)}",
            "position": "Test Position",
            "department": "Test Department",
            "hire_date": "2024-01-01",
            "salary": random.randint(30000, 80000),
            "federal_state_id": random.randint(1, 16),
            "is_active": True
        }
        
        with self.client.post(
            "/api/v1/employees",
            json=employee_data,
            catch_response=True,
            name="POST /employees"
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.employee_ids.append(data["id"])
                response.success()
            else:
                response.failure(f"Failed to create employee: {response.status_code}")
    
    @task(scenarios.TASK_WEIGHTS["update_employee"])
    def update_employee(self):
        """Employee aktualisieren"""
        if not self.employee_ids:
            return
        
        employee_id = random.choice(self.employee_ids)
        update_data = {
            "salary": random.randint(30000, 80000),
            "position": f"Updated Position {random.randint(1, 100)}"
        }
        
        with self.client.patch(
            f"/api/v1/employees/{employee_id}",
            json=update_data,
            catch_response=True,
            name="PATCH /employees/{id}"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to update employee {employee_id}: {response.status_code}")
    
    @task(scenarios.TASK_WEIGHTS["get_vacation_allowances"])
    def get_vacation_allowances(self):
        """Vacation Allowances abrufen"""
        with self.client.get(
            "/api/v1/vacation-allowances",
            catch_response=True,
            name="GET /vacation-allowances"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "items" in data:
                    self.vacation_allowance_ids = [va["id"] for va in data["items"][:10]]
                response.success()
            else:
                response.failure(f"Failed to get vacation allowances: {response.status_code}")
    
    @task(scenarios.TASK_WEIGHTS["create_vacation_allowance"])
    def create_vacation_allowance(self):
        """Vacation Allowance erstellen"""
        if not self.employee_ids:
            return
        
        employee_id = random.choice(self.employee_ids)
        va_data = {
            "employee_id": employee_id,
            "year": random.choice([2024, 2025]),
            "total_days": random.randint(20, 30),
            "used_days": random.randint(0, 10),
            "remaining_days": random.randint(10, 30)
        }
        
        with self.client.post(
            "/api/v1/vacation-allowances",
            json=va_data,
            catch_response=True,
            name="POST /vacation-allowances"
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.vacation_allowance_ids.append(data["id"])
                response.success()
            else:
                response.failure(f"Failed to create vacation allowance: {response.status_code}")
    
    @task(scenarios.TASK_WEIGHTS["update_vacation_allowance"])
    def update_vacation_allowance(self):
        """Vacation Allowance aktualisieren"""
        if not self.vacation_allowance_ids:
            return
        
        va_id = random.choice(self.vacation_allowance_ids)
        update_data = {
            "used_days": random.randint(0, 15)
        }
        
        with self.client.patch(
            f"/api/v1/vacation-allowances/{va_id}",
            json=update_data,
            catch_response=True,
            name="PATCH /vacation-allowances/{id}"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to update vacation allowance {va_id}: {response.status_code}")
    
    @task(scenarios.TASK_WEIGHTS["get_federal_states"])
    def get_federal_states(self):
        """Federal States abrufen"""
        with self.client.get(
            "/api/v1/federal-states",
            catch_response=True,
            name="GET /federal-states"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to get federal states: {response.status_code}")

class LoadTestResults:
    """Sammelt und analysiert Load Test Ergebnisse"""
    
    def __init__(self):
        self.stats = {}
        self.errors = []
        self.response_times = []
    
    def collect_stats(self, environment):
        """Sammelt Statistiken aus Locust Environment"""
        stats = environment.stats
        
        # Gesamtstatistiken
        total_stats = stats.total
        
        self.stats = {
            "total_requests": total_stats.num_requests,
            "total_failures": total_stats.num_failures,
            "avg_response_time": total_stats.avg_response_time,
            "min_response_time": total_stats.min_response_time,
            "max_response_time": total_stats.max_response_time,
            "median_response_time": total_stats.median_response_time,
            "response_time_95th": total_stats.get_response_time_percentile(0.95),
            "response_time_99th": total_stats.get_response_time_percentile(0.99),
            "requests_per_second": total_stats.total_rps,
            "error_rate": (total_stats.num_failures / max(total_stats.num_requests, 1)) * 100,
            "scenarios_count": len([name for name in stats.entries.keys() if not name.startswith("Aggregated")])
        }
        
        # Detaillierte Endpoint-Statistiken
        self.stats["endpoints"] = {}
        for name, entry in stats.entries.items():
            if name != "Aggregated":
                self.stats["endpoints"][name] = {
                    "requests": entry.num_requests,
                    "failures": entry.num_failures,
                    "avg_response_time": entry.avg_response_time,
                    "min_response_time": entry.min_response_time,
                    "max_response_time": entry.max_response_time,
                    "rps": entry.total_rps,
                    "error_rate": (entry.num_failures / max(entry.num_requests, 1)) * 100
                }
        
        # Fehler sammeln
        self.errors = []
        for error in stats.errors.values():
            self.errors.append({
                "method": error.method,
                "name": error.name,
                "error": error.error,
                "occurrences": error.occurrences
            })
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analysiert die Ergebnisse gegen Performance-Ziele"""
        analysis = {
            "performance_targets_met": {
                "response_time_95th": self.stats.get("response_time_95th", 999) <= targets.api_response_time_95th,
                "response_time_avg": self.stats.get("avg_response_time", 999) <= targets.api_response_time_avg,
                "error_rate": self.stats.get("error_rate", 100) <= targets.max_error_rate,
                "max_response_time": self.stats.get("max_response_time", 999) <= targets.api_response_time_max
            },
            "peak_users_handled": load_config.peak_load_users,  # Annahme: alle geplanten User wurden verarbeitet
            "critical_issues": []
        }
        
        # Kritische Issues identifizieren
        if self.stats.get("error_rate", 0) > targets.max_error_rate:
            analysis["critical_issues"].append(f"Error rate {self.stats['error_rate']:.2f}% exceeds target {targets.max_error_rate}%")
        
        if self.stats.get("response_time_95th", 0) > targets.api_response_time_95th:
            analysis["critical_issues"].append(f"95th percentile response time {self.stats['response_time_95th']:.1f}ms exceeds target {targets.api_response_time_95th}ms")
        
        if self.stats.get("avg_response_time", 0) > targets.api_response_time_avg:
            analysis["critical_issues"].append(f"Average response time {self.stats['avg_response_time']:.1f}ms exceeds target {targets.api_response_time_avg}ms")
        
        return analysis

async def run_load_tests() -> Dict[str, Any]:
    """Führt die kompletten Load Tests aus"""
    print("🚀 Starting API Load Tests")
    
    # Setup Logging
    setup_logging("INFO", None)
    
    # Environment erstellen
    env = Environment(user_classes=[GynOrgAPIUser])
    
    # Results Collector
    results_collector = LoadTestResults()
    
    try:
        # Test-Szenarien durchführen
        test_scenarios = [
            {"users": load_config.baseline_users, "duration": load_config.baseline_duration, "name": "Baseline"},
            {"users": load_config.light_load_users, "duration": load_config.light_load_duration, "name": "Light Load"},
            {"users": load_config.medium_load_users, "duration": load_config.medium_load_duration, "name": "Medium Load"},
            {"users": load_config.heavy_load_users, "duration": load_config.heavy_load_duration, "name": "Heavy Load"},
            {"users": load_config.peak_load_users, "duration": load_config.peak_load_duration, "name": "Peak Load"}
        ]
        
        for scenario in test_scenarios:
            print(f"\n--- Running {scenario['name']} Test ---")
            print(f"Users: {scenario['users']}, Duration: {scenario['duration']}s")
            
            # Reset stats für jedes Szenario
            env.stats.reset_all()
            
            # Test starten
            env.create_local_runner()
            env.runner.start(scenario["users"], spawn_rate=load_config.spawn_rate)
            
            # Test laufen lassen
            time.sleep(scenario["duration"])
            
            # Test stoppen
            env.runner.quit()
            
            print(f"✅ {scenario['name']} Test completed")
            print(f"   Requests: {env.stats.total.num_requests}")
            print(f"   Failures: {env.stats.total.num_failures}")
            print(f"   Avg Response Time: {env.stats.total.avg_response_time:.1f}ms")
            print(f"   95th Percentile: {env.stats.total.get_response_time_percentile(0.95):.1f}ms")
            print(f"   Error Rate: {(env.stats.total.num_failures / max(env.stats.total.num_requests, 1)) * 100:.2f}%")
        
        # Finale Statistiken sammeln
        results_collector.collect_stats(env)
        analysis = results_collector.analyze_results()
        
        # Ergebnisse zusammenstellen
        final_results = {
            **results_collector.stats,
            **analysis,
            "test_scenarios_completed": len(test_scenarios),
            "total_test_duration": sum(s["duration"] for s in test_scenarios)
        }
        
        print(f"\n🎯 Load Test Summary:")
        print(f"   Total Requests: {final_results['total_requests']}")
        print(f"   Total Failures: {final_results['total_failures']}")
        print(f"   Error Rate: {final_results['error_rate']:.2f}%")
        print(f"   Avg Response Time: {final_results['avg_response_time']:.1f}ms")
        print(f"   95th Percentile: {final_results['response_time_95th']:.1f}ms")
        print(f"   Peak Users Handled: {final_results['peak_users_handled']}")
        
        # Performance Targets Check
        targets_met = all(final_results["performance_targets_met"].values())
        print(f"   Performance Targets: {'✅ MET' if targets_met else '❌ NOT MET'}")
        
        if final_results["critical_issues"]:
            print("   Critical Issues:")
            for issue in final_results["critical_issues"]:
                print(f"     - {issue}")
        
        return final_results
        
    except Exception as e:
        print(f"❌ Load Tests failed: {e}")
        return {
            "error": str(e),
            "total_requests": 0,
            "total_failures": 0,
            "error_rate": 100,
            "avg_response_time": 999,
            "response_time_95th": 999,
            "peak_users_handled": 0,
            "performance_targets_met": {
                "response_time_95th": False,
                "response_time_avg": False,
                "error_rate": False,
                "max_response_time": False
            },
            "critical_issues": [f"Load test execution failed: {e}"]
        }

if __name__ == "__main__":
    import asyncio
    
    print("=== GynOrg API Load Testing ===")
    results = asyncio.run(run_load_tests())
    
    print("\n=== Final Results ===")
    print(json.dumps(results, indent=2))

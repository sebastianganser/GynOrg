#!/usr/bin/env python3
"""
Database Performance Testing
Direkte Datenbank-Performance-Tests für komplexe Queries
"""

import time
import asyncio
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import asyncpg
import psutil
import json
from dataclasses import dataclass, asdict

from config import targets, scenarios

@dataclass
class QueryResult:
    """Ergebnis eines Query-Performance-Tests"""
    query_name: str
    sql: str
    execution_time_ms: float
    rows_returned: int
    complexity: str
    timestamp: str
    success: bool
    error_message: str = ""

@dataclass
class DatabaseMetrics:
    """Database Performance Metriken"""
    total_queries: int
    successful_queries: int
    failed_queries: int
    avg_execution_time: float
    min_execution_time: float
    max_execution_time: float
    p95_execution_time: float
    total_rows_processed: int
    queries_per_second: float

class DatabasePerformanceTester:
    """Database Performance Test Runner"""
    
    def __init__(self, db_url: str = "postgresql://postgres:postgres@localhost:5432/gynorg"):
        self.db_url = db_url
        self.connection_pool = None
        self.results: List[QueryResult] = []
        self.start_time = None
        self.end_time = None
    
    async def setup(self):
        """Database Connection Pool Setup"""
        try:
            self.connection_pool = await asyncpg.create_pool(
                self.db_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            print("Database connection pool created successfully")
            return True
        except Exception as e:
            print(f"Failed to create database connection pool: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup Database Connections"""
        if self.connection_pool:
            await self.connection_pool.close()
            print("Database connection pool closed")
    
    async def execute_query(self, query_name: str, sql: str, complexity: str = "medium") -> QueryResult:
        """Führt eine Query aus und misst Performance"""
        start_time = time.time()
        
        try:
            async with self.connection_pool.acquire() as connection:
                rows = await connection.fetch(sql)
                execution_time = (time.time() - start_time) * 1000  # in ms
                
                result = QueryResult(
                    query_name=query_name,
                    sql=sql,
                    execution_time_ms=execution_time,
                    rows_returned=len(rows),
                    complexity=complexity,
                    timestamp=datetime.now().isoformat(),
                    success=True
                )
                
                print(f"✅ {query_name}: {execution_time:.2f}ms ({len(rows)} rows)")
                return result
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            result = QueryResult(
                query_name=query_name,
                sql=sql,
                execution_time_ms=execution_time,
                rows_returned=0,
                complexity=complexity,
                timestamp=datetime.now().isoformat(),
                success=False,
                error_message=str(e)
            )
            
            print(f"❌ {query_name}: Failed after {execution_time:.2f}ms - {e}")
            return result
    
    async def test_simple_queries(self) -> List[QueryResult]:
        """Einfache Query-Tests"""
        print("\n=== Testing Simple Queries ===")
        
        queries = [
            ("employee_by_id", "SELECT * FROM employees WHERE id = 1", "low"),
            ("employee_count", "SELECT COUNT(*) FROM employees", "low"),
            ("federal_states_list", "SELECT * FROM federal_states ORDER BY name", "low"),
            ("vacation_allowance_by_id", "SELECT * FROM vacation_allowances WHERE id = 1", "low"),
            ("employee_exists", "SELECT EXISTS(SELECT 1 FROM employees WHERE id = 1)", "low"),
        ]
        
        results = []
        for query_name, sql, complexity in queries:
            result = await self.execute_query(query_name, sql, complexity)
            results.append(result)
            self.results.append(result)
            
            # Kurze Pause zwischen Queries
            await asyncio.sleep(0.1)
        
        return results
    
    async def test_pagination_queries(self) -> List[QueryResult]:
        """Pagination Performance Tests"""
        print("\n=== Testing Pagination Queries ===")
        
        queries = [
            ("employees_page_1", "SELECT * FROM employees ORDER BY id LIMIT 20 OFFSET 0", "medium"),
            ("employees_page_10", "SELECT * FROM employees ORDER BY id LIMIT 20 OFFSET 200", "medium"),
            ("employees_page_50", "SELECT * FROM employees ORDER BY id LIMIT 20 OFFSET 1000", "medium"),
            ("vacation_allowances_page_1", "SELECT * FROM vacation_allowances ORDER BY id LIMIT 50 OFFSET 0", "medium"),
            ("vacation_allowances_page_20", "SELECT * FROM vacation_allowances ORDER BY id LIMIT 50 OFFSET 1000", "medium"),
        ]
        
        results = []
        for query_name, sql, complexity in queries:
            result = await self.execute_query(query_name, sql, complexity)
            results.append(result)
            self.results.append(result)
            await asyncio.sleep(0.1)
        
        return results
    
    async def test_search_queries(self) -> List[QueryResult]:
        """Such-Performance Tests"""
        print("\n=== Testing Search Queries ===")
        
        queries = [
            ("search_employee_name", "SELECT * FROM employees WHERE first_name ILIKE '%test%' OR last_name ILIKE '%test%'", "medium"),
            ("search_employee_email", "SELECT * FROM employees WHERE email ILIKE '%@example.com%'", "medium"),
            ("search_employee_department", "SELECT * FROM employees WHERE department = 'IT'", "medium"),
            ("search_employee_position", "SELECT * FROM employees WHERE position ILIKE '%manager%'", "medium"),
            ("search_employee_salary_range", "SELECT * FROM employees WHERE salary BETWEEN 50000 AND 80000", "medium"),
        ]
        
        results = []
        for query_name, sql, complexity in queries:
            result = await self.execute_query(query_name, sql, complexity)
            results.append(result)
            self.results.append(result)
            await asyncio.sleep(0.1)
        
        return results
    
    async def test_join_queries(self) -> List[QueryResult]:
        """JOIN Performance Tests"""
        print("\n=== Testing JOIN Queries ===")
        
        queries = [
            ("employee_with_federal_state", """
                SELECT e.*, fs.name as federal_state_name 
                FROM employees e 
                LEFT JOIN federal_states fs ON e.federal_state_id = fs.id 
                LIMIT 100
            """, "high"),
            
            ("employee_with_vacation_allowances", """
                SELECT e.first_name, e.last_name, va.year, va.total_days, va.used_days
                FROM employees e
                LEFT JOIN vacation_allowances va ON e.id = va.employee_id
                WHERE e.id <= 50
                ORDER BY e.id, va.year
            """, "high"),
            
            ("employees_with_current_year_vacation", """
                SELECT e.*, va.total_days, va.used_days, (va.total_days - va.used_days) as remaining_days
                FROM employees e
                LEFT JOIN vacation_allowances va ON e.id = va.employee_id AND va.year = EXTRACT(YEAR FROM CURRENT_DATE)
                ORDER BY e.last_name, e.first_name
                LIMIT 200
            """, "high"),
            
            ("vacation_summary_by_department", """
                SELECT e.department, 
                       COUNT(DISTINCT e.id) as employee_count,
                       AVG(va.total_days) as avg_vacation_days,
                       SUM(va.used_days) as total_used_days
                FROM employees e
                LEFT JOIN vacation_allowances va ON e.id = va.employee_id
                WHERE va.year = EXTRACT(YEAR FROM CURRENT_DATE)
                GROUP BY e.department
                ORDER BY employee_count DESC
            """, "high"),
        ]
        
        results = []
        for query_name, sql, complexity in queries:
            result = await self.execute_query(query_name, sql, complexity)
            results.append(result)
            self.results.append(result)
            await asyncio.sleep(0.2)  # Längere Pause für komplexe Queries
        
        return results
    
    async def test_aggregation_queries(self) -> List[QueryResult]:
        """Aggregation Performance Tests"""
        print("\n=== Testing Aggregation Queries ===")
        
        queries = [
            ("employee_count_by_department", """
                SELECT department, COUNT(*) as employee_count
                FROM employees 
                GROUP BY department 
                ORDER BY employee_count DESC
            """, "high"),
            
            ("salary_statistics", """
                SELECT 
                    COUNT(*) as total_employees,
                    AVG(salary) as avg_salary,
                    MIN(salary) as min_salary,
                    MAX(salary) as max_salary,
                    STDDEV(salary) as salary_stddev
                FROM employees
            """, "high"),
            
            ("vacation_utilization_stats", """
                SELECT 
                    va.year,
                    COUNT(*) as total_allowances,
                    AVG(va.total_days) as avg_total_days,
                    AVG(va.used_days) as avg_used_days,
                    AVG(CAST(va.used_days AS FLOAT) / va.total_days * 100) as avg_utilization_percent
                FROM vacation_allowances va
                GROUP BY va.year
                ORDER BY va.year DESC
            """, "high"),
            
            ("employees_by_hire_year", """
                SELECT 
                    EXTRACT(YEAR FROM hire_date) as hire_year,
                    COUNT(*) as employees_hired,
                    AVG(salary) as avg_starting_salary
                FROM employees
                GROUP BY EXTRACT(YEAR FROM hire_date)
                ORDER BY hire_year DESC
            """, "high"),
        ]
        
        results = []
        for query_name, sql, complexity in queries:
            result = await self.execute_query(query_name, sql, complexity)
            results.append(result)
            self.results.append(result)
            await asyncio.sleep(0.2)
        
        return results
    
    async def test_concurrent_queries(self, concurrent_users: int = 10) -> List[QueryResult]:
        """Concurrent Query Performance Tests"""
        print(f"\n=== Testing Concurrent Queries ({concurrent_users} users) ===")
        
        # Mix aus verschiedenen Query-Typen für realistische Last
        query_mix = [
            ("concurrent_employee_list", "SELECT * FROM employees ORDER BY id LIMIT 20", "medium"),
            ("concurrent_employee_search", "SELECT * FROM employees WHERE department = 'IT'", "medium"),
            ("concurrent_vacation_list", "SELECT * FROM vacation_allowances ORDER BY id LIMIT 30", "medium"),
            ("concurrent_employee_detail", "SELECT * FROM employees WHERE id = (SELECT id FROM employees ORDER BY RANDOM() LIMIT 1)", "medium"),
            ("concurrent_join_query", """
                SELECT e.first_name, e.last_name, va.total_days 
                FROM employees e 
                LEFT JOIN vacation_allowances va ON e.id = va.employee_id 
                WHERE e.id <= 10
            """, "high"),
        ]
        
        async def run_user_queries():
            """Simuliert einen User mit mehreren Queries"""
            user_results = []
            for _ in range(5):  # Jeder User führt 5 Queries aus
                query_name, sql, complexity = query_mix[len(user_results) % len(query_mix)]
                result = await self.execute_query(f"{query_name}_user", sql, complexity)
                user_results.append(result)
                await asyncio.sleep(0.1)
            return user_results
        
        # Concurrent Users starten
        start_time = time.time()
        tasks = [run_user_queries() for _ in range(concurrent_users)]
        all_results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Ergebnisse sammeln
        concurrent_results = []
        for user_results in all_results:
            concurrent_results.extend(user_results)
            self.results.extend(user_results)
        
        total_time = end_time - start_time
        total_queries = len(concurrent_results)
        qps = total_queries / total_time
        
        print(f"Concurrent test completed: {total_queries} queries in {total_time:.2f}s ({qps:.2f} QPS)")
        
        return concurrent_results
    
    def calculate_metrics(self) -> DatabaseMetrics:
        """Berechnet Performance-Metriken"""
        if not self.results:
            return DatabaseMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0)
        
        successful_results = [r for r in self.results if r.success]
        failed_results = [r for r in self.results if not r.success]
        
        if successful_results:
            execution_times = [r.execution_time_ms for r in successful_results]
            avg_time = statistics.mean(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            p95_time = statistics.quantiles(execution_times, n=20)[18] if len(execution_times) > 1 else avg_time
        else:
            avg_time = min_time = max_time = p95_time = 0
        
        total_rows = sum(r.rows_returned for r in successful_results)
        
        # QPS berechnen
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            qps = len(self.results) / duration if duration > 0 else 0
        else:
            qps = 0
        
        return DatabaseMetrics(
            total_queries=len(self.results),
            successful_queries=len(successful_results),
            failed_queries=len(failed_results),
            avg_execution_time=avg_time,
            min_execution_time=min_time,
            max_execution_time=max_time,
            p95_execution_time=p95_time,
            total_rows_processed=total_rows,
            queries_per_second=qps
        )
    
    def check_performance_targets(self, metrics: DatabaseMetrics) -> Dict[str, bool]:
        """Prüft Performance-Ziele"""
        checks = {
            "avg_execution_time": metrics.avg_execution_time <= targets.db_query_time_95th,
            "p95_execution_time": metrics.p95_execution_time <= targets.db_query_time_95th * 2,
            "error_rate": (metrics.failed_queries / metrics.total_queries * 100) <= targets.max_error_rate if metrics.total_queries > 0 else True,
            "queries_per_second": metrics.queries_per_second >= 10  # Mindestens 10 QPS
        }
        
        return checks
    
    async def run_full_test_suite(self) -> Dict[str, Any]:
        """Führt alle Database Performance Tests aus"""
        print("=== Starting Database Performance Test Suite ===")
        
        if not await self.setup():
            return {"error": "Failed to setup database connection"}
        
        self.start_time = time.time()
        
        try:
            # Test-Suites ausführen
            await self.test_simple_queries()
            await self.test_pagination_queries()
            await self.test_search_queries()
            await self.test_join_queries()
            await self.test_aggregation_queries()
            await self.test_concurrent_queries(concurrent_users=5)
            
            self.end_time = time.time()
            
            # Metriken berechnen
            metrics = self.calculate_metrics()
            performance_checks = self.check_performance_targets(metrics)
            
            # Ergebnisse zusammenfassen
            test_results = {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": self.end_time - self.start_time,
                "metrics": asdict(metrics),
                "performance_checks": performance_checks,
                "all_passed": all(performance_checks.values()),
                "detailed_results": [asdict(r) for r in self.results]
            }
            
            # Report ausgeben
            self.print_summary_report(metrics, performance_checks)
            
            return test_results
            
        finally:
            await self.cleanup()
    
    def print_summary_report(self, metrics: DatabaseMetrics, checks: Dict[str, bool]):
        """Druckt Summary Report"""
        print("\n" + "="*60)
        print("DATABASE PERFORMANCE TEST SUMMARY")
        print("="*60)
        
        print(f"Total Queries: {metrics.total_queries}")
        print(f"Successful: {metrics.successful_queries}")
        print(f"Failed: {metrics.failed_queries}")
        print(f"Success Rate: {(metrics.successful_queries/metrics.total_queries*100):.1f}%")
        
        print(f"\nExecution Times:")
        print(f"  Average: {metrics.avg_execution_time:.2f}ms")
        print(f"  Min: {metrics.min_execution_time:.2f}ms")
        print(f"  Max: {metrics.max_execution_time:.2f}ms")
        print(f"  95th Percentile: {metrics.p95_execution_time:.2f}ms")
        
        print(f"\nThroughput:")
        print(f"  Queries per Second: {metrics.queries_per_second:.2f}")
        print(f"  Total Rows Processed: {metrics.total_rows_processed}")
        
        print(f"\nPerformance Targets:")
        for check_name, passed in checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {check_name}: {status}")
        
        overall_status = "✅ ALL TESTS PASSED" if all(checks.values()) else "❌ SOME TESTS FAILED"
        print(f"\nOverall Result: {overall_status}")
        print("="*60)

async def main():
    """Hauptfunktion für direkten Test-Aufruf"""
    tester = DatabasePerformanceTester()
    results = await tester.run_full_test_suite()
    
    # Ergebnisse in Datei speichern
    with open("tests/performance/db_performance_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: tests/performance/db_performance_results.json")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())

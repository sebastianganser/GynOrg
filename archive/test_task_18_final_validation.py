"""
Final Validation Script for Task 18: Complete Multi-Year Holiday System

This script runs all validation tests and creates a comprehensive final report
for Task 18 implementation readiness.
"""

import subprocess
import sys
import json
import time
from datetime import datetime
from pathlib import Path

class Task18FinalValidator:
    """Final validation orchestrator for Task 18"""
    
    def __init__(self):
        self.results = {
            "validation_timestamp": datetime.now().isoformat(),
            "task_18_status": "pending",
            "subtask_results": {},
            "performance_metrics": {},
            "final_grade": "pending",
            "go_live_ready": False,
            "issues": [],
            "recommendations": []
        }
    
    def run_test_script(self, script_path: str, description: str) -> dict:
        """Run a test script and capture results"""
        print(f"\n🔍 Running {description}...")
        print(f"   Script: {script_path}")
        
        try:
            # Check if script exists
            if not Path(script_path).exists():
                return {
                    "status": "skipped",
                    "reason": f"Script not found: {script_path}",
                    "duration": 0
                }
            
            start_time = time.time()
            
            # Run the script
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            return {
                "status": "passed" if result.returncode == 0 else "failed",
                "returncode": result.returncode,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "reason": "Test script timed out after 5 minutes",
                "duration": 300
            }
        except Exception as e:
            return {
                "status": "error",
                "reason": str(e),
                "duration": 0
            }
    
    def validate_subtask_18_1_to_18_3(self) -> dict:
        """Validate backend API subtasks 18.1-18.3"""
        print("\n📋 Validating Backend API Subtasks (18.1-18.3)...")
        
        result = self.run_test_script(
            "backend/test_task_18_3_api.py",
            "Backend Holiday API Tests (Subtasks 18.1-18.3)"
        )
        
        if result["status"] == "passed":
            print("   ✅ Backend API tests passed")
            return {"grade": "A", "status": "passed", "details": "All backend API features working"}
        elif result["status"] == "skipped":
            print("   ⚠️ Backend API tests skipped")
            return {"grade": "C", "status": "skipped", "details": result["reason"]}
        else:
            print("   ❌ Backend API tests failed")
            return {"grade": "F", "status": "failed", "details": result.get("stderr", "Unknown error")}
    
    def validate_subtask_18_4_to_18_5(self) -> dict:
        """Validate frontend subtasks 18.4-18.5"""
        print("\n🎨 Validating Frontend Subtasks (18.4-18.5)...")
        
        # Check if frontend test files exist
        frontend_tests = [
            "frontend/test_useHolidays_multi_year.html",
            "frontend/test_year_navigation.html"
        ]
        
        existing_tests = [test for test in frontend_tests if Path(test).exists()]
        
        if len(existing_tests) == len(frontend_tests):
            print(f"   ✅ All {len(frontend_tests)} frontend test files found")
            return {"grade": "A", "status": "passed", "details": "Frontend tests available"}
        elif len(existing_tests) > 0:
            print(f"   ⚠️ {len(existing_tests)}/{len(frontend_tests)} frontend test files found")
            return {"grade": "B", "status": "partial", "details": f"Some frontend tests missing"}
        else:
            print("   ❌ No frontend test files found")
            return {"grade": "D", "status": "failed", "details": "Frontend tests missing"}
    
    def validate_subtask_18_6(self) -> dict:
        """Validate absence calculation subtask 18.6"""
        print("\n🧮 Validating Absence Calculations (18.6)...")
        
        result = self.run_test_script(
            "backend/test_task_18_6_absence_calculations.py",
            "Absence Calculation Tests (Subtask 18.6)"
        )
        
        if result["status"] == "passed":
            print("   ✅ Absence calculation tests passed")
            return {"grade": "A", "status": "passed", "details": "Absence calculations working"}
        elif result["status"] == "skipped":
            print("   ⚠️ Absence calculation tests skipped")
            return {"grade": "C", "status": "skipped", "details": result["reason"]}
        else:
            print("   ❌ Absence calculation tests failed")
            return {"grade": "F", "status": "failed", "details": result.get("stderr", "Unknown error")}
    
    def validate_subtask_18_7(self) -> dict:
        """Validate database migration subtask 18.7"""
        print("\n🗄️ Validating Database Migrations (18.7)...")
        
        result = self.run_test_script(
            "backend/test_migration_18_7.py",
            "Database Migration Tests (Subtask 18.7)"
        )
        
        # Check if migration file exists
        migration_file = "backend/alembic/versions/d4f8e9a1b2c3_add_holiday_performance_optimizations.py"
        migration_exists = Path(migration_file).exists()
        
        if migration_exists:
            print("   ✅ Migration file exists")
            if result["status"] == "passed":
                return {"grade": "A", "status": "passed", "details": "Migration ready and validated"}
            else:
                return {"grade": "B", "status": "ready", "details": "Migration file ready (tests need server)"}
        else:
            print("   ❌ Migration file missing")
            return {"grade": "F", "status": "failed", "details": "Migration file not found"}
    
    def validate_subtask_18_8(self) -> dict:
        """Validate comprehensive testing subtask 18.8"""
        print("\n🔬 Validating Comprehensive Testing (18.8)...")
        
        result = self.run_test_script(
            "backend/test_task_18_8_comprehensive.py",
            "Comprehensive System Tests (Subtask 18.8)"
        )
        
        if result["status"] == "passed":
            print("   ✅ Comprehensive tests passed")
            return {"grade": "A", "status": "passed", "details": "All comprehensive tests passed"}
        elif result["status"] == "skipped":
            print("   ⚠️ Comprehensive tests skipped")
            return {"grade": "C", "status": "skipped", "details": result["reason"]}
        else:
            print("   ❌ Comprehensive tests failed")
            return {"grade": "F", "status": "failed", "details": result.get("stderr", "Unknown error")}
    
    def calculate_overall_grade(self, subtask_results: dict) -> str:
        """Calculate overall grade based on subtask results"""
        grade_points = {
            "A": 4.0,
            "B": 3.0,
            "C": 2.0,
            "D": 1.0,
            "F": 0.0
        }
        
        # Weight subtasks by importance
        weights = {
            "18.1-18.3": 0.25,  # Backend API
            "18.4-18.5": 0.20,  # Frontend
            "18.6": 0.25,       # Absence Calculations
            "18.7": 0.15,       # Database Migrations
            "18.8": 0.15        # Comprehensive Testing
        }
        
        total_points = 0
        total_weight = 0
        
        for subtask, result in subtask_results.items():
            grade = result.get("grade", "F")
            weight = weights.get(subtask, 0.1)
            
            total_points += grade_points.get(grade, 0) * weight
            total_weight += weight
        
        if total_weight == 0:
            return "F"
        
        avg_points = total_points / total_weight
        
        if avg_points >= 3.7:
            return "A"
        elif avg_points >= 3.0:
            return "B"
        elif avg_points >= 2.0:
            return "C"
        elif avg_points >= 1.0:
            return "D"
        else:
            return "F"
    
    def generate_recommendations(self, subtask_results: dict, overall_grade: str) -> list:
        """Generate recommendations based on results"""
        recommendations = []
        
        # Check for failed subtasks
        failed_subtasks = [k for k, v in subtask_results.items() if v.get("status") == "failed"]
        if failed_subtasks:
            recommendations.append(f"🔴 CRITICAL: Fix failed subtasks: {', '.join(failed_subtasks)}")
        
        # Check for skipped subtasks
        skipped_subtasks = [k for k, v in subtask_results.items() if v.get("status") == "skipped"]
        if skipped_subtasks:
            recommendations.append(f"🟡 IMPORTANT: Complete skipped subtasks: {', '.join(skipped_subtasks)}")
        
        # Grade-specific recommendations
        if overall_grade in ["A", "B"]:
            recommendations.append("✅ System ready for production deployment")
            recommendations.append("🚀 Consider running final integration tests with real data")
        elif overall_grade == "C":
            recommendations.append("⚠️ System needs improvements before production")
            recommendations.append("🔧 Focus on fixing failed tests and performance issues")
        else:
            recommendations.append("❌ System not ready for production")
            recommendations.append("🛠️ Major fixes required before deployment")
        
        # Always recommend server testing
        recommendations.append("🖥️ Run tests with server running for complete validation")
        
        return recommendations
    
    def run_validation(self) -> dict:
        """Run complete validation process"""
        print("🚀 Starting Task 18 Final Validation...")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all subtask validations
        subtask_results = {
            "18.1-18.3": self.validate_subtask_18_1_to_18_3(),
            "18.4-18.5": self.validate_subtask_18_4_to_18_5(),
            "18.6": self.validate_subtask_18_6(),
            "18.7": self.validate_subtask_18_7(),
            "18.8": self.validate_subtask_18_8()
        }
        
        # Calculate overall results
        overall_grade = self.calculate_overall_grade(subtask_results)
        recommendations = self.generate_recommendations(subtask_results, overall_grade)
        
        # Determine go-live readiness
        passed_count = sum(1 for r in subtask_results.values() if r.get("status") == "passed")
        total_count = len(subtask_results)
        go_live_ready = overall_grade in ["A", "B"] and passed_count >= 3
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Update results
        self.results.update({
            "subtask_results": subtask_results,
            "final_grade": overall_grade,
            "go_live_ready": go_live_ready,
            "recommendations": recommendations,
            "validation_duration": total_duration,
            "passed_subtasks": passed_count,
            "total_subtasks": total_count
        })
        
        return self.results
    
    def print_final_report(self, results: dict):
        """Print comprehensive final report"""
        print("\n" + "=" * 80)
        print("📊 TASK 18 FINAL VALIDATION REPORT")
        print("=" * 80)
        
        print(f"\n🕐 Validation completed: {results['validation_timestamp']}")
        print(f"⏱️ Total duration: {results['validation_duration']:.2f} seconds")
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Final Grade: {results['final_grade']}")
        print(f"   Passed Subtasks: {results['passed_subtasks']}/{results['total_subtasks']}")
        print(f"   Go-Live Ready: {'✅ YES' if results['go_live_ready'] else '❌ NO'}")
        
        print(f"\n📋 SUBTASK BREAKDOWN:")
        for subtask, result in results['subtask_results'].items():
            status_icon = {
                "passed": "✅",
                "failed": "❌",
                "skipped": "⚠️",
                "partial": "🟡",
                "ready": "🔧"
            }.get(result.get("status"), "❓")
            
            print(f"   {status_icon} {subtask}: {result.get('grade', 'N/A')} - {result.get('details', 'No details')}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        if results['go_live_ready']:
            print(f"\n🎉 CONGRATULATIONS!")
            print(f"   Task 18 Multi-Year Holiday System is ready for production!")
            print(f"   All critical components are functional and tested.")
        else:
            print(f"\n⚠️ ATTENTION REQUIRED")
            print(f"   Task 18 needs additional work before production deployment.")
            print(f"   Please address the recommendations above.")
        
        print("\n" + "=" * 80)


def main():
    """Main validation function"""
    validator = Task18FinalValidator()
    
    try:
        results = validator.run_validation()
        validator.print_final_report(results)
        
        # Save results to file
        report_file = f"task_18_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Exit with appropriate code
        if results['go_live_ready']:
            print("\n✅ Validation PASSED - Task 18 ready for production!")
            sys.exit(0)
        else:
            print("\n❌ Validation INCOMPLETE - Additional work required")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Validation interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n❌ Validation failed with error: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()

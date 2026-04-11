"""
Test Suite for Migration 18.7: Holiday Performance Optimizations

This test validates the performance optimization migration for multi-year holiday support.
"""

import pytest
import sqlite3
import os
from pathlib import Path

# Test configuration
DB_PATH = "data/gynorg.db"
MIGRATION_FILE = "backend/alembic/versions/d4f8e9a1b2c3_add_holiday_performance_optimizations.py"

def test_database_exists():
    """Test that the database exists"""
    print("\n🔍 Test 1: Database Existence Check...")
    
    if os.path.exists(DB_PATH):
        print(f"   ✅ Database found at: {DB_PATH}")
        return True
    else:
        print(f"   ❌ Database not found at: {DB_PATH}")
        return False

def test_holidays_table_structure():
    """Test that the holidays table has the expected structure"""
    print("\n📋 Test 2: Holidays Table Structure...")
    
    if not os.path.exists(DB_PATH):
        print("   ⚠️ Database not found, skipping test")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get table info
        cursor.execute("PRAGMA table_info(holidays)")
        columns = cursor.fetchall()
        
        expected_columns = [
            'id', 'name', 'date', 'federal_state', 'is_nationwide', 
            'year', 'notes', 'created_at', 'updated_at'
        ]
        
        actual_columns = [col[1] for col in columns]
        
        print(f"   📊 Found columns: {actual_columns}")
        
        missing_columns = set(expected_columns) - set(actual_columns)
        if missing_columns:
            print(f"   ❌ Missing columns: {missing_columns}")
            return False
        
        print("   ✅ All expected columns present")
        return True
        
    except Exception as e:
        print(f"   ❌ Error checking table structure: {e}")
        return False
    finally:
        conn.close()

def test_existing_indexes():
    """Test current indexes on holidays table"""
    print("\n🔍 Test 3: Current Index Analysis...")
    
    if not os.path.exists(DB_PATH):
        print("   ⚠️ Database not found, skipping test")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get existing indexes
        cursor.execute("PRAGMA index_list(holidays)")
        indexes = cursor.fetchall()
        
        print(f"   📊 Current indexes: {len(indexes)}")
        for idx in indexes:
            print(f"     • {idx[1]} (unique: {bool(idx[2])})")
            
            # Get index details
            cursor.execute(f"PRAGMA index_info({idx[1]})")
            index_info = cursor.fetchall()
            columns = [info[2] for info in index_info]
            print(f"       Columns: {columns}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error checking indexes: {e}")
        return False
    finally:
        conn.close()

def test_holiday_data_sample():
    """Test sample holiday data"""
    print("\n📅 Test 4: Holiday Data Sample...")
    
    if not os.path.exists(DB_PATH):
        print("   ⚠️ Database not found, skipping test")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM holidays")
        total_count = cursor.fetchone()[0]
        print(f"   📊 Total holidays: {total_count}")
        
        if total_count == 0:
            print("   ⚠️ No holiday data found")
            return True
        
        # Get year range
        cursor.execute("SELECT MIN(year), MAX(year) FROM holidays")
        year_range = cursor.fetchone()
        print(f"   📅 Year range: {year_range[0]} - {year_range[1]}")
        
        # Get sample data
        cursor.execute("""
            SELECT name, date, federal_state, year 
            FROM holidays 
            ORDER BY date 
            LIMIT 5
        """)
        samples = cursor.fetchall()
        
        print("   📋 Sample holidays:")
        for sample in samples:
            state = sample[2] if sample[2] else "Bundesweit"
            print(f"     • {sample[0]} ({sample[1]}) - {state}")
        
        # Check for year-date consistency
        cursor.execute("""
            SELECT COUNT(*) 
            FROM holidays 
            WHERE CAST(strftime('%Y', date) AS INTEGER) != year
        """)
        inconsistent = cursor.fetchone()[0]
        
        if inconsistent > 0:
            print(f"   ⚠️ Found {inconsistent} holidays with year-date inconsistencies")
        else:
            print("   ✅ All holidays have consistent year-date values")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error checking holiday data: {e}")
        return False
    finally:
        conn.close()

def test_migration_file_exists():
    """Test that the migration file exists and is valid"""
    print("\n📄 Test 5: Migration File Validation...")
    
    if not os.path.exists(MIGRATION_FILE):
        print(f"   ❌ Migration file not found: {MIGRATION_FILE}")
        return False
    
    print(f"   ✅ Migration file found: {MIGRATION_FILE}")
    
    # Read and validate migration content
    with open(MIGRATION_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required elements
    required_elements = [
        'def upgrade()',
        'def downgrade()',
        'idx_holidays_year',
        'idx_holidays_federal_state',
        'idx_holidays_year_federal_state',
        'idx_holidays_date_year'
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"   ❌ Missing elements in migration: {missing_elements}")
        return False
    
    print("   ✅ Migration file contains all required elements")
    print("   📋 Performance indexes to be added:")
    print("     • idx_holidays_year - Year-based queries")
    print("     • idx_holidays_federal_state - State-specific queries")
    print("     • idx_holidays_year_federal_state - Multi-year state queries")
    print("     • idx_holidays_date_year - Date range queries")
    
    return True

def test_performance_baseline():
    """Measure current query performance as baseline"""
    print("\n⚡ Test 6: Performance Baseline Measurement...")
    
    if not os.path.exists(DB_PATH):
        print("   ⚠️ Database not found, skipping test")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        import time
        
        # Test queries that will benefit from indexes
        test_queries = [
            ("Year-based query", "SELECT COUNT(*) FROM holidays WHERE year = 2024"),
            ("State-based query", "SELECT COUNT(*) FROM holidays WHERE federal_state = 'SACHSEN_ANHALT'"),
            ("Multi-year range", "SELECT COUNT(*) FROM holidays WHERE year BETWEEN 2023 AND 2025"),
            ("Date range query", "SELECT COUNT(*) FROM holidays WHERE date BETWEEN '2024-01-01' AND '2024-12-31'")
        ]
        
        print("   📊 Current query performance (before optimization):")
        
        for query_name, query in test_queries:
            start_time = time.time()
            cursor.execute(query)
            result = cursor.fetchone()[0]
            end_time = time.time()
            
            duration_ms = (end_time - start_time) * 1000
            print(f"     • {query_name}: {result} rows, {duration_ms:.2f}ms")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error measuring performance: {e}")
        return False
    finally:
        conn.close()

def run_migration_tests():
    """Run all migration tests"""
    print("🚀 Starting Migration 18.7 Tests...")
    print("=" * 60)
    
    tests = [
        test_database_exists,
        test_holidays_table_structure,
        test_existing_indexes,
        test_holiday_data_sample,
        test_migration_file_exists,
        test_performance_baseline
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Migration is ready to be applied.")
        print("\n🎯 Next Steps:")
        print("   1. Apply migration: alembic upgrade head")
        print("   2. Verify performance improvements")
        print("   3. Run post-migration validation")
    else:
        print(f"❌ {total - passed} tests failed. Please review before applying migration.")
    
    return passed == total

if __name__ == "__main__":
    run_migration_tests()

#!/usr/bin/env python3
"""
Test der robusten Cleanup-Funktion
"""

import asyncio
from run_phase1_tests import Phase1TestRunner

async def test_robust_cleanup():
    """Testet die robuste Cleanup-Funktion"""
    print("🧪 Testing robust cleanup function...")
    
    runner = Phase1TestRunner()
    
    # Test der robusten Cleanup-Funktion
    success = runner.robust_cleanup_database()
    
    print(f"\n🎯 Cleanup result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    return success

if __name__ == "__main__":
    asyncio.run(test_robust_cleanup())

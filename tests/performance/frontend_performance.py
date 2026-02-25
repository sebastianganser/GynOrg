#!/usr/bin/env python3
"""
Frontend Performance Testing
Lighthouse CI und Bundle Analyzer für Core Web Vitals
"""

import os
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import config, targets, scenarios, report_config

@dataclass
class CoreWebVitalsResult:
    """Core Web Vitals Ergebnis"""
    url: str
    lcp: float  # Largest Contentful Paint
    fid: float  # First Input Delay
    cls: float  # Cumulative Layout Shift
    fcp: float  # First Contentful Paint
    ttfb: float  # Time to First Byte
    performance_score: int
    accessibility_score: int
    timestamp: str
    passed_targets: bool

@dataclass
class BundleAnalysisResult:
    """Bundle Analyse Ergebnis"""
    total_size_kb: float
    js_size_kb: float
    css_size_kb: float
    largest_chunks: List[Dict[str, Any]]
    unused_code_percent: float
    passed_size_target: bool

class FrontendPerformanceTester:
    """Frontend Performance Test Runner"""
    
    def __init__(self):
        self.results: List[CoreWebVitalsResult] = []
        self.bundle_results: List[BundleAnalysisResult] = []
        self.driver = None
        
    def setup_chrome_driver(self) -> bool:
        """Chrome Driver für Lighthouse Setup"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            print("Chrome driver setup successful")
            return True
            
        except Exception as e:
            print(f"Failed to setup Chrome driver: {e}")
            return False
    
    def cleanup(self):
        """Cleanup Resources"""
        if self.driver:
            self.driver.quit()
            print("Chrome driver closed")
    
    def run_lighthouse_audit(self, url: str) -> CoreWebVitalsResult:
        """Führt Lighthouse Audit für eine URL aus"""
        print(f"Running Lighthouse audit for: {url}")
        
        try:
            # Lighthouse CLI ausführen
            lighthouse_cmd = [
                "lighthouse",
                url,
                "--output=json",
                "--output-path=/tmp/lighthouse-report.json",
                "--chrome-flags=--headless",
                "--quiet"
            ]
            
            result = subprocess.run(lighthouse_cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                print(f"Lighthouse failed: {result.stderr}")
                return self._create_failed_result(url)
            
            # Lighthouse Report laden
            with open("/tmp/lighthouse-report.json", "r") as f:
                report = json.load(f)
            
            # Core Web Vitals extrahieren
            audits = report.get("audits", {})
            categories = report.get("categories", {})
            
            lcp = audits.get("largest-contentful-paint", {}).get("numericValue", 0) / 1000
            fid = audits.get("max-potential-fid", {}).get("numericValue", 0) / 1000
            cls = audits.get("cumulative-layout-shift", {}).get("numericValue", 0)
            fcp = audits.get("first-contentful-paint", {}).get("numericValue", 0) / 1000
            ttfb = audits.get("server-response-time", {}).get("numericValue", 0) / 1000
            
            performance_score = int(categories.get("performance", {}).get("score", 0) * 100)
            accessibility_score = int(categories.get("accessibility", {}).get("score", 0) * 100)
            
            # Targets prüfen
            passed_targets = (
                lcp <= targets.lcp_target and
                fid <= targets.fid_target and
                cls <= targets.cls_target
            )
            
            result = CoreWebVitalsResult(
                url=url,
                lcp=lcp,
                fid=fid,
                cls=cls,
                fcp=fcp,
                ttfb=ttfb,
                performance_score=performance_score,
                accessibility_score=accessibility_score,
                timestamp=datetime.now().isoformat(),
                passed_targets=passed_targets
            )
            
            status = "✅ PASS" if passed_targets else "❌ FAIL"
            print(f"{status} {url}: LCP={lcp:.2f}s, FID={fid:.3f}s, CLS={cls:.3f}, Score={performance_score}")
            
            return result
            
        except Exception as e:
            print(f"Lighthouse audit failed for {url}: {e}")
            return self._create_failed_result(url)
    
    def _create_failed_result(self, url: str) -> CoreWebVitalsResult:
        """Erstellt ein Failed Result"""
        return CoreWebVitalsResult(
            url=url,
            lcp=999.0,
            fid=999.0,
            cls=999.0,
            fcp=999.0,
            ttfb=999.0,
            performance_score=0,
            accessibility_score=0,
            timestamp=datetime.now().isoformat(),
            passed_targets=False
        )
    
    def test_core_web_vitals(self) -> List[CoreWebVitalsResult]:
        """Testet Core Web Vitals für alle Frontend-Seiten"""
        print("\n=== Testing Core Web Vitals ===")
        
        results = []
        
        for page in scenarios.FRONTEND_PAGES:
            full_url = f"{config.frontend_url}{page}"
            result = self.run_lighthouse_audit(full_url)
            results.append(result)
            self.results.append(result)
            
            # Kurze Pause zwischen Tests
            time.sleep(2)
        
        return results
    
    def analyze_bundle_size(self) -> BundleAnalysisResult:
        """Analysiert Bundle-Größe des Frontend-Builds"""
        print("\n=== Analyzing Bundle Size ===")
        
        try:
            # Frontend Build-Verzeichnis prüfen
            build_dir = "frontend/dist"
            if not os.path.exists(build_dir):
                print("Frontend build directory not found. Running build...")
                # Frontend Build ausführen
                build_result = subprocess.run(
                    ["npm", "run", "build"], 
                    cwd="frontend", 
                    capture_output=True, 
                    text=True,
                    timeout=300
                )
                
                if build_result.returncode != 0:
                    print(f"Frontend build failed: {build_result.stderr}")
                    return self._create_failed_bundle_result()
            
            # Bundle-Dateien analysieren
            total_size = 0
            js_size = 0
            css_size = 0
            largest_chunks = []
            
            for root, dirs, files in os.walk(build_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    
                    if file.endswith('.js'):
                        js_size += file_size
                        largest_chunks.append({
                            "name": file,
                            "size_kb": file_size / 1024,
                            "type": "js"
                        })
                    elif file.endswith('.css'):
                        css_size += file_size
                        largest_chunks.append({
                            "name": file,
                            "size_kb": file_size / 1024,
                            "type": "css"
                        })
            
            # Größte Chunks sortieren
            largest_chunks.sort(key=lambda x: x["size_kb"], reverse=True)
            largest_chunks = largest_chunks[:10]  # Top 10
            
            total_size_kb = total_size / 1024
            js_size_kb = js_size / 1024
            css_size_kb = css_size / 1024
            
            # Unused Code schätzen (vereinfacht)
            unused_code_percent = 0.0  # TODO: Implementierung mit Coverage API
            
            passed_size_target = total_size_kb <= targets.max_bundle_size
            
            result = BundleAnalysisResult(
                total_size_kb=total_size_kb,
                js_size_kb=js_size_kb,
                css_size_kb=css_size_kb,
                largest_chunks=largest_chunks,
                unused_code_percent=unused_code_percent,
                passed_size_target=passed_size_target
            )
            
            self.bundle_results.append(result)
            
            status = "✅ PASS" if passed_size_target else "❌ FAIL"
            print(f"{status} Bundle Size: {total_size_kb:.1f}KB (Target: {targets.max_bundle_size}KB)")
            print(f"  JS: {js_size_kb:.1f}KB, CSS: {css_size_kb:.1f}KB")
            
            return result
            
        except Exception as e:
            print(f"Bundle analysis failed: {e}")
            return self._create_failed_bundle_result()
    
    def _create_failed_bundle_result(self) -> BundleAnalysisResult:
        """Erstellt ein Failed Bundle Result"""
        return BundleAnalysisResult(
            total_size_kb=999999.0,
            js_size_kb=999999.0,
            css_size_kb=999999.0,
            largest_chunks=[],
            unused_code_percent=100.0,
            passed_size_target=False
        )
    
    def test_page_load_performance(self) -> List[Dict[str, Any]]:
        """Testet Page Load Performance mit Selenium"""
        print("\n=== Testing Page Load Performance ===")
        
        if not self.setup_chrome_driver():
            return []
        
        results = []
        
        try:
            for page in scenarios.FRONTEND_PAGES:
                full_url = f"{config.frontend_url}{page}"
                print(f"Testing page load: {page}")
                
                start_time = time.time()
                
                # Seite laden
                self.driver.get(full_url)
                
                # Warten bis Seite geladen
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                load_time = time.time() - start_time
                
                # Performance Timing via JavaScript
                timing = self.driver.execute_script("""
                    var timing = window.performance.timing;
                    return {
                        navigationStart: timing.navigationStart,
                        domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                        loadComplete: timing.loadEventEnd - timing.navigationStart,
                        firstPaint: performance.getEntriesByType('paint')[0] ? 
                                   performance.getEntriesByType('paint')[0].startTime : 0
                    };
                """)
                
                result = {
                    "url": full_url,
                    "page": page,
                    "load_time_seconds": load_time,
                    "dom_content_loaded_ms": timing.get("domContentLoaded", 0),
                    "load_complete_ms": timing.get("loadComplete", 0),
                    "first_paint_ms": timing.get("firstPaint", 0),
                    "timestamp": datetime.now().isoformat(),
                    "passed": load_time <= 3.0  # 3 Sekunden Ziel
                }
                
                results.append(result)
                
                status = "✅ PASS" if result["passed"] else "❌ FAIL"
                print(f"  {status} Load Time: {load_time:.2f}s")
                
                time.sleep(1)
            
        finally:
            self.cleanup()
        
        return results
    
    def check_frontend_targets(self) -> Dict[str, bool]:
        """Prüft Frontend Performance Targets"""
        if not self.results:
            return {"no_results": False}
        
        checks = {}
        
        for result in self.results:
            page_key = result.url.replace(config.frontend_url, "").replace("/", "_") or "home"
            checks[f"{page_key}_lcp"] = result.lcp <= targets.lcp_target
            checks[f"{page_key}_fid"] = result.fid <= targets.fid_target
            checks[f"{page_key}_cls"] = result.cls <= targets.cls_target
            checks[f"{page_key}_performance"] = result.performance_score >= 90
        
        if self.bundle_results:
            checks["bundle_size"] = self.bundle_results[0].passed_size_target
        
        return checks
    
    async def run_full_frontend_test_suite(self) -> Dict[str, Any]:
        """Führt alle Frontend Performance Tests aus"""
        print("=== Starting Frontend Performance Test Suite ===")
        
        start_time = time.time()
        
        try:
            # Core Web Vitals Tests
            cwv_results = self.test_core_web_vitals()
            
            # Bundle Size Analysis
            bundle_result = self.analyze_bundle_size()
            
            # Page Load Performance
            page_load_results = self.test_page_load_performance()
            
            end_time = time.time()
            
            # Performance Checks
            performance_checks = self.check_frontend_targets()
            
            # Ergebnisse zusammenfassen
            test_results = {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": end_time - start_time,
                "core_web_vitals": [asdict(r) for r in cwv_results],
                "bundle_analysis": asdict(bundle_result) if bundle_result else None,
                "page_load_performance": page_load_results,
                "performance_checks": performance_checks,
                "all_passed": all(performance_checks.values()),
                "summary": {
                    "pages_tested": len(cwv_results),
                    "avg_lcp": sum(r.lcp for r in cwv_results) / len(cwv_results) if cwv_results else 0,
                    "avg_performance_score": sum(r.performance_score for r in cwv_results) / len(cwv_results) if cwv_results else 0,
                    "bundle_size_kb": bundle_result.total_size_kb if bundle_result else 0
                }
            }
            
            # Report ausgeben
            self.print_summary_report(test_results)
            
            return test_results
            
        except Exception as e:
            print(f"Frontend performance test suite failed: {e}")
            return {"error": str(e)}
    
    def print_summary_report(self, results: Dict[str, Any]):
        """Druckt Summary Report"""
        print("\n" + "="*60)
        print("FRONTEND PERFORMANCE TEST SUMMARY")
        print("="*60)
        
        summary = results.get("summary", {})
        print(f"Pages Tested: {summary.get('pages_tested', 0)}")
        print(f"Average LCP: {summary.get('avg_lcp', 0):.2f}s (Target: ≤{targets.lcp_target}s)")
        print(f"Average Performance Score: {summary.get('avg_performance_score', 0):.0f}/100")
        print(f"Bundle Size: {summary.get('bundle_size_kb', 0):.1f}KB (Target: ≤{targets.max_bundle_size}KB)")
        
        print(f"\nCore Web Vitals Results:")
        for result in results.get("core_web_vitals", []):
            status = "✅ PASS" if result["passed_targets"] else "❌ FAIL"
            page = result["url"].replace(config.frontend_url, "") or "/"
            print(f"  {status} {page}: LCP={result['lcp']:.2f}s, FID={result['fid']:.3f}s, CLS={result['cls']:.3f}")
        
        checks = results.get("performance_checks", {})
        print(f"\nPerformance Targets:")
        for check_name, passed in checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {check_name}: {status}")
        
        overall_status = "✅ ALL TESTS PASSED" if results.get("all_passed", False) else "❌ SOME TESTS FAILED"
        print(f"\nOverall Result: {overall_status}")
        print("="*60)

async def main():
    """Hauptfunktion für direkten Test-Aufruf"""
    tester = FrontendPerformanceTester()
    results = await tester.run_full_frontend_test_suite()
    
    # Ergebnisse in Datei speichern
    os.makedirs("tests/performance/reports", exist_ok=True)
    with open("tests/performance/reports/frontend_performance_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: tests/performance/reports/frontend_performance_results.json")
    
    return results

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

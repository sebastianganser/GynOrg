#!/usr/bin/env python3
"""
Memory and Resource Monitoring
Überwachung von Memory Leaks, CPU Usage und Resource Leaks
"""

import os
import time
import json
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import config, targets

@dataclass
class ResourceSnapshot:
    """Resource Usage Snapshot"""
    timestamp: str
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    open_files: int
    threads: int

@dataclass
class ProcessMonitorResult:
    """Process Monitoring Ergebnis"""
    process_name: str
    pid: int
    duration_seconds: float
    snapshots: List[ResourceSnapshot]
    peak_memory_mb: float
    avg_memory_mb: float
    peak_cpu_percent: float
    avg_cpu_percent: float
    memory_leak_detected: bool
    memory_growth_rate_mb_per_min: float
    passed_targets: bool

@dataclass
class FrontendMemoryResult:
    """Frontend Memory Monitoring Ergebnis"""
    url: str
    duration_seconds: float
    initial_heap_mb: float
    peak_heap_mb: float
    final_heap_mb: float
    heap_growth_mb: float
    dom_nodes_initial: int
    dom_nodes_peak: int
    dom_nodes_final: int
    event_listeners_initial: int
    event_listeners_final: int
    memory_leak_detected: bool
    passed_targets: bool

class ResourceMonitor:
    """System Resource Monitor"""
    
    def __init__(self):
        self.monitoring = False
        self.snapshots: List[ResourceSnapshot] = []
        self.monitor_thread: Optional[threading.Thread] = None
        
    def start_monitoring(self, interval_seconds: float = 1.0):
        """Startet Resource Monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.snapshots = []
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval_seconds,)
        )
        self.monitor_thread.start()
        print(f"Resource monitoring started (interval: {interval_seconds}s)")
    
    def stop_monitoring(self):
        """Stoppt Resource Monitoring"""
        if not self.monitoring:
            return
        
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("Resource monitoring stopped")
    
    def _monitor_loop(self, interval: float):
        """Monitor Loop"""
        while self.monitoring:
            try:
                snapshot = self._take_snapshot()
                self.snapshots.append(snapshot)
                time.sleep(interval)
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                break
    
    def _take_snapshot(self) -> ResourceSnapshot:
        """Nimmt Resource Snapshot"""
        # CPU und Memory
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        disk_read_mb = disk_io.read_bytes / (1024 * 1024) if disk_io else 0
        disk_write_mb = disk_io.write_bytes / (1024 * 1024) if disk_io else 0
        
        # Network I/O
        net_io = psutil.net_io_counters()
        net_sent_mb = net_io.bytes_sent / (1024 * 1024) if net_io else 0
        net_recv_mb = net_io.bytes_recv / (1024 * 1024) if net_io else 0
        
        # Process Info
        current_process = psutil.Process()
        open_files = len(current_process.open_files())
        threads = current_process.num_threads()
        
        return ResourceSnapshot(
            timestamp=datetime.now().isoformat(),
            cpu_percent=cpu_percent,
            memory_mb=memory.used / (1024 * 1024),
            memory_percent=memory.percent,
            disk_io_read_mb=disk_read_mb,
            disk_io_write_mb=disk_write_mb,
            network_sent_mb=net_sent_mb,
            network_recv_mb=net_recv_mb,
            open_files=open_files,
            threads=threads
        )

class ProcessMonitor:
    """Process-spezifisches Monitoring"""
    
    def __init__(self):
        self.results: List[ProcessMonitorResult] = []
    
    def monitor_process_by_name(self, process_name: str, duration_seconds: float) -> ProcessMonitorResult:
        """Überwacht einen Prozess nach Name"""
        print(f"Monitoring process '{process_name}' for {duration_seconds}s...")
        
        # Prozess finden
        target_process = None
        for proc in psutil.process_iter(['pid', 'name']):
            if process_name.lower() in proc.info['name'].lower():
                target_process = psutil.Process(proc.info['pid'])
                break
        
        if not target_process:
            print(f"Process '{process_name}' not found")
            return self._create_failed_result(process_name, 0)
        
        return self._monitor_process(target_process, process_name, duration_seconds)
    
    def monitor_process_by_pid(self, pid: int, duration_seconds: float) -> ProcessMonitorResult:
        """Überwacht einen Prozess nach PID"""
        print(f"Monitoring process PID {pid} for {duration_seconds}s...")
        
        try:
            target_process = psutil.Process(pid)
            process_name = target_process.name()
            return self._monitor_process(target_process, process_name, duration_seconds)
        except psutil.NoSuchProcess:
            print(f"Process PID {pid} not found")
            return self._create_failed_result(f"PID-{pid}", pid)
    
    def _monitor_process(self, process: psutil.Process, name: str, duration: float) -> ProcessMonitorResult:
        """Überwacht einen spezifischen Prozess"""
        snapshots = []
        start_time = time.time()
        end_time = start_time + duration
        
        initial_memory = 0
        
        try:
            while time.time() < end_time:
                if not process.is_running():
                    print(f"Process {name} terminated during monitoring")
                    break
                
                # Memory Info
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / (1024 * 1024)
                
                if initial_memory == 0:
                    initial_memory = memory_mb
                
                # CPU Info
                cpu_percent = process.cpu_percent()
                
                # Process Details
                num_threads = process.num_threads()
                open_files = len(process.open_files())
                
                snapshot = ResourceSnapshot(
                    timestamp=datetime.now().isoformat(),
                    cpu_percent=cpu_percent,
                    memory_mb=memory_mb,
                    memory_percent=0,  # Nicht verfügbar für einzelnen Prozess
                    disk_io_read_mb=0,  # Vereinfacht
                    disk_io_write_mb=0,  # Vereinfacht
                    network_sent_mb=0,  # Vereinfacht
                    network_recv_mb=0,  # Vereinfacht
                    open_files=open_files,
                    threads=num_threads
                )
                
                snapshots.append(snapshot)
                time.sleep(1.0)
                
        except psutil.NoSuchProcess:
            print(f"Process {name} terminated during monitoring")
        except Exception as e:
            print(f"Error monitoring process {name}: {e}")
        
        actual_duration = time.time() - start_time
        
        # Analyse der Ergebnisse
        if not snapshots:
            return self._create_failed_result(name, process.pid)
        
        memory_values = [s.memory_mb for s in snapshots]
        cpu_values = [s.cpu_percent for s in snapshots]
        
        peak_memory = max(memory_values)
        avg_memory = sum(memory_values) / len(memory_values)
        peak_cpu = max(cpu_values)
        avg_cpu = sum(cpu_values) / len(cpu_values)
        
        # Memory Leak Detection
        final_memory = memory_values[-1]
        memory_growth = final_memory - initial_memory
        memory_growth_rate = (memory_growth / actual_duration) * 60  # MB per minute
        
        # Memory Leak wenn > 10MB/min Wachstum
        memory_leak_detected = memory_growth_rate > 10.0
        
        # Target Checks
        passed_targets = (
            peak_memory <= targets.max_memory_usage_mb and
            peak_cpu <= targets.max_cpu_usage_percent and
            not memory_leak_detected
        )
        
        result = ProcessMonitorResult(
            process_name=name,
            pid=process.pid,
            duration_seconds=actual_duration,
            snapshots=snapshots,
            peak_memory_mb=peak_memory,
            avg_memory_mb=avg_memory,
            peak_cpu_percent=peak_cpu,
            avg_cpu_percent=avg_cpu,
            memory_leak_detected=memory_leak_detected,
            memory_growth_rate_mb_per_min=memory_growth_rate,
            passed_targets=passed_targets
        )
        
        self.results.append(result)
        
        status = "✅ PASS" if passed_targets else "❌ FAIL"
        print(f"{status} {name}: Peak Memory={peak_memory:.1f}MB, Peak CPU={peak_cpu:.1f}%, Growth={memory_growth_rate:.2f}MB/min")
        
        return result
    
    def _create_failed_result(self, name: str, pid: int) -> ProcessMonitorResult:
        """Erstellt Failed Result"""
        return ProcessMonitorResult(
            process_name=name,
            pid=pid,
            duration_seconds=0,
            snapshots=[],
            peak_memory_mb=0,
            avg_memory_mb=0,
            peak_cpu_percent=0,
            avg_cpu_percent=0,
            memory_leak_detected=False,
            memory_growth_rate_mb_per_min=0,
            passed_targets=False
        )

class FrontendMemoryMonitor:
    """Frontend Memory Leak Detection"""
    
    def __init__(self):
        self.driver = None
        self.results: List[FrontendMemoryResult] = []
    
    def setup_driver(self) -> bool:
        """Setup Chrome Driver mit Memory Monitoring"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--enable-precise-memory-info")
            chrome_options.add_argument("--js-flags=--expose-gc")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            print("Chrome driver for memory monitoring setup successful")
            return True
            
        except Exception as e:
            print(f"Failed to setup Chrome driver: {e}")
            return False
    
    def cleanup(self):
        """Cleanup"""
        if self.driver:
            self.driver.quit()
    
    def monitor_page_memory(self, url: str, duration_seconds: float = 60) -> FrontendMemoryResult:
        """Überwacht Memory Usage einer Seite"""
        print(f"Monitoring memory for {url} for {duration_seconds}s...")
        
        if not self.setup_driver():
            return self._create_failed_frontend_result(url)
        
        try:
            # Seite laden
            self.driver.get(url)
            time.sleep(3)  # Warten bis geladen
            
            # Initial Memory Snapshot
            initial_memory = self._get_memory_info()
            initial_dom = self._get_dom_info()
            initial_listeners = self._get_event_listeners_count()
            
            start_time = time.time()
            end_time = start_time + duration_seconds
            
            peak_memory = initial_memory
            
            # Memory Monitoring Loop
            while time.time() < end_time:
                # Garbage Collection forcieren
                self.driver.execute_script("if (window.gc) { window.gc(); }")
                
                # Aktuelle Memory Info
                current_memory = self._get_memory_info()
                if current_memory > peak_memory:
                    peak_memory = current_memory
                
                # Simuliere User Interaktion
                self._simulate_user_interaction()
                
                time.sleep(2)
            
            # Final Memory Snapshot
            final_memory = self._get_memory_info()
            final_dom = self._get_dom_info()
            final_listeners = self._get_event_listeners_count()
            
            # Memory Leak Detection
            memory_growth = final_memory - initial_memory
            memory_leak_detected = memory_growth > 50  # > 50MB Wachstum
            
            # Target Check
            passed_targets = (
                peak_memory <= 200 and  # Max 200MB
                not memory_leak_detected and
                final_listeners <= initial_listeners * 1.1  # Max 10% Listener-Wachstum
            )
            
            result = FrontendMemoryResult(
                url=url,
                duration_seconds=time.time() - start_time,
                initial_heap_mb=initial_memory,
                peak_heap_mb=peak_memory,
                final_heap_mb=final_memory,
                heap_growth_mb=memory_growth,
                dom_nodes_initial=initial_dom,
                dom_nodes_peak=0,  # Vereinfacht
                dom_nodes_final=final_dom,
                event_listeners_initial=initial_listeners,
                event_listeners_final=final_listeners,
                memory_leak_detected=memory_leak_detected,
                passed_targets=passed_targets
            )
            
            self.results.append(result)
            
            status = "✅ PASS" if passed_targets else "❌ FAIL"
            print(f"{status} {url}: Memory Growth={memory_growth:.1f}MB, Peak={peak_memory:.1f}MB")
            
            return result
            
        except Exception as e:
            print(f"Frontend memory monitoring failed for {url}: {e}")
            return self._create_failed_frontend_result(url)
        
        finally:
            self.cleanup()
    
    def _get_memory_info(self) -> float:
        """Holt Memory Info via JavaScript"""
        try:
            memory_info = self.driver.execute_script("""
                if (performance.memory) {
                    return {
                        used: performance.memory.usedJSHeapSize,
                        total: performance.memory.totalJSHeapSize,
                        limit: performance.memory.jsHeapSizeLimit
                    };
                }
                return {used: 0, total: 0, limit: 0};
            """)
            
            return memory_info.get("used", 0) / (1024 * 1024)  # MB
            
        except Exception:
            return 0
    
    def _get_dom_info(self) -> int:
        """Holt DOM Node Count"""
        try:
            return self.driver.execute_script("return document.querySelectorAll('*').length;")
        except Exception:
            return 0
    
    def _get_event_listeners_count(self) -> int:
        """Schätzt Event Listener Count (vereinfacht)"""
        try:
            # Vereinfachte Schätzung basierend auf Elementen mit Event Attributen
            return self.driver.execute_script("""
                var count = 0;
                var elements = document.querySelectorAll('*');
                for (var i = 0; i < elements.length; i++) {
                    var attrs = elements[i].attributes;
                    for (var j = 0; j < attrs.length; j++) {
                        if (attrs[j].name.startsWith('on')) {
                            count++;
                        }
                    }
                }
                return count;
            """)
        except Exception:
            return 0
    
    def _simulate_user_interaction(self):
        """Simuliert User Interaktion"""
        try:
            # Klicks auf verschiedene Elemente
            buttons = self.driver.find_elements("css selector", "button, a, input")
            if buttons:
                buttons[0].click()
                time.sleep(0.5)
        except Exception:
            pass
    
    def _create_failed_frontend_result(self, url: str) -> FrontendMemoryResult:
        """Erstellt Failed Frontend Result"""
        return FrontendMemoryResult(
            url=url,
            duration_seconds=0,
            initial_heap_mb=0,
            peak_heap_mb=0,
            final_heap_mb=0,
            heap_growth_mb=0,
            dom_nodes_initial=0,
            dom_nodes_peak=0,
            dom_nodes_final=0,
            event_listeners_initial=0,
            event_listeners_final=0,
            memory_leak_detected=True,
            passed_targets=False
        )

class MemoryTestSuite:
    """Complete Memory & Resource Test Suite"""
    
    def __init__(self):
        self.resource_monitor = ResourceMonitor()
        self.process_monitor = ProcessMonitor()
        self.frontend_monitor = FrontendMemoryMonitor()
    
    async def run_backend_memory_tests(self, duration_seconds: float = 300) -> List[ProcessMonitorResult]:
        """Führt Backend Memory Tests aus"""
        print("\n=== Backend Memory & Resource Tests ===")
        
        results = []
        
        # Python Backend Process
        python_result = self.process_monitor.monitor_process_by_name("python", duration_seconds)
        results.append(python_result)
        
        # Uvicorn Process (falls separat)
        uvicorn_result = self.process_monitor.monitor_process_by_name("uvicorn", duration_seconds)
        if uvicorn_result.snapshots:  # Nur wenn gefunden
            results.append(uvicorn_result)
        
        return results
    
    async def run_frontend_memory_tests(self) -> List[FrontendMemoryResult]:
        """Führt Frontend Memory Tests aus"""
        print("\n=== Frontend Memory Tests ===")
        
        results = []
        
        # Test verschiedene Seiten
        test_pages = [
            f"{config.frontend_url}/",
            f"{config.frontend_url}/employees"
        ]
        
        for page_url in test_pages:
            result = self.frontend_monitor.monitor_page_memory(page_url, 120)  # 2 Min
            results.append(result)
        
        return results
    
    async def run_system_resource_monitoring(self, duration_seconds: float = 300) -> List[ResourceSnapshot]:
        """Führt System Resource Monitoring aus"""
        print(f"\n=== System Resource Monitoring ({duration_seconds}s) ===")
        
        self.resource_monitor.start_monitoring(1.0)
        
        # Load Testing während Monitoring
        await self._run_concurrent_load()
        
        # Warten bis Ende
        time.sleep(duration_seconds)
        
        self.resource_monitor.stop_monitoring()
        
        return self.resource_monitor.snapshots
    
    async def _run_concurrent_load(self):
        """Führt Load aus während Resource Monitoring"""
        try:
            # Einfache API Calls
            for _ in range(10):
                requests.get(f"{config.base_url}/api/v1/federal-states", timeout=5)
                time.sleep(1)
        except Exception as e:
            print(f"Concurrent load failed: {e}")
    
    async def run_full_memory_test_suite(self) -> Dict[str, Any]:
        """Führt alle Memory & Resource Tests aus"""
        print("=== Starting Memory & Resource Test Suite ===")
        
        start_time = time.time()
        
        try:
            # Backend Memory Tests
            backend_results = await self.run_backend_memory_tests(180)  # 3 Min
            
            # Frontend Memory Tests
            frontend_results = await self.run_frontend_memory_tests()
            
            # System Resource Monitoring
            system_snapshots = await self.run_system_resource_monitoring(120)  # 2 Min
            
            end_time = time.time()
            
            # Analyse der Ergebnisse
            all_backend_passed = all(r.passed_targets for r in backend_results)
            all_frontend_passed = all(r.passed_targets for r in frontend_results)
            
            # System Resource Analyse
            if system_snapshots:
                peak_memory = max(s.memory_mb for s in system_snapshots)
                avg_cpu = sum(s.cpu_percent for s in system_snapshots) / len(system_snapshots)
                system_passed = peak_memory <= targets.max_memory_usage_mb and avg_cpu <= targets.max_cpu_usage_percent
            else:
                peak_memory = 0
                avg_cpu = 0
                system_passed = False
            
            test_results = {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": end_time - start_time,
                "backend_memory_tests": [asdict(r) for r in backend_results],
                "frontend_memory_tests": [asdict(r) for r in frontend_results],
                "system_resource_snapshots": [asdict(s) for s in system_snapshots[-10:]],  # Letzte 10
                "summary": {
                    "backend_processes_tested": len(backend_results),
                    "frontend_pages_tested": len(frontend_results),
                    "system_peak_memory_mb": peak_memory,
                    "system_avg_cpu_percent": avg_cpu,
                    "backend_passed": all_backend_passed,
                    "frontend_passed": all_frontend_passed,
                    "system_passed": system_passed,
                    "all_passed": all_backend_passed and all_frontend_passed and system_passed
                }
            }
            
            # Report ausgeben
            self.print_summary_report(test_results)
            
            return test_results
            
        except Exception as e:
            print(f"Memory test suite failed: {e}")
            return {"error": str(e)}
    
    def print_summary_report(self, results: Dict[str, Any]):
        """Druckt Summary Report"""
        print("\n" + "="*60)
        print("MEMORY & RESOURCE TEST SUMMARY")
        print("="*60)
        
        summary = results.get("summary", {})
        
        print(f"Backend Processes: {summary.get('backend_processes_tested', 0)}")
        print(f"Frontend Pages: {summary.get('frontend_pages_tested', 0)}")
        print(f"System Peak Memory: {summary.get('system_peak_memory_mb', 0):.1f}MB")
        print(f"System Avg CPU: {summary.get('system_avg_cpu_percent', 0):.1f}%")
        
        print(f"\nBackend Memory Results:")
        for result in results.get("backend_memory_tests", []):
            status = "✅ PASS" if result["passed_targets"] else "❌ FAIL"
            leak_status = "🔴 LEAK" if result["memory_leak_detected"] else "✅ OK"
            print(f"  {status} {result['process_name']}: Peak={result['peak_memory_mb']:.1f}MB, {leak_status}")
        
        print(f"\nFrontend Memory Results:")
        for result in results.get("frontend_memory_tests", []):
            status = "✅ PASS" if result["passed_targets"] else "❌ FAIL"
            leak_status = "🔴 LEAK" if result["memory_leak_detected"] else "✅ OK"
            print(f"  {status} {result['url']}: Growth={result['heap_growth_mb']:.1f}MB, {leak_status}")
        
        backend_status = "✅ PASS" if summary.get("backend_passed", False) else "❌ FAIL"
        frontend_status = "✅ PASS" if summary.get("frontend_passed", False) else "❌ FAIL"
        system_status = "✅ PASS" if summary.get("system_passed", False) else "❌ FAIL"
        
        print(f"\nTarget Results:")
        print(f"  Backend Memory: {backend_status}")
        print(f"  Frontend Memory: {frontend_status}")
        print(f"  System Resources: {system_status}")
        
        overall_status = "✅ ALL TESTS PASSED" if summary.get("all_passed", False) else "❌ SOME TESTS FAILED"
        print(f"\nOverall Result: {overall_status}")
        print("="*60)

async def main():
    """Hauptfunktion für direkten Test-Aufruf"""
    suite = MemoryTestSuite()
    results = await suite.run_full_memory_test_suite()
    
    # Ergebnisse speichern
    os.makedirs("tests/performance/reports", exist_ok=True)
    with open("tests/performance/reports/memory_monitoring_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: tests/performance/reports/memory_monitoring_results.json")
    
    return results

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

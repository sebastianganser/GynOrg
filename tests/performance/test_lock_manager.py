#!/usr/bin/env python3
"""
Test Lock Manager
Verhindert parallele Ausführung von Performance Tests
"""

import os
import time
import psutil
from pathlib import Path
from typing import Optional
from datetime import datetime

class TestLockManager:
    """Verwaltet Locks für Performance Tests um parallele Ausführung zu verhindern"""
    
    def __init__(self, lock_name: str = "performance_test"):
        self.lock_name = lock_name
        # Absoluten Pfad verwenden basierend auf der aktuellen Datei
        script_dir = Path(__file__).parent
        self.lock_dir = script_dir / "logs"
        self.lock_file = self.lock_dir / f"{lock_name}.lock"
        self.pid_file = self.lock_dir / f"{lock_name}.pid"
        self.current_pid = os.getpid()
        
        # Lock-Verzeichnis erstellen
        self.lock_dir.mkdir(exist_ok=True)
    
    def acquire_lock(self, timeout: int = 5) -> bool:
        """
        Versucht Lock zu akquirieren
        
        Args:
            timeout: Maximale Wartezeit in Sekunden
            
        Returns:
            True wenn Lock erfolgreich akquiriert, False sonst
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self._try_acquire_lock():
                return True
            
            # Prüfen ob der blockierende Prozess noch läuft
            if self._cleanup_stale_locks():
                continue  # Versuche erneut nach Cleanup
            
            print(f"Waiting for lock... ({int(time.time() - start_time)}s)")
            time.sleep(1)
        
        return False
    
    def _try_acquire_lock(self) -> bool:
        """Versucht Lock-Datei zu erstellen"""
        try:
            if self.lock_file.exists():
                return False
            
            # Lock-Datei mit Timestamp und PID erstellen
            lock_info = {
                "pid": self.current_pid,
                "timestamp": datetime.now().isoformat(),
                "process_name": "performance_test"
            }
            
            # Atomisches Schreiben über temporäre Datei
            temp_file = self.lock_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                f.write(f"PID: {lock_info['pid']}\n")
                f.write(f"Started: {lock_info['timestamp']}\n")
                f.write(f"Process: {lock_info['process_name']}\n")
            
            # Atomisches Rename
            temp_file.rename(self.lock_file)
            
            # PID-Datei erstellen
            with open(self.pid_file, 'w') as f:
                f.write(str(self.current_pid))
            
            print(f"✅ Lock acquired by PID {self.current_pid}")
            return True
            
        except Exception as e:
            print(f"Error acquiring lock: {e}")
            return False
    
    def _cleanup_stale_locks(self) -> bool:
        """
        Bereinigt verwaiste Lock-Dateien von nicht mehr laufenden Prozessen
        
        Returns:
            True wenn ein stale lock entfernt wurde, False sonst
        """
        try:
            if not self.pid_file.exists():
                # Kein PID-File, aber Lock existiert - wahrscheinlich stale
                if self.lock_file.exists():
                    print("Removing stale lock (no PID file)")
                    self.lock_file.unlink()
                    return True
                return False
            
            # PID aus Datei lesen
            with open(self.pid_file, 'r') as f:
                old_pid = int(f.read().strip())
            
            # Prüfen ob Prozess noch läuft
            if self._is_process_running(old_pid):
                # Prozess läuft noch - kein stale lock
                return False
            
            # Prozess läuft nicht mehr - Lock entfernen
            print(f"Removing stale lock from dead process {old_pid}")
            self.release_lock()
            return True
            
        except Exception as e:
            print(f"Error checking for stale locks: {e}")
            # Im Zweifel Lock entfernen
            if self.lock_file.exists():
                self.lock_file.unlink()
            if self.pid_file.exists():
                self.pid_file.unlink()
            return True
    
    def _is_process_running(self, pid: int) -> bool:
        """Prüft ob ein Prozess mit der gegebenen PID läuft"""
        try:
            process = psutil.Process(pid)
            # Zusätzlich prüfen ob es ein Python-Prozess ist
            if 'python' in process.name().lower():
                return True
            return False
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    def release_lock(self) -> bool:
        """
        Gibt den Lock frei
        
        Returns:
            True wenn erfolgreich freigegeben, False sonst
        """
        try:
            success = True
            
            if self.lock_file.exists():
                self.lock_file.unlink()
                print(f"✅ Lock released by PID {self.current_pid}")
            
            if self.pid_file.exists():
                self.pid_file.unlink()
            
            return success
            
        except Exception as e:
            print(f"Error releasing lock: {e}")
            return False
    
    def is_locked(self) -> bool:
        """Prüft ob aktuell ein Lock aktiv ist"""
        if not self.lock_file.exists():
            return False
        
        # Prüfen ob Lock von einem laufenden Prozess stammt
        if self._cleanup_stale_locks():
            return False  # War ein stale lock, jetzt frei
        
        return True
    
    def get_lock_info(self) -> Optional[dict]:
        """
        Gibt Informationen über den aktuellen Lock zurück
        
        Returns:
            Dict mit Lock-Informationen oder None wenn kein Lock
        """
        if not self.lock_file.exists():
            return None
        
        try:
            with open(self.lock_file, 'r') as f:
                content = f.read()
            
            info = {}
            for line in content.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip().lower()] = value.strip()
            
            return info
            
        except Exception as e:
            print(f"Error reading lock info: {e}")
            return None
    
    def force_release(self) -> bool:
        """
        Forciert die Freigabe des Locks (Notfall-Funktion)
        
        Returns:
            True wenn erfolgreich, False sonst
        """
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
                print("🔓 Lock forcibly released")
            
            if self.pid_file.exists():
                self.pid_file.unlink()
            
            return True
            
        except Exception as e:
            print(f"Error force-releasing lock: {e}")
            return False

# Context Manager für automatisches Lock-Management
class TestLock:
    """Context Manager für automatisches Lock-Management"""
    
    def __init__(self, lock_name: str = "performance_test", timeout: int = 10):
        self.manager = TestLockManager(lock_name)
        self.timeout = timeout
        self.acquired = False
    
    def __enter__(self):
        print(f"🔒 Attempting to acquire test lock...")
        
        if self.manager.is_locked():
            lock_info = self.manager.get_lock_info()
            if lock_info:
                print(f"❌ Test already running (PID: {lock_info.get('pid', 'unknown')}, Started: {lock_info.get('started', 'unknown')})")
            else:
                print("❌ Test already running (unknown process)")
            
            print("\nOptions:")
            print("1. Wait for current test to finish")
            print("2. Force release lock (use with caution)")
            print("3. Exit")
            
            raise RuntimeError("Another performance test is already running. Please wait or force-release the lock.")
        
        self.acquired = self.manager.acquire_lock(self.timeout)
        
        if not self.acquired:
            raise RuntimeError(f"Could not acquire test lock within {self.timeout} seconds")
        
        return self.manager
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.acquired:
            self.manager.release_lock()

# Utility-Funktionen
def check_running_tests() -> bool:
    """Prüft ob aktuell Performance Tests laufen"""
    manager = TestLockManager()
    return manager.is_locked()

def force_cleanup_locks():
    """Bereinigt alle Lock-Dateien (Notfall-Funktion)"""
    manager = TestLockManager()
    return manager.force_release()

def get_test_status() -> dict:
    """Gibt Status aller Test-Locks zurück"""
    manager = TestLockManager()
    
    status = {
        "locked": manager.is_locked(),
        "lock_info": manager.get_lock_info() if manager.is_locked() else None,
        "lock_file_exists": manager.lock_file.exists(),
        "pid_file_exists": manager.pid_file.exists()
    }
    
    return status

if __name__ == "__main__":
    # Test-Funktionalität
    print("Testing Lock Manager...")
    
    # Status anzeigen
    status = get_test_status()
    print(f"Current status: {status}")
    
    # Lock testen
    try:
        with TestLock("test_lock", timeout=5) as lock:
            print("Lock acquired successfully!")
            time.sleep(2)
            print("Releasing lock...")
    except RuntimeError as e:
        print(f"Lock test failed: {e}")
    
    print("Lock test completed.")

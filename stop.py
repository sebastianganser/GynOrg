#!/usr/bin/env python3
"""
GynOrg Development Server Stopper
Stoppt alle laufenden Backend (FastAPI) und Frontend (Vite) Server
"""

import os
import sys
import time
import signal
import subprocess
import platform
from typing import List, Dict, Optional


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class ServerStopper:
    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        self.stopped_processes = []
        
    def print_colored(self, message: str, color: str = Colors.OKBLUE):
        """Print colored message to console"""
        print(f"{color}{message}{Colors.ENDC}")
    
    def find_processes_by_port(self, port: int) -> List[Dict]:
        """Find processes using a specific port"""
        processes = []
        try:
            if self.is_windows:
                # Windows: Use netstat to find processes
                cmd = ['netstat', '-ano']
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and ('LISTENING' in line or 'ABH?REN' in line):
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            try:
                                # Get process name
                                tasklist_cmd = ['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV']
                                tasklist_result = subprocess.run(tasklist_cmd, capture_output=True, text=True)
                                if tasklist_result.returncode == 0:
                                    lines = tasklist_result.stdout.strip().split('\n')
                                    if len(lines) > 1:
                                        process_name = lines[1].split(',')[0].strip('"')
                                        processes.append({
                                            'pid': int(pid),
                                            'name': process_name,
                                            'port': port
                                        })
                            except (ValueError, IndexError):
                                continue
            else:
                # Unix/Linux/macOS: Use lsof to find processes
                cmd = ['lsof', '-ti', f':{port}']
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    for pid_str in result.stdout.strip().split('\n'):
                        if pid_str:
                            try:
                                pid = int(pid_str)
                                # Get process name
                                ps_cmd = ['ps', '-p', str(pid), '-o', 'comm=']
                                ps_result = subprocess.run(ps_cmd, capture_output=True, text=True)
                                process_name = ps_result.stdout.strip() if ps_result.returncode == 0 else 'unknown'
                                
                                processes.append({
                                    'pid': pid,
                                    'name': process_name,
                                    'port': port
                                })
                            except ValueError:
                                continue
                                
        except FileNotFoundError:
            self.print_colored(f"❌ Benötigte Tools nicht verfügbar für Port-Check", Colors.FAIL)
        except Exception as e:
            self.print_colored(f"❌ Fehler beim Suchen von Prozessen auf Port {port}: {e}", Colors.FAIL)
            
        return processes
    
    def find_processes_by_name(self, name_patterns: List[str]) -> List[Dict]:
        """Find processes by name patterns"""
        processes = []
        try:
            if self.is_windows:
                # Windows: Use tasklist
                cmd = ['tasklist', '/FO', 'CSV']
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    for line in lines:
                        parts = line.split(',')
                        if len(parts) >= 2:
                            process_name = parts[0].strip('"').lower()
                            pid_str = parts[1].strip('"')
                            
                            for pattern in name_patterns:
                                if pattern.lower() in process_name:
                                    try:
                                        processes.append({
                                            'pid': int(pid_str),
                                            'name': parts[0].strip('"'),
                                            'pattern': pattern
                                        })
                                    except ValueError:
                                        continue
            else:
                # Unix/Linux/macOS: Use ps and grep
                for pattern in name_patterns:
                    cmd = ['pgrep', '-f', pattern]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        for pid_str in result.stdout.strip().split('\n'):
                            if pid_str:
                                try:
                                    pid = int(pid_str)
                                    # Get process command
                                    ps_cmd = ['ps', '-p', str(pid), '-o', 'args=']
                                    ps_result = subprocess.run(ps_cmd, capture_output=True, text=True)
                                    process_cmd = ps_result.stdout.strip() if ps_result.returncode == 0 else 'unknown'
                                    
                                    processes.append({
                                        'pid': pid,
                                        'name': process_cmd,
                                        'pattern': pattern
                                    })
                                except ValueError:
                                    continue
                                    
        except FileNotFoundError:
            self.print_colored(f"❌ Benötigte Tools nicht verfügbar für Prozess-Suche", Colors.FAIL)
        except Exception as e:
            self.print_colored(f"❌ Fehler beim Suchen von Prozessen: {e}", Colors.FAIL)
            
        return processes
    
    def kill_process(self, pid: int, name: str, graceful: bool = True) -> bool:
        """Kill a process by PID"""
        try:
            if self.is_windows:
                if graceful:
                    # Try graceful termination first
                    cmd = ['taskkill', '/PID', str(pid)]
                else:
                    # Force kill
                    cmd = ['taskkill', '/F', '/PID', str(pid)]
            else:
                if graceful:
                    # Send SIGTERM first
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(2)
                    
                    # Check if process is still running
                    try:
                        os.kill(pid, 0)  # Check if process exists
                        # Still running, force kill
                        os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        # Process already terminated
                        pass
                    return True
                else:
                    # Force kill
                    os.kill(pid, signal.SIGKILL)
                    return True
            
            if self.is_windows:
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.returncode == 0
                
        except ProcessLookupError:
            # Process already terminated
            return True
        except PermissionError:
            self.print_colored(f"❌ Keine Berechtigung um Prozess {pid} ({name}) zu beenden", Colors.FAIL)
            return False
        except Exception as e:
            self.print_colored(f"❌ Fehler beim Beenden von Prozess {pid} ({name}): {e}", Colors.FAIL)
            return False
            
        return True
    
    def force_kill_port_8000(self) -> int:
        """Aggressively kill any process using port 8000"""
        self.print_colored("🔧 Aggressive Suche nach Port 8000 Prozessen...", Colors.WARNING)
        
        stopped_count = 0
        try:
            # Use netstat to find all processes on port 8000
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, shell=True)
            lines = result.stdout.split('\n')
            
            pids_to_kill = set()  # Use set to avoid duplicates
            for line in lines:
                if ':8000' in line and ('LISTENING' in line or 'ABH?REN' in line or 'ABHÖREN' in line):
                    parts = line.split()
                    if len(parts) >= 5:
                        pid_str = parts[-1]
                        if pid_str.isdigit():
                            pids_to_kill.add(int(pid_str))
            
            if pids_to_kill:
                self.print_colored(f"🎯 Gefundene PIDs für Port 8000: {', '.join(map(str, pids_to_kill))}", Colors.WARNING)
                for pid in pids_to_kill:
                    try:
                        # Force kill without mercy
                        if self.is_windows:
                            subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True, capture_output=True)
                        else:
                            os.kill(pid, signal.SIGKILL)
                        
                        self.print_colored(f"✅ PID {pid} erfolgreich beendet", Colors.OKGREEN)
                        self.stopped_processes.append(f"Port 8000 Prozess (PID: {pid})")
                        stopped_count += 1
                    except (subprocess.CalledProcessError, ProcessLookupError, PermissionError) as e:
                        self.print_colored(f"⚠️  Konnte PID {pid} nicht beenden: {e}", Colors.WARNING)
            else:
                self.print_colored("ℹ️  Keine Prozesse auf Port 8000 gefunden", Colors.OKCYAN)
                
        except Exception as e:
            self.print_colored(f"❌ Fehler beim aggressiven Port-Kill: {e}", Colors.FAIL)
            
        return stopped_count

    def stop_backend_servers(self) -> int:
        """Stop all backend servers (uvicorn processes)"""
        self.print_colored("🔍 Suche Backend Server (uvicorn)...", Colors.OKCYAN)
        
        stopped_count = 0
        
        # First try aggressive port 8000 cleanup
        stopped_count += self.force_kill_port_8000()
        
        # Find by port 8000 (in case some survived)
        port_processes = self.find_processes_by_port(8000)
        for proc in port_processes:
            self.print_colored(f"🛑 Stoppe Backend Server: {proc['name']} (PID: {proc['pid']}, Port: {proc['port']})", Colors.WARNING)
            if self.kill_process(proc['pid'], proc['name']):
                self.stopped_processes.append(f"Backend Server (PID: {proc['pid']})")
                stopped_count += 1
                self.print_colored(f"✅ Backend Server gestoppt", Colors.OKGREEN)
            else:
                self.print_colored(f"❌ Konnte Backend Server nicht stoppen", Colors.FAIL)
        
        # Find by process name patterns
        uvicorn_patterns = ['uvicorn', 'main:app', 'fastapi']
        name_processes = self.find_processes_by_name(uvicorn_patterns)
        
        for proc in name_processes:
            # Avoid duplicates from port search
            if not any(p['pid'] == proc['pid'] for p in port_processes):
                self.print_colored(f"🛑 Stoppe Backend Prozess: {proc['name']} (PID: {proc['pid']})", Colors.WARNING)
                if self.kill_process(proc['pid'], proc['name']):
                    self.stopped_processes.append(f"Backend Prozess (PID: {proc['pid']})")
                    stopped_count += 1
                    self.print_colored(f"✅ Backend Prozess gestoppt", Colors.OKGREEN)
                else:
                    self.print_colored(f"❌ Konnte Backend Prozess nicht stoppen", Colors.FAIL)
        
        if stopped_count == 0:
            self.print_colored("ℹ️  Keine Backend Server gefunden", Colors.OKCYAN)
            
        return stopped_count
    
    def stop_frontend_servers(self) -> int:
        """Stop all frontend servers (npm/vite processes)"""
        self.print_colored("🔍 Suche Frontend Server (Vite/npm)...", Colors.OKCYAN)
        
        stopped_count = 0
        
        # Find by port 5173 (Vite default)
        port_processes = self.find_processes_by_port(5173)
        for proc in port_processes:
            self.print_colored(f"🛑 Stoppe Frontend Server: {proc['name']} (PID: {proc['pid']}, Port: {proc['port']})", Colors.WARNING)
            if self.kill_process(proc['pid'], proc['name']):
                self.stopped_processes.append(f"Frontend Server (PID: {proc['pid']})")
                stopped_count += 1
                self.print_colored(f"✅ Frontend Server gestoppt", Colors.OKGREEN)
            else:
                self.print_colored(f"❌ Konnte Frontend Server nicht stoppen", Colors.FAIL)
        
        # Find by process name patterns
        frontend_patterns = ['vite', 'npm run dev', 'node.*vite', 'gynorg-frontend']
        name_processes = self.find_processes_by_name(frontend_patterns)
        
        for proc in name_processes:
            # Avoid duplicates from port search
            if not any(p['pid'] == proc['pid'] for p in port_processes):
                self.print_colored(f"🛑 Stoppe Frontend Prozess: {proc['name']} (PID: {proc['pid']})", Colors.WARNING)
                if self.kill_process(proc['pid'], proc['name']):
                    self.stopped_processes.append(f"Frontend Prozess (PID: {proc['pid']})")
                    stopped_count += 1
                    self.print_colored(f"✅ Frontend Prozess gestoppt", Colors.OKGREEN)
                else:
                    self.print_colored(f"❌ Konnte Frontend Prozess nicht stoppen", Colors.FAIL)
        
        if stopped_count == 0:
            self.print_colored("ℹ️  Keine Frontend Server gefunden", Colors.OKCYAN)
            
        return stopped_count
    
    def stop_all_servers(self):
        """Stop all development servers"""
        self.print_colored("=" * 60, Colors.HEADER)
        self.print_colored("🛑 GynOrg Development Server Stopper", Colors.HEADER)
        self.print_colored("=" * 60, Colors.HEADER)
        
        total_stopped = 0
        
        # Stop backend servers
        backend_stopped = self.stop_backend_servers()
        total_stopped += backend_stopped
        
        print()  # Empty line for better readability
        
        # Stop frontend servers
        frontend_stopped = self.stop_frontend_servers()
        total_stopped += frontend_stopped
        
        # Summary
        self.print_colored("\n" + "=" * 60, Colors.HEADER)
        if total_stopped > 0:
            self.print_colored(f"✅ {total_stopped} Server/Prozesse erfolgreich gestoppt:", Colors.OKGREEN)
            for process in self.stopped_processes:
                self.print_colored(f"   • {process}", Colors.OKGREEN)
        else:
            self.print_colored("ℹ️  Keine laufenden GynOrg Server gefunden", Colors.OKCYAN)
            self.print_colored("💡 Möglicherweise sind bereits alle Server gestoppt", Colors.OKCYAN)
        
        self.print_colored("=" * 60, Colors.HEADER)
        
        # Additional cleanup suggestions
        if total_stopped == 0:
            self.print_colored("\n💡 Zusätzliche Cleanup-Optionen:", Colors.WARNING)
            if self.is_windows:
                self.print_colored("   • Alle Node.js Prozesse: taskkill /F /IM node.exe", Colors.WARNING)
                self.print_colored("   • Alle Python Prozesse: taskkill /F /IM python.exe", Colors.WARNING)
            else:
                self.print_colored("   • Alle Node.js Prozesse: pkill -f node", Colors.WARNING)
                self.print_colored("   • Alle Python Prozesse: pkill -f python", Colors.WARNING)
            self.print_colored("   ⚠️  Vorsicht: Diese Befehle stoppen ALLE entsprechenden Prozesse!", Colors.FAIL)


def main():
    """Main entry point"""
    stopper = ServerStopper()
    
    try:
        stopper.stop_all_servers()
    except KeyboardInterrupt:
        stopper.print_colored("\n🛑 Abgebrochen durch Benutzer", Colors.WARNING)
        sys.exit(1)
    except Exception as e:
        stopper.print_colored(f"❌ Unerwarteter Fehler: {e}", Colors.FAIL)
        sys.exit(1)


if __name__ == "__main__":
    main()

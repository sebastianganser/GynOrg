#!/usr/bin/env python3
"""
GynOrg Development Server Starter
Startet Backend (FastAPI) und Frontend (Vite) Server parallel
"""

import os
import sys
import time
import signal
import socket
import subprocess
import threading
from pathlib import Path
from typing import Optional, List


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


class ServerManager:
    def __init__(self):
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        self.running = True
        
    def print_colored(self, message: str, color: str = Colors.OKBLUE):
        """Print colored message to console"""
        print(f"{color}{message}{Colors.ENDC}")
    
    def _free_port(self, port: int) -> bool:
        """Try to free a port by killing the process using it (aggressive method)"""
        try:
            freed_any = False
            
            # Windows: Use netstat to find PID and taskkill to stop it
            if os.name == 'nt':
                # Find process using the port
                result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, shell=True)
                lines = result.stdout.split('\n')
                
                pids_to_kill = set()  # Use set to avoid duplicates
                for line in lines:
                    if f':{port}' in line and ('LISTENING' in line or 'ABH?REN' in line or 'ABHÖREN' in line):
                        parts = line.split()
                        if len(parts) >= 5:
                            pid_str = parts[-1]
                            if pid_str.isdigit():
                                pids_to_kill.add(int(pid_str))
                
                if pids_to_kill:
                    self.print_colored(f"🎯 Gefundene PIDs für Port {port}: {', '.join(map(str, pids_to_kill))}", Colors.WARNING)
                    for pid in pids_to_kill:
                        try:
                            # Force kill without mercy
                            subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=True, capture_output=True)
                            self.print_colored(f"✅ PID {pid} erfolgreich beendet", Colors.OKGREEN)
                            freed_any = True
                        except (subprocess.CalledProcessError, ProcessLookupError, PermissionError) as e:
                            self.print_colored(f"⚠️  Konnte PID {pid} nicht beenden: {e}", Colors.WARNING)
                    
                    if freed_any:
                        time.sleep(2)  # Wait longer for the port to be freed
                        return True
            else:
                # Unix/Linux/macOS: Use lsof and kill
                cmd = ['lsof', '-ti', f':{port}']
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid.strip():
                            self.print_colored(f"🔍 Gefundener Prozess PID {pid} auf Port {port}", Colors.OKCYAN)
                            kill_cmd = ['kill', '-9', pid.strip()]
                            kill_result = subprocess.run(kill_cmd, capture_output=True, text=True)
                            if kill_result.returncode == 0:
                                freed_any = True
                                self.print_colored(f"✅ PID {pid} erfolgreich beendet", Colors.OKGREEN)
                            else:
                                self.print_colored(f"⚠️  Konnte Prozess {pid} nicht beenden", Colors.WARNING)
                    
                    if freed_any:
                        time.sleep(2)  # Wait for the port to be freed
                        return True
            
            return freed_any
            
        except Exception as e:
            self.print_colored(f"❌ Fehler beim Freigeben von Port {port}: {e}", Colors.FAIL)
            return False
        
    def check_port(self, port: int, service_name: str) -> bool:
        """Check if a port is already in use and try to free it"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                if result == 0:
                    self.print_colored(f"⚠️  Port {port} ({service_name}) ist bereits belegt!", Colors.WARNING)
                    self.print_colored(f"🔧 Versuche Port {port} freizugeben...", Colors.OKCYAN)
                    
                    # Try to free the port
                    if self._free_port(port):
                        self.print_colored(f"✅ Port {port} erfolgreich freigegeben", Colors.OKGREEN)
                        return True
                    else:
                        self.print_colored(f"❌ Konnte Port {port} nicht freigeben", Colors.FAIL)
                        return False
                return True
        except Exception as e:
            self.print_colored(f"❌ Fehler beim Port-Check für {service_name}: {e}", Colors.FAIL)
            return False
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are available"""
        self.print_colored("🔍 Überprüfe Dependencies...", Colors.OKCYAN)
        
        # Check Python and uvicorn
        try:
            result = subprocess.run(['python', '-c', 'import uvicorn'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.print_colored("❌ uvicorn nicht gefunden. Installiere Backend-Dependencies:", Colors.FAIL)
                self.print_colored("   cd backend && pip install -r requirements.txt", Colors.WARNING)
                return False
        except FileNotFoundError:
            self.print_colored("❌ Python nicht gefunden!", Colors.FAIL)
            return False
            
        # Check Node.js and npm (Windows-compatible)
        try:
            # Try different ways to call node/npm on Windows
            node_commands = ['node', 'node.exe']
            npm_commands = ['npm', 'npm.cmd', 'npm.exe']
            
            node_found = False
            npm_found = False
            
            # Try to find Node.js
            for cmd in node_commands:
                try:
                    node_result = subprocess.run([cmd, '--version'], 
                                               capture_output=True, text=True, shell=True)
                    if node_result.returncode == 0:
                        node_version = node_result.stdout.strip()
                        self.print_colored(f"✅ Node.js {node_version} gefunden", Colors.OKGREEN)
                        node_found = True
                        break
                except:
                    continue
            
            if not node_found:
                self.print_colored("❌ Node.js nicht gefunden!", Colors.FAIL)
                return False
            
            # Try to find npm
            for cmd in npm_commands:
                try:
                    npm_result = subprocess.run([cmd, '--version'], 
                                              capture_output=True, text=True, shell=True)
                    if npm_result.returncode == 0:
                        npm_version = npm_result.stdout.strip()
                        self.print_colored(f"✅ npm {npm_version} gefunden", Colors.OKGREEN)
                        npm_found = True
                        break
                except:
                    continue
            
            if not npm_found:
                self.print_colored("❌ npm nicht gefunden!", Colors.FAIL)
                return False
                
        except Exception as e:
            self.print_colored(f"❌ Fehler beim Überprüfen von Node.js/npm: {e}", Colors.FAIL)
            return False
            
        # Check if frontend dependencies are installed
        frontend_node_modules = Path("frontend/node_modules")
        if not frontend_node_modules.exists():
            self.print_colored("⚠️  Frontend-Dependencies nicht installiert. Installiere...", Colors.WARNING)
            try:
                subprocess.run(['npm', 'install'], cwd='frontend', check=True)
                self.print_colored("✅ Frontend-Dependencies installiert", Colors.OKGREEN)
            except subprocess.CalledProcessError:
                self.print_colored("❌ Fehler beim Installieren der Frontend-Dependencies", Colors.FAIL)
                return False
                
        self.print_colored("✅ Alle Dependencies verfügbar", Colors.OKGREEN)
        return True
    
    def start_backend(self, port: int = 8000) -> bool:
        """Start the FastAPI backend server"""
        self.print_colored(f"🚀 Starte Backend Server (FastAPI) auf Port {port}...", Colors.OKCYAN)
        
        if not Path("backend").exists():
            self.print_colored("❌ Backend-Verzeichnis nicht gefunden!", Colors.FAIL)
            return False
            
        try:
            # Start uvicorn server
            cmd = [
                sys.executable, '-m', 'uvicorn', 
                'main:app', 
                '--host', '0.0.0.0', 
                '--port', str(port), 
                '--reload',
                '--log-level', 'info'
            ]
            
            self.backend_process = subprocess.Popen(
                cmd,
                cwd='backend',
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Store the actual port used
            self.backend_port = port
            
            # Start thread to monitor backend output
            threading.Thread(
                target=self._monitor_process_output, 
                args=(self.backend_process, "BACKEND", Colors.OKBLUE),
                daemon=True
            ).start()
            
            # Wait a moment and check if process is still running
            time.sleep(2)
            if self.backend_process.poll() is None:
                self.print_colored(f"✅ Backend Server gestartet auf http://localhost:{port}", Colors.OKGREEN)
                return True
            else:
                self.print_colored("❌ Backend Server konnte nicht gestartet werden", Colors.FAIL)
                return False
                
        except Exception as e:
            self.print_colored(f"❌ Fehler beim Starten des Backend Servers: {e}", Colors.FAIL)
            return False
    
    def start_frontend(self) -> bool:
        """Start the Vite frontend development server"""
        self.print_colored("🚀 Starte Frontend Server (Vite)...", Colors.OKCYAN)
        
        if not Path("frontend").exists():
            self.print_colored("❌ Frontend-Verzeichnis nicht gefunden!", Colors.FAIL)
            return False
            
        try:
            # Start npm dev server (Windows-compatible)
            npm_commands = ['npm', 'npm.cmd', 'npm.exe']
            
            frontend_process = None
            for npm_cmd in npm_commands:
                try:
                    cmd = [npm_cmd, 'run', 'dev']
                    
                    self.frontend_process = subprocess.Popen(
                        cmd,
                        cwd='frontend',
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        bufsize=1,
                        shell=True
                    )
                    break
                except FileNotFoundError:
                    continue
            
            if self.frontend_process is None:
                raise Exception("npm command not found")
            
            # Start thread to monitor frontend output
            threading.Thread(
                target=self._monitor_process_output, 
                args=(self.frontend_process, "FRONTEND", Colors.OKCYAN),
                daemon=True
            ).start()
            
            # Wait a moment and check if process is still running
            time.sleep(3)
            if self.frontend_process.poll() is None:
                self.print_colored("✅ Frontend Server gestartet auf http://localhost:3000", Colors.OKGREEN)
                return True
            else:
                self.print_colored("❌ Frontend Server konnte nicht gestartet werden", Colors.FAIL)
                return False
                
        except Exception as e:
            self.print_colored(f"❌ Fehler beim Starten des Frontend Servers: {e}", Colors.FAIL)
            return False
    
    def _monitor_process_output(self, process: subprocess.Popen, name: str, color: str):
        """Monitor and display process output"""
        try:
            for line in iter(process.stdout.readline, ''):
                if line and self.running:
                    # Filter out some verbose logs
                    if any(skip in line.lower() for skip in ['watching for file changes', 'started server process']):
                        continue
                    print(f"{color}[{name}]{Colors.ENDC} {line.rstrip()}")
        except Exception:
            pass
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        self.print_colored("\n🛑 Stoppe Server...", Colors.WARNING)
        self.stop_servers()
        sys.exit(0)
    
    def stop_servers(self):
        """Stop both servers gracefully"""
        self.running = False
        
        if self.backend_process and self.backend_process.poll() is None:
            self.print_colored("🛑 Stoppe Backend Server...", Colors.WARNING)
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
            self.print_colored("✅ Backend Server gestoppt", Colors.OKGREEN)
        
        if self.frontend_process and self.frontend_process.poll() is None:
            self.print_colored("🛑 Stoppe Frontend Server...", Colors.WARNING)
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
            self.print_colored("✅ Frontend Server gestoppt", Colors.OKGREEN)
    
    def find_available_port(self, start_port: int, service_name: str) -> Optional[int]:
        """Find an available port starting from start_port"""
        for port in range(start_port, start_port + 10):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex(('localhost', port))
                    if result != 0:  # Port is available
                        self.print_colored(f"✅ Port {port} ist verfügbar für {service_name}", Colors.OKGREEN)
                        return port
            except Exception:
                continue
        return None

    def start_servers(self):
        """Start both backend and frontend servers"""
        self.print_colored("=" * 60, Colors.HEADER)
        self.print_colored("🏥 GynOrg Development Server Starter", Colors.HEADER)
        self.print_colored("=" * 60, Colors.HEADER)
        
        # Check dependencies first
        if not self.check_dependencies():
            return False
        
        # Find available backend port
        backend_port = 8000
        if not self.check_port(8000, "Backend"):
            self.print_colored("🔍 Suche nach alternativem Backend-Port...", Colors.OKCYAN)
            backend_port = self.find_available_port(8001, "Backend")
            if backend_port is None:
                self.print_colored("❌ Kein verfügbarer Port für Backend gefunden (8000-8009)", Colors.FAIL)
                self.print_colored("💡 Tipp: Verwende 'python stop.py' um laufende Server zu stoppen", Colors.WARNING)
                return False
            else:
                self.print_colored(f"🔄 Verwende alternativen Backend-Port: {backend_port}", Colors.WARNING)
            
        # Check frontend port
        if not self.check_port(3000, "Frontend"):
            self.print_colored("💡 Tipp: Verwende 'python stop.py' um laufende Server zu stoppen", Colors.WARNING)
            return False
        
        # Start backend with determined port
        if not self.start_backend(backend_port):
            return False
        
        # Start frontend
        if not self.start_frontend():
            self.stop_servers()
            return False
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.print_colored("\n" + "=" * 60, Colors.OKGREEN)
        self.print_colored("🎉 Beide Server erfolgreich gestartet!", Colors.OKGREEN)
        self.print_colored("🌐 Frontend: http://localhost:3000", Colors.OKGREEN)
        self.print_colored(f"🔧 Backend:  http://localhost:{backend_port}", Colors.OKGREEN)
        self.print_colored(f"📚 API Docs: http://localhost:{backend_port}/api/v1/docs", Colors.OKGREEN)
        if backend_port != 8000:
            self.print_colored(f"⚠️  Backend läuft auf Port {backend_port} statt 8000!", Colors.WARNING)
            self.print_colored("   Stelle sicher, dass das Frontend die richtige Backend-URL verwendet.", Colors.WARNING)
        self.print_colored("=" * 60, Colors.OKGREEN)
        self.print_colored("\n💡 Drücke Ctrl+C um beide Server zu stoppen", Colors.WARNING)
        
        # Keep the script running
        try:
            while self.running:
                time.sleep(1)
                # Check if processes are still running
                if self.backend_process and self.backend_process.poll() is not None:
                    self.print_colored("❌ Backend Server unerwartet beendet", Colors.FAIL)
                    break
                if self.frontend_process and self.frontend_process.poll() is not None:
                    self.print_colored("❌ Frontend Server unerwartet beendet", Colors.FAIL)
                    break
        except KeyboardInterrupt:
            pass
        
        return True


def main():
    """Main entry point"""
    manager = ServerManager()
    
    try:
        success = manager.start_servers()
        if not success:
            sys.exit(1)
    except Exception as e:
        manager.print_colored(f"❌ Unerwarteter Fehler: {e}", Colors.FAIL)
        sys.exit(1)
    finally:
        manager.stop_servers()


if __name__ == "__main__":
    main()

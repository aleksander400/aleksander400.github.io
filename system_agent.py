import psutil
import platform
import subprocess
from typing import List, Dict

class SystemManager:
    def __init__(self):
        self.system_info = self.get_system_info()
        
    def execute_system_command(self, command: str) -> str:
        """Execute system command with security checks"""
        try:
            result = subprocess.run(command, shell=True, check=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.stdout.decode('utf-8')
        except subprocess.CalledProcessError as e:
            return f"Błąd wykonania komendy: {e.stderr.decode('utf-8')}"

    def get_system_info(self) -> Dict:
        """Get detailed system information"""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'cpu_cores': psutil.cpu_count(),
            'total_ram': psutil.virtual_memory().total
        }

    def list_processes(self) -> List[Dict]:
        """Get list of running processes"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            processes.append(proc.info)
        return processes

    def kill_process(self, pid: int) -> bool:
        """Terminate process by PID"""
        try:
            p = psutil.Process(pid)
            p.terminate()
            return True
        except psutil.NoSuchProcess:
            return False

    def monitor_resources(self) -> Dict:
        """Monitor system resources"""
        return {
            'cpu_usage': psutil.cpu_percent(interval=1),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_io': psutil.net_io_counters()
        }

"""
System Detection Module
Intelligent detection of hardware, OS, and system capabilities
"""

import os
import platform
import subprocess
import psutil
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SystemInfo:
    """Comprehensive system information container."""
    hostname: str
    os_name: str
    os_version: str
    architecture: str
    cpu_cores: int
    cpu_frequency: float
    memory_total: int
    memory_available: int
    disk_total: int
    disk_available: int
    network_interfaces: List[str]
    python_version: str
    package_managers: List[str]


class SystemDetector:
    """Intelligent system detection and analysis."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def detect_basic_info(self) -> Dict[str, str]:
        """Quick system detection for basic information."""
        return {
            "hostname": platform.node(),
            "os": platform.system(),
            "os_version": platform.release(),
            "arch": platform.machine(),
            "python": platform.python_version()
        }
        
    def detect_comprehensive_info(self) -> SystemInfo:
        """Comprehensive system detection and analysis."""
        self.logger.info("Starting comprehensive system detection")
        
        # Basic platform info
        hostname = platform.node()
        os_name = self._detect_os_distribution()
        os_version = platform.release()
        architecture = platform.machine()
        
        # CPU information
        cpu_cores = psutil.cpu_count(logical=False)
        cpu_frequency = psutil.cpu_freq().current if psutil.cpu_freq() else 0.0
        
        # Memory information
        memory = psutil.virtual_memory()
        memory_total = memory.total
        memory_available = memory.available
        
        # Disk information
        disk = psutil.disk_usage('/')
        disk_total = disk.total
        disk_available = disk.free
        
        # Network interfaces
        network_interfaces = self._detect_network_interfaces()
        
        # Python version
        python_version = platform.python_version()
        
        # Package managers
        package_managers = self._detect_package_managers()
        
        return SystemInfo(
            hostname=hostname,
            os_name=os_name,
            os_version=os_version,
            architecture=architecture,
            cpu_cores=cpu_cores,
            cpu_frequency=cpu_frequency,
            memory_total=memory_total,
            memory_available=memory_available,
            disk_total=disk_total,
            disk_available=disk_available,
            network_interfaces=network_interfaces,
            python_version=python_version,
            package_managers=package_managers
        )
        
    def _detect_os_distribution(self) -> str:
        """Detect specific OS distribution."""
        try:
            # Try reading /etc/os-release (most modern Linux distributions)
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('PRETTY_NAME='):
                            return line.split('=')[1].strip().strip('"')
                            
            # Fallback to platform detection
            return platform.platform()
            
        except Exception as e:
            self.logger.warning(f"Could not detect OS distribution: {e}")
            return platform.system()
            
    def _detect_network_interfaces(self) -> List[str]:
        """Detect available network interfaces."""
        try:
            interfaces = []
            net_if_addrs = psutil.net_if_addrs()
            
            for interface_name, interface_addresses in net_if_addrs.items():
                # Skip loopback interface
                if interface_name == 'lo':
                    continue
                    
                # Check if interface has IP address
                for address in interface_addresses:
                    if address.family == 2:  # AF_INET (IPv4)
                        interfaces.append(interface_name)
                        break
                        
            return interfaces
            
        except Exception as e:
            self.logger.warning(f"Could not detect network interfaces: {e}")
            return []
            
    def _detect_package_managers(self) -> List[str]:
        """Detect available package managers."""
        package_managers = []
        
        # Common package managers to check
        managers = {
            'apt': ['apt', 'apt-get'],
            'yum': ['yum'],
            'dnf': ['dnf'],
            'pacman': ['pacman'],
            'zypper': ['zypper'],
            'apk': ['apk'],
            'brew': ['brew'],
            'pip': ['pip', 'pip3'],
            'conda': ['conda'],
            'snap': ['snap'],
            'flatpak': ['flatpak']
        }
        
        for manager_name, commands in managers.items():
            for command in commands:
                if self._command_exists(command):
                    package_managers.append(manager_name)
                    break
                    
        return package_managers
        
    def _command_exists(self, command: str) -> bool:
        """Check if command exists in system PATH."""
        try:
            subprocess.run(['which', command], 
                         check=True, 
                         capture_output=True, 
                         text=True)
            return True
        except subprocess.CalledProcessError:
            return False
            
    def detect_thermal_capabilities(self) -> Dict[str, any]:
        """Detect thermal monitoring capabilities (Q9550 specific)."""
        thermal_info = {
            "sensors_available": False,
            "thermal_zones": [],
            "cpu_temp_available": False,
            "q9550_detected": False
        }
        
        try:
            # Check for sensors command
            if self._command_exists('sensors'):
                thermal_info["sensors_available"] = True
                
                # Run sensors and parse output
                result = subprocess.run(['sensors'], 
                                      capture_output=True, 
                                      text=True)
                if result.returncode == 0:
                    output = result.stdout
                    if 'Core' in output and 'temp' in output.lower():
                        thermal_info["cpu_temp_available"] = True
                        
                    # Check for Q9550 specific signatures
                    if 'Q9550' in output or 'Core 2 Quad' in output:
                        thermal_info["q9550_detected"] = True
                        
            # Check thermal zones
            thermal_zones = []
            thermal_zone_path = "/sys/class/thermal"
            if os.path.exists(thermal_zone_path):
                for item in os.listdir(thermal_zone_path):
                    if item.startswith('thermal_zone'):
                        thermal_zones.append(item)
                        
            thermal_info["thermal_zones"] = thermal_zones
            
        except Exception as e:
            self.logger.warning(f"Could not detect thermal capabilities: {e}")
            
        return thermal_info
        
    def detect_virtualization(self) -> Dict[str, any]:
        """Detect if system is running in virtualization."""
        virt_info = {
            "is_virtual": False,
            "hypervisor": None,
            "container": None
        }
        
        try:
            # Check for common virtualization indicators
            if os.path.exists('/proc/cpuinfo'):
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read()
                    
                if 'hypervisor' in cpuinfo.lower():
                    virt_info["is_virtual"] = True
                    
                # Check for specific hypervisors
                hypervisors = ['vmware', 'virtualbox', 'kvm', 'xen', 'hyper-v']
                for hypervisor in hypervisors:
                    if hypervisor in cpuinfo.lower():
                        virt_info["hypervisor"] = hypervisor
                        break
                        
            # Check for container environments
            if os.path.exists('/.dockerenv'):
                virt_info["container"] = "docker"
            elif os.path.exists('/run/.containerenv'):
                virt_info["container"] = "podman"
                
        except Exception as e:
            self.logger.warning(f"Could not detect virtualization: {e}")
            
        return virt_info
        
    def detect_security_features(self) -> Dict[str, any]:
        """Detect available security features."""
        security_info = {
            "sudo_available": False,
            "ssh_server_running": False,
            "firewall_active": False,
            "selinux_status": None,
            "apparmor_status": None
        }
        
        try:
            # Check sudo
            security_info["sudo_available"] = self._command_exists('sudo')
            
            # Check SSH server
            try:
                result = subprocess.run(['systemctl', 'is-active', 'ssh'], 
                                      capture_output=True, text=True)
                security_info["ssh_server_running"] = (result.returncode == 0 and 
                                                     'active' in result.stdout)
            except:
                # Try alternative SSH service names
                for service in ['sshd', 'openssh']:
                    try:
                        result = subprocess.run(['systemctl', 'is-active', service], 
                                              capture_output=True, text=True)
                        if result.returncode == 0 and 'active' in result.stdout:
                            security_info["ssh_server_running"] = True
                            break
                    except:
                        continue
                        
            # Check firewall
            if self._command_exists('ufw'):
                try:
                    result = subprocess.run(['ufw', 'status'], 
                                          capture_output=True, text=True)
                    security_info["firewall_active"] = 'Status: active' in result.stdout
                except:
                    pass
                    
        except Exception as e:
            self.logger.warning(f"Could not detect security features: {e}")
            
        return security_info
        
    def health_check(self) -> bool:
        """Perform basic system health check."""
        try:
            # Check disk space (warn if less than 10% free)
            disk = psutil.disk_usage('/')
            disk_free_percent = (disk.free / disk.total) * 100
            if disk_free_percent < 10:
                self.logger.warning(f"Low disk space: {disk_free_percent:.1f}% free")
                return False
                
            # Check memory usage (warn if less than 10% free)
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                self.logger.warning(f"High memory usage: {memory.percent:.1f}%")
                return False
                
            # Check CPU load
            load_avg = os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0
            cpu_cores = psutil.cpu_count()
            if load_avg > cpu_cores * 2:
                self.logger.warning(f"High CPU load: {load_avg:.2f} (cores: {cpu_cores})")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
            
    def export_system_info(self, filepath: str):
        """Export comprehensive system information to JSON."""
        try:
            system_info = self.detect_comprehensive_info()
            thermal_info = self.detect_thermal_capabilities()
            virt_info = self.detect_virtualization()
            security_info = self.detect_security_features()
            
            export_data = {
                "timestamp": psutil.boot_time(),
                "system": system_info.__dict__,
                "thermal": thermal_info,
                "virtualization": virt_info,
                "security": security_info
            }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
                
            self.logger.info(f"System information exported to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Could not export system info: {e}")
            raise
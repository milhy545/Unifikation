"""
Network Scanner Module
Intelligent network discovery and ecosystem topology detection
"""

import socket
import subprocess
import ipaddress
import concurrent.futures
import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
import json


@dataclass
class ServerInfo:
    """Information about discovered server."""
    ip_address: str
    hostname: Optional[str]
    open_ports: List[int]
    ssh_port: Optional[int]
    services: Dict[str, str]
    ping_time: float
    server_type: Optional[str]


@dataclass
class NetworkTopology:
    """Complete network topology information."""
    local_ip: str
    subnet: str
    gateway: str
    servers: List[ServerInfo]
    total_hosts: int
    ecosystem_servers: List[ServerInfo]


class NetworkScanner:
    """Intelligent network discovery and ecosystem analysis."""
    
    # Known ecosystem servers and their characteristics
    ECOSYSTEM_SERVERS = {
        "workstation": {
            "ports": [22, 8000, 3001],
            "services": ["ssh", "development", "testing"]
        },
        "llm_server": {
            "ports": [22, 2222, 8080, 11434],
            "services": ["ssh", "llm_api", "ollama"]
        },
        "orchestration": {
            "ports": [22, 2222, 8123, 3000, 9000, 8020],
            "services": ["ssh", "home_assistant", "adguard", "portainer", "zen"]
        },
        "database": {
            "ports": [22, 2222, 5432, 6379, 3306],
            "services": ["ssh", "postgresql", "redis", "mysql"]
        },
        "monitoring": {
            "ports": [22, 2222, 9090, 3000, 5601, 9200],
            "services": ["ssh", "prometheus", "grafana", "kibana", "elasticsearch"]
        }
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_local_network_info(self) -> Dict[str, str]:
        """Get local network configuration."""
        try:
            # Get default route
            result = subprocess.run(['ip', 'route', 'show', 'default'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                # Parse default route: default via 192.168.0.1 dev wlan0
                parts = result.stdout.split()
                gateway = parts[2] if len(parts) > 2 else None
                interface = parts[4] if len(parts) > 4 else None
            else:
                gateway = None
                interface = None
                
            # Get local IP address
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # Determine subnet
            if local_ip and gateway:
                # Assume /24 subnet for common home networks
                network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
                subnet = str(network.network_address) + "/24"
            else:
                subnet = None
                
            return {
                "local_ip": local_ip,
                "gateway": gateway,
                "subnet": subnet,
                "interface": interface,
                "hostname": hostname
            }
            
        except Exception as e:
            self.logger.error(f"Could not get network info: {e}")
            return {}
            
    def scan_port(self, ip: str, port: int, timeout: float = 1.0) -> bool:
        """Scan single port on target IP."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))
                return result == 0
        except Exception:
            return False
            
    def scan_common_ports(self, ip: str, timeout: float = 1.0) -> List[int]:
        """Scan common ports on target IP."""
        common_ports = [22, 80, 443, 8080, 8443, 3000, 8000, 8123, 9000, 11434, 2222]
        open_ports = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_port = {
                executor.submit(self.scan_port, ip, port, timeout): port 
                for port in common_ports
            }
            
            for future in concurrent.futures.as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    if future.result():
                        open_ports.append(port)
                except Exception as e:
                    self.logger.debug(f"Port scan error for {ip}:{port}: {e}")
                    
        return sorted(open_ports)
        
    def ping_host(self, ip: str, timeout: int = 2) -> Optional[float]:
        """Ping host and return response time."""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', str(timeout), ip],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # Parse ping time from output
                for line in result.stdout.split('\n'):
                    if 'time=' in line:
                        time_str = line.split('time=')[1].split()[0]
                        return float(time_str)
                return 0.0  # Ping successful but couldn't parse time
            else:
                return None
                
        except Exception as e:
            self.logger.debug(f"Ping failed for {ip}: {e}")
            return None
            
    def resolve_hostname(self, ip: str) -> Optional[str]:
        """Resolve IP address to hostname."""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except Exception:
            return None
            
    def identify_server_type(self, server_info: ServerInfo) -> Optional[str]:
        """Identify server type based on open ports and services."""
        open_ports_set = set(server_info.open_ports)
        
        for server_type, config in self.ECOSYSTEM_SERVERS.items():
            required_ports = set(config["ports"])
            
            # Check if server has majority of required ports
            matching_ports = open_ports_set.intersection(required_ports)
            if len(matching_ports) >= len(required_ports) * 0.6:  # 60% match threshold
                return server_type
                
        return None
        
    def scan_subnet(self, subnet: str, timeout: float = 1.0) -> List[ServerInfo]:
        """Scan entire subnet for active hosts."""
        self.logger.info(f"Scanning subnet: {subnet}")
        
        try:
            network = ipaddress.IPv4Network(subnet, strict=False)
        except ValueError as e:
            self.logger.error(f"Invalid subnet: {e}")
            return []
            
        active_servers = []
        
        # Scan hosts in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            future_to_ip = {
                executor.submit(self._scan_single_host, str(ip), timeout): str(ip)
                for ip in network.hosts()
            }
            
            for future in concurrent.futures.as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    server_info = future.result()
                    if server_info:
                        active_servers.append(server_info)
                        self.logger.info(f"Found server: {ip} ({server_info.hostname})")
                except Exception as e:
                    self.logger.debug(f"Scan error for {ip}: {e}")
                    
        return active_servers
        
    def _scan_single_host(self, ip: str, timeout: float) -> Optional[ServerInfo]:
        """Scan single host for server information."""
        # First ping to check if host is alive
        ping_time = self.ping_host(ip, timeout=2)
        if ping_time is None:
            return None
            
        # Resolve hostname
        hostname = self.resolve_hostname(ip)
        
        # Scan ports
        open_ports = self.scan_common_ports(ip, timeout)
        
        # Detect SSH port
        ssh_port = None
        for port in [22, 2222]:
            if port in open_ports:
                ssh_port = port
                break
                
        # Identify services
        services = self._identify_services(open_ports)
        
        server_info = ServerInfo(
            ip_address=ip,
            hostname=hostname,
            open_ports=open_ports,
            ssh_port=ssh_port,
            services=services,
            ping_time=ping_time,
            server_type=None
        )
        
        # Identify server type
        server_info.server_type = self.identify_server_type(server_info)
        
        return server_info
        
    def _identify_services(self, open_ports: List[int]) -> Dict[str, str]:
        """Identify services based on open ports."""
        service_mapping = {
            22: "ssh",
            2222: "ssh-alt",
            80: "http",
            443: "https",
            3000: "grafana/adguard",
            8000: "development",
            8080: "http-alt/llm-api",
            8123: "home-assistant",
            8443: "https-alt",
            9000: "portainer",
            11434: "ollama",
            5432: "postgresql",
            6379: "redis",
            3306: "mysql",
            9090: "prometheus",
            5601: "kibana",
            9200: "elasticsearch"
        }
        
        services = {}
        for port in open_ports:
            if port in service_mapping:
                services[str(port)] = service_mapping[port]
                
        return services
        
    def scan_ecosystem(self) -> List[ServerInfo]:
        """Scan for ecosystem servers specifically."""
        network_info = self.get_local_network_info()
        
        if not network_info.get("subnet"):
            self.logger.error("Could not determine local subnet")
            return []
            
        all_servers = self.scan_subnet(network_info["subnet"])
        
        # Filter for ecosystem servers (servers with SSH and other services)
        ecosystem_servers = []
        for server in all_servers:
            if (server.ssh_port and 
                len(server.open_ports) > 1 and 
                server.server_type):
                ecosystem_servers.append(server)
                
        return ecosystem_servers
        
    def discover_network_topology(self) -> NetworkTopology:
        """Discover complete network topology."""
        self.logger.info("Discovering network topology")
        
        network_info = self.get_local_network_info()
        
        if not network_info.get("subnet"):
            self.logger.error("Could not determine network topology")
            return NetworkTopology(
                local_ip="unknown",
                subnet="unknown", 
                gateway="unknown",
                servers=[],
                total_hosts=0,
                ecosystem_servers=[]
            )
            
        # Scan all servers
        all_servers = self.scan_subnet(network_info["subnet"])
        
        # Identify ecosystem servers
        ecosystem_servers = [s for s in all_servers if s.server_type]
        
        return NetworkTopology(
            local_ip=network_info["local_ip"],
            subnet=network_info["subnet"],
            gateway=network_info["gateway"],
            servers=all_servers,
            total_hosts=len(all_servers),
            ecosystem_servers=ecosystem_servers
        )
        
    def test_ssh_connectivity(self, servers: List[ServerInfo]) -> Dict[str, bool]:
        """Test SSH connectivity to discovered servers."""
        connectivity_results = {}
        
        for server in servers:
            if not server.ssh_port:
                connectivity_results[server.ip_address] = False
                continue
                
            try:
                # Test SSH connection (just connection, not authentication)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(5)
                    result = sock.connect_ex((server.ip_address, server.ssh_port))
                    connectivity_results[server.ip_address] = (result == 0)
                    
            except Exception as e:
                self.logger.debug(f"SSH test failed for {server.ip_address}: {e}")
                connectivity_results[server.ip_address] = False
                
        return connectivity_results
        
    def connectivity_check(self) -> bool:
        """Perform basic connectivity health check."""
        try:
            # Test internet connectivity
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                result = sock.connect_ex(("8.8.8.8", 53))
                internet_ok = (result == 0)
                
            # Test local network
            network_info = self.get_local_network_info()
            gateway_ok = True
            if network_info.get("gateway"):
                ping_result = self.ping_host(network_info["gateway"])
                gateway_ok = ping_result is not None
                
            return internet_ok and gateway_ok
            
        except Exception as e:
            self.logger.error(f"Connectivity check failed: {e}")
            return False
            
    def export_topology(self, filepath: str):
        """Export network topology to JSON file."""
        try:
            topology = self.discover_network_topology()
            
            # Convert to serializable format
            topology_dict = {
                "local_ip": topology.local_ip,
                "subnet": topology.subnet,
                "gateway": topology.gateway,
                "total_hosts": topology.total_hosts,
                "servers": [
                    {
                        "ip_address": server.ip_address,
                        "hostname": server.hostname,
                        "open_ports": server.open_ports,
                        "ssh_port": server.ssh_port,
                        "services": server.services,
                        "ping_time": server.ping_time,
                        "server_type": server.server_type
                    }
                    for server in topology.servers
                ],
                "ecosystem_servers": [
                    {
                        "ip_address": server.ip_address,
                        "hostname": server.hostname,
                        "server_type": server.server_type,
                        "open_ports": server.open_ports
                    }
                    for server in topology.ecosystem_servers
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(topology_dict, f, indent=2)
                
            self.logger.info(f"Network topology exported to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Could not export topology: {e}")
            raise
"""
Dependency Resolution Module
Intelligent package dependency management across different OS distributions
"""

import subprocess
import logging
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class PackageManager(Enum):
    """Supported package managers."""
    APT = "apt"
    YUM = "yum"
    DNF = "dnf"
    PACMAN = "pacman"
    ZYPPER = "zypper"
    APK = "apk"
    BREW = "brew"
    PIP = "pip"
    CONDA = "conda"
    SNAP = "snap"


@dataclass
class Package:
    """Package definition with OS-specific names."""
    name: str
    apt_name: Optional[str] = None
    yum_name: Optional[str] = None
    dnf_name: Optional[str] = None
    pacman_name: Optional[str] = None
    apk_name: Optional[str] = None
    brew_name: Optional[str] = None
    pip_name: Optional[str] = None
    description: str = ""
    required: bool = True


@dataclass
class InstallationPlan:
    """Complete installation plan for system setup."""
    packages_to_install: List[Package]
    packages_to_update: List[Package]
    conflicts_detected: List[str]
    installation_order: List[List[Package]]
    estimated_time: int
    disk_space_required: int


class DependencyResolver:
    """Intelligent dependency resolution and package management."""
    
    # Common packages with OS-specific names
    COMMON_PACKAGES = {
        "git": Package(
            name="git",
            apt_name="git",
            yum_name="git",
            dnf_name="git",
            pacman_name="git",
            apk_name="git",
            brew_name="git",
            description="Version control system"
        ),
        "python3": Package(
            name="python3",
            apt_name="python3",
            yum_name="python3",
            dnf_name="python3",
            pacman_name="python",
            apk_name="python3",
            brew_name="python@3.9",
            description="Python 3 interpreter"
        ),
        "pip": Package(
            name="pip",
            apt_name="python3-pip",
            yum_name="python3-pip",
            dnf_name="python3-pip",
            pacman_name="python-pip",
            apk_name="py3-pip",
            pip_name="pip",
            description="Python package installer"
        ),
        "curl": Package(
            name="curl",
            apt_name="curl",
            yum_name="curl",
            dnf_name="curl",
            pacman_name="curl",
            apk_name="curl",
            brew_name="curl",
            description="Command line tool for transfers"
        ),
        "wget": Package(
            name="wget",
            apt_name="wget",
            yum_name="wget",
            dnf_name="wget",
            pacman_name="wget",
            apk_name="wget",
            brew_name="wget",
            description="Network downloader"
        ),
        "ssh": Package(
            name="ssh",
            apt_name="openssh-client",
            yum_name="openssh-clients",
            dnf_name="openssh-clients",
            pacman_name="openssh",
            apk_name="openssh-client",
            description="SSH client"
        ),
        "sshd": Package(
            name="sshd",
            apt_name="openssh-server",
            yum_name="openssh-server",
            dnf_name="openssh-server",
            pacman_name="openssh",
            apk_name="openssh-server",
            description="SSH server daemon"
        ),
        "tmux": Package(
            name="tmux",
            apt_name="tmux",
            yum_name="tmux",
            dnf_name="tmux",
            pacman_name="tmux",
            apk_name="tmux",
            brew_name="tmux",
            description="Terminal multiplexer"
        ),
        "htop": Package(
            name="htop",
            apt_name="htop",
            yum_name="htop",
            dnf_name="htop",
            pacman_name="htop",
            apk_name="htop",
            brew_name="htop",
            description="Interactive process viewer"
        ),
        "docker": Package(
            name="docker",
            apt_name="docker.io",
            yum_name="docker",
            dnf_name="docker",
            pacman_name="docker",
            apk_name="docker",
            brew_name="docker",
            description="Container platform"
        ),
        "nodejs": Package(
            name="nodejs",
            apt_name="nodejs",
            yum_name="nodejs",
            dnf_name="nodejs",
            pacman_name="nodejs",
            apk_name="nodejs",
            brew_name="node",
            description="JavaScript runtime"
        ),
        "npm": Package(
            name="npm",
            apt_name="npm",
            yum_name="npm",
            dnf_name="npm",
            pacman_name="npm",
            apk_name="npm",
            brew_name="npm",
            description="Node.js package manager"
        )
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.detected_managers = self._detect_package_managers()
        
    def _detect_package_managers(self) -> List[PackageManager]:
        """Detect available package managers on the system."""
        managers = []
        
        manager_commands = {
            PackageManager.APT: ["apt", "apt-get"],
            PackageManager.YUM: ["yum"],
            PackageManager.DNF: ["dnf"],
            PackageManager.PACMAN: ["pacman"],
            PackageManager.ZYPPER: ["zypper"],
            PackageManager.APK: ["apk"],
            PackageManager.BREW: ["brew"],
            PackageManager.PIP: ["pip", "pip3"],
            PackageManager.CONDA: ["conda"],
            PackageManager.SNAP: ["snap"]
        }
        
        for manager, commands in manager_commands.items():
            for command in commands:
                if self._command_exists(command):
                    managers.append(manager)
                    break
                    
        return managers
        
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
            
    def get_package_name(self, package: Package, manager: PackageManager) -> Optional[str]:
        """Get OS-specific package name for given package manager."""
        name_mapping = {
            PackageManager.APT: package.apt_name,
            PackageManager.YUM: package.yum_name,
            PackageManager.DNF: package.dnf_name,
            PackageManager.PACMAN: package.pacman_name,
            PackageManager.APK: package.apk_name,
            PackageManager.BREW: package.brew_name,
            PackageManager.PIP: package.pip_name
        }
        
        return name_mapping.get(manager) or package.name
        
    def is_package_installed(self, package: Package) -> bool:
        """Check if package is already installed."""
        for manager in self.detected_managers:
            package_name = self.get_package_name(package, manager)
            if not package_name:
                continue
                
            try:
                if manager == PackageManager.APT:
                    result = subprocess.run(
                        ['dpkg', '-l', package_name],
                        capture_output=True, text=True
                    )
                    return result.returncode == 0
                    
                elif manager == PackageManager.YUM:
                    result = subprocess.run(
                        ['rpm', '-q', package_name],
                        capture_output=True, text=True
                    )
                    return result.returncode == 0
                    
                elif manager == PackageManager.DNF:
                    result = subprocess.run(
                        ['rpm', '-q', package_name],
                        capture_output=True, text=True
                    )
                    return result.returncode == 0
                    
                elif manager == PackageManager.PACMAN:
                    result = subprocess.run(
                        ['pacman', '-Q', package_name],
                        capture_output=True, text=True
                    )
                    return result.returncode == 0
                    
                elif manager == PackageManager.APK:
                    result = subprocess.run(
                        ['apk', 'info', '-e', package_name],
                        capture_output=True, text=True
                    )
                    return result.returncode == 0
                    
                elif manager == PackageManager.PIP:
                    result = subprocess.run(
                        ['pip', 'show', package_name],
                        capture_output=True, text=True
                    )
                    return result.returncode == 0
                    
            except Exception as e:
                self.logger.debug(f"Could not check {package_name} with {manager}: {e}")
                continue
                
        return False
        
    def resolve_dependencies(self, required_packages: List[str]) -> InstallationPlan:
        """Resolve dependencies and create installation plan."""
        self.logger.info(f"Resolving dependencies for {len(required_packages)} packages")
        
        packages_to_install = []
        packages_to_update = []
        conflicts_detected = []
        
        for package_name in required_packages:
            if package_name in self.COMMON_PACKAGES:
                package = self.COMMON_PACKAGES[package_name]
                
                if not self.is_package_installed(package):
                    packages_to_install.append(package)
                    self.logger.debug(f"Package {package_name} needs installation")
                else:
                    self.logger.debug(f"Package {package_name} already installed")
            else:
                self.logger.warning(f"Unknown package: {package_name}")
                
        # Detect conflicts
        conflicts_detected = self._detect_conflicts(packages_to_install)
        
        # Create installation order based on dependencies
        installation_order = self._create_installation_order(packages_to_install)
        
        # Estimate installation time and disk space
        estimated_time = len(packages_to_install) * 30  # 30 seconds per package
        disk_space_required = len(packages_to_install) * 50  # 50MB per package
        
        return InstallationPlan(
            packages_to_install=packages_to_install,
            packages_to_update=packages_to_update,
            conflicts_detected=conflicts_detected,
            installation_order=installation_order,
            estimated_time=estimated_time,
            disk_space_required=disk_space_required
        )
        
    def _detect_conflicts(self, packages: List[Package]) -> List[str]:
        """Detect potential package conflicts."""
        conflicts = []
        
        # Known conflicts
        conflict_sets = [
            {"yum", "dnf"},  # YUM and DNF conflict
            {"python2", "python3"},  # Python version conflicts
        ]
        
        package_names = {pkg.name for pkg in packages}
        
        for conflict_set in conflict_sets:
            if len(conflict_set.intersection(package_names)) > 1:
                conflicts.append(f"Conflicting packages: {', '.join(conflict_set)}")
                
        return conflicts
        
    def _create_installation_order(self, packages: List[Package]) -> List[List[Package]]:
        """Create optimal installation order based on dependencies."""
        # Simple ordering: system packages first, then applications
        system_packages = []
        dev_packages = []
        app_packages = []
        
        for package in packages:
            if package.name in ["python3", "pip", "git", "curl", "wget"]:
                system_packages.append(package)
            elif package.name in ["nodejs", "npm", "docker"]:
                dev_packages.append(package)
            else:
                app_packages.append(package)
                
        return [group for group in [system_packages, dev_packages, app_packages] if group]
        
    def install_packages(self, packages: List[Package], dry_run: bool = False) -> bool:
        """Install packages using appropriate package manager."""
        if not packages:
            self.logger.info("No packages to install")
            return True
            
        self.logger.info(f"Installing {len(packages)} packages (dry_run={dry_run})")
        
        for manager in self.detected_managers:
            if manager in [PackageManager.APT, PackageManager.YUM, PackageManager.DNF, 
                          PackageManager.PACMAN, PackageManager.APK]:
                return self._install_with_system_manager(packages, manager, dry_run)
                
        self.logger.error("No suitable package manager found")
        return False
        
    def _install_with_system_manager(self, packages: List[Package], 
                                   manager: PackageManager, dry_run: bool) -> bool:
        """Install packages with system package manager."""
        package_names = []
        
        for package in packages:
            name = self.get_package_name(package, manager)
            if name:
                package_names.append(name)
                
        if not package_names:
            self.logger.warning("No valid package names found")
            return False
            
        commands = {
            PackageManager.APT: ["sudo", "apt", "install", "-y"] + package_names,
            PackageManager.YUM: ["sudo", "yum", "install", "-y"] + package_names,
            PackageManager.DNF: ["sudo", "dnf", "install", "-y"] + package_names,
            PackageManager.PACMAN: ["sudo", "pacman", "-S", "--noconfirm"] + package_names,
            PackageManager.APK: ["sudo", "apk", "add"] + package_names
        }
        
        command = commands.get(manager)
        if not command:
            self.logger.error(f"Unsupported package manager: {manager}")
            return False
            
        if dry_run:
            self.logger.info(f"Would run: {' '.join(command)}")
            return True
            
        try:
            self.logger.info(f"Running: {' '.join(command)}")
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            self.logger.info("Package installation completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Package installation failed: {e}")
            self.logger.error(f"Error output: {e.stderr}")
            return False
            
    def update_package_lists(self) -> bool:
        """Update package manager repositories."""
        for manager in self.detected_managers:
            try:
                if manager == PackageManager.APT:
                    subprocess.run(["sudo", "apt", "update"], check=True)
                elif manager == PackageManager.YUM:
                    subprocess.run(["sudo", "yum", "check-update"], check=False)
                elif manager == PackageManager.DNF:
                    subprocess.run(["sudo", "dnf", "check-update"], check=False)
                elif manager == PackageManager.PACMAN:
                    subprocess.run(["sudo", "pacman", "-Sy"], check=True)
                elif manager == PackageManager.APK:
                    subprocess.run(["sudo", "apk", "update"], check=True)
                    
                self.logger.info(f"Updated {manager.value} package lists")
                return True
                
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"Could not update {manager.value}: {e}")
                continue
                
        return False
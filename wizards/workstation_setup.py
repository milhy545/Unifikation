"""
Workstation Setup Wizard
Automated setup for development workstation (Aspire PC type)
"""

import os
import sys
import logging
import subprocess
from typing import Dict, List, Optional
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tools.system_detector import SystemDetector
from tools.dependency_resolver import DependencyResolver
from tools.network_scanner import NetworkScanner
from tools.config_validator import ConfigValidator


@dataclass
class WorkstationConfig:
    """Workstation configuration parameters."""
    hostname: str
    enable_ssh_server: bool = True
    ssh_port: int = 2222
    install_development_tools: bool = True
    setup_tmux_ecosystem: bool = True
    configure_power_management: bool = True
    setup_ai_tools: bool = True
    enable_monitoring: bool = True


class WorkstationWizard:
    """Intelligent workstation setup wizard."""
    
    REQUIRED_PACKAGES = [
        "git", "python3", "pip", "curl", "wget", "ssh", "sshd", 
        "tmux", "htop", "nodejs", "npm"
    ]
    
    DEVELOPMENT_PACKAGES = [
        "docker", "code", "firefox", "vim", "nano", "build-essential",
        "python3-dev", "python3-venv"
    ]
    
    AI_TOOLS_PACKAGES = [
        "python3-pip", "python3-dev", "ffmpeg", "git-lfs"
    ]
    
    def __init__(self, language: str = "en"):
        """Initialize workstation wizard."""
        self.language = language
        self.system_detector = SystemDetector()
        self.dependency_resolver = DependencyResolver()
        self.network_scanner = NetworkScanner()
        self.config_validator = ConfigValidator()
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging for the wizard."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('workstation_setup.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def gather_requirements(self) -> WorkstationConfig:
        """Gather workstation setup requirements from user."""
        self.logger.info("Gathering workstation setup requirements")
        
        if self.language == "cz":
            print("\n🖥️ NASTAVENÍ VÝVOJOVÉ WORKSTATION")
            print("=" * 50)
            hostname = input("Název počítače [Aspire-PC]: ") or "Aspire-PC"
            
            ssh_prompt = "Povolit SSH server? (y/n) [y]: "
            ssh_input = input(ssh_prompt).lower()
            enable_ssh = ssh_input in ['', 'y', 'yes', 'ano']
            
            dev_prompt = "Nainstalovat vývojové nástroje? (y/n) [y]: "
            dev_input = input(dev_prompt).lower()
            install_dev = dev_input in ['', 'y', 'yes', 'ano']
            
            ai_prompt = "Nastavit AI nástroje (Claude, etc.)? (y/n) [y]: "
            ai_input = input(ai_prompt).lower()
            setup_ai = ai_input in ['', 'y', 'yes', 'ano']
            
            power_prompt = "Nastavit Q9550 power management? (y/n) [y]: "
            power_input = input(power_prompt).lower()
            setup_power = power_input in ['', 'y', 'yes', 'ano']
            
        else:
            print("\n💻 WORKSTATION SETUP")
            print("=" * 30)
            hostname = input("Computer hostname [Aspire-PC]: ") or "Aspire-PC"
            
            ssh_input = input("Enable SSH server? (y/n) [y]: ").lower()
            enable_ssh = ssh_input in ['', 'y', 'yes']
            
            dev_input = input("Install development tools? (y/n) [y]: ").lower()
            install_dev = dev_input in ['', 'y', 'yes']
            
            ai_input = input("Setup AI tools (Claude, etc.)? (y/n) [y]: ").lower()
            setup_ai = ai_input in ['', 'y', 'yes']
            
            power_input = input("Setup Q9550 power management? (y/n) [y]: ").lower()
            setup_power = power_input in ['', 'y', 'yes']
            
        return WorkstationConfig(
            hostname=hostname,
            enable_ssh_server=enable_ssh,
            install_development_tools=install_dev,
            setup_ai_tools=setup_ai,
            configure_power_management=setup_power
        )
        
    def analyze_system(self) -> Dict:
        """Analyze current system state."""
        self.logger.info("Analyzing system configuration")
        
        # Detect system information
        system_info = self.system_detector.detect_comprehensive_info()
        thermal_info = self.system_detector.detect_thermal_capabilities()
        security_info = self.system_detector.detect_security_features()
        
        # Detect network topology
        network_topology = self.network_scanner.discover_network_topology()
        
        # Validate current configuration
        validation_report = self.config_validator.generate_validation_report()
        
        analysis = {
            "system": system_info,
            "thermal": thermal_info,
            "security": security_info,
            "network": network_topology,
            "validation": validation_report,
            "q9550_detected": thermal_info.get("q9550_detected", False),
            "existing_ecosystem": len(network_topology.ecosystem_servers) > 0
        }
        
        # Display analysis results
        if self.language == "cz":
            print(f"\n📊 ANALÝZA SYSTÉMU")
            print(f"• OS: {system_info.os_name}")
            print(f"• CPU: {system_info.cpu_cores} jader @ {system_info.cpu_frequency:.1f} MHz")
            print(f"• RAM: {system_info.memory_total // (1024**3)} GB")
            print(f"• Q9550 detekováno: {'✅' if analysis['q9550_detected'] else '❌'}")
            print(f"• Existující ecosystem: {len(network_topology.ecosystem_servers)} serverů")
        else:
            print(f"\n📊 SYSTEM ANALYSIS")
            print(f"• OS: {system_info.os_name}")
            print(f"• CPU: {system_info.cpu_cores} cores @ {system_info.cpu_frequency:.1f} MHz")
            print(f"• RAM: {system_info.memory_total // (1024**3)} GB")
            print(f"• Q9550 detected: {'✅' if analysis['q9550_detected'] else '❌'}")
            print(f"• Existing ecosystem: {len(network_topology.ecosystem_servers)} servers")
            
        return analysis
        
    def create_installation_plan(self, config: WorkstationConfig, analysis: Dict) -> Dict:
        """Create detailed installation plan."""
        self.logger.info("Creating installation plan")
        
        # Base packages
        packages_to_install = self.REQUIRED_PACKAGES.copy()
        
        # Add optional packages based on configuration
        if config.install_development_tools:
            packages_to_install.extend(self.DEVELOPMENT_PACKAGES)
            
        if config.setup_ai_tools:
            packages_to_install.extend(self.AI_TOOLS_PACKAGES)
            
        # Resolve dependencies
        installation_plan = self.dependency_resolver.resolve_dependencies(packages_to_install)
        
        # Configuration steps
        config_steps = []
        
        if config.enable_ssh_server:
            config_steps.append({
                "name": "configure_ssh",
                "description": "Configure SSH server on port 2222",
                "estimated_time": 60
            })
            
        if config.setup_tmux_ecosystem:
            config_steps.append({
                "name": "setup_tmux",
                "description": "Configure tmux ecosystem integration",
                "estimated_time": 120
            })
            
        if config.configure_power_management and analysis["q9550_detected"]:
            config_steps.append({
                "name": "setup_power_management",
                "description": "Configure Q9550 thermal management",
                "estimated_time": 180
            })
            
        if config.setup_ai_tools:
            config_steps.append({
                "name": "setup_ai_tools",
                "description": "Configure AI development environment",
                "estimated_time": 300
            })
            
        total_time = (installation_plan.estimated_time + 
                     sum(step["estimated_time"] for step in config_steps))
        
        plan = {
            "packages": installation_plan,
            "configuration_steps": config_steps,
            "total_estimated_time": total_time,
            "disk_space_required": installation_plan.disk_space_required + 1000,  # +1GB for configs
            "conflicts": installation_plan.conflicts_detected,
            "warnings": []
        }
        
        # Add warnings
        if analysis["validation"].overall_status == "error":
            plan["warnings"].append("System has configuration errors that need fixing")
            
        if not analysis["security"]["sudo_available"]:
            plan["warnings"].append("Sudo access required for system configuration")
            
        return plan
        
    def display_installation_plan(self, plan: Dict):
        """Display installation plan to user."""
        if self.language == "cz":
            print(f"\n📋 INSTALAČNÍ PLÁN")
            print(f"• Balíčky k instalaci: {len(plan['packages'].packages_to_install)}")
            print(f"• Konfigurační kroky: {len(plan['configuration_steps'])}")
            print(f"• Odhadovaný čas: {plan['total_estimated_time']//60} minut")
            print(f"• Potřebný diskový prostor: {plan['disk_space_required']} MB")
            
            if plan['conflicts']:
                print(f"⚠️  Konflikty: {len(plan['conflicts'])}")
                for conflict in plan['conflicts']:
                    print(f"   • {conflict}")
                    
            if plan['warnings']:
                print(f"⚠️  Upozornění:")
                for warning in plan['warnings']:
                    print(f"   • {warning}")
                    
        else:
            print(f"\n📋 INSTALLATION PLAN")
            print(f"• Packages to install: {len(plan['packages'].packages_to_install)}")
            print(f"• Configuration steps: {len(plan['configuration_steps'])}")
            print(f"• Estimated time: {plan['total_estimated_time']//60} minutes")
            print(f"• Disk space required: {plan['disk_space_required']} MB")
            
            if plan['conflicts']:
                print(f"⚠️  Conflicts: {len(plan['conflicts'])}")
                for conflict in plan['conflicts']:
                    print(f"   • {conflict}")
                    
            if plan['warnings']:
                print(f"⚠️  Warnings:")
                for warning in plan['warnings']:
                    print(f"   • {warning}")
                    
    def execute_installation(self, plan: Dict, config: WorkstationConfig, dry_run: bool = False):
        """Execute the installation plan."""
        self.logger.info(f"Executing installation plan (dry_run={dry_run})")
        
        try:
            # Update package lists
            if not dry_run:
                self.dependency_resolver.update_package_lists()
                
            # Install packages
            success = self.dependency_resolver.install_packages(
                plan['packages'].packages_to_install, 
                dry_run=dry_run
            )
            
            if not success and not dry_run:
                raise Exception("Package installation failed")
                
            # Execute configuration steps
            for step in plan['configuration_steps']:
                self.logger.info(f"Executing step: {step['name']}")
                
                if step['name'] == 'configure_ssh':
                    self._configure_ssh_server(config, dry_run)
                elif step['name'] == 'setup_tmux':
                    self._setup_tmux_ecosystem(config, dry_run)
                elif step['name'] == 'setup_power_management':
                    self._setup_power_management(config, dry_run)
                elif step['name'] == 'setup_ai_tools':
                    self._setup_ai_tools(config, dry_run)
                    
            self.logger.info("Installation completed successfully")
            
        except Exception as e:
            self.logger.error(f"Installation failed: {e}")
            raise
            
    def _configure_ssh_server(self, config: WorkstationConfig, dry_run: bool):
        """Configure SSH server."""
        if dry_run:
            self.logger.info("Would configure SSH server on port 2222")
            return
            
        # Configure SSH server port
        ssh_config = f"""
# Workstation SSH Configuration
Port {config.ssh_port}
PermitRootLogin no
PasswordAuthentication yes
PubkeyAuthentication yes
"""
        
        self.logger.info("Configuring SSH server")
        # In real implementation, would modify /etc/ssh/sshd_config
        
    def _setup_tmux_ecosystem(self, config: WorkstationConfig, dry_run: bool):
        """Setup tmux ecosystem integration."""
        if dry_run:
            self.logger.info("Would setup tmux ecosystem")
            return
            
        self.logger.info("Setting up tmux ecosystem")
        # In real implementation, would create tmux configs and auto-start scripts
        
    def _setup_power_management(self, config: WorkstationConfig, dry_run: bool):
        """Setup Q9550 power management."""
        if dry_run:
            self.logger.info("Would setup Q9550 power management")
            return
            
        self.logger.info("Setting up Q9550 power management")
        # In real implementation, would install thermal monitoring and CPU controls
        
    def _setup_ai_tools(self, config: WorkstationConfig, dry_run: bool):
        """Setup AI development tools."""
        if dry_run:
            self.logger.info("Would setup AI tools")
            return
            
        self.logger.info("Setting up AI development tools")
        # In real implementation, would install Claude Code, setup Python environments
        
    def validate_installation(self) -> bool:
        """Validate completed installation."""
        self.logger.info("Validating installation")
        
        validation_report = self.config_validator.generate_validation_report()
        
        if validation_report.overall_status == "error":
            self.logger.error("Installation validation failed")
            for issue in validation_report.critical_issues:
                self.logger.error(f"Critical issue: {issue}")
            return False
        else:
            self.logger.info("Installation validation passed")
            return True
            
    def run_setup(self):
        """Main setup workflow."""
        try:
            # Welcome message
            if self.language == "cz":
                print("🚀 Vítejte v Unifikation Workstation Setup")
                print("Inteligentní automatizace nastavení vývojové stanice")
            else:
                print("🚀 Welcome to Unifikation Workstation Setup")
                print("Intelligent development workstation automation")
                
            # Gather requirements
            config = self.gather_requirements()
            
            # Analyze system
            analysis = self.analyze_system()
            
            # Create installation plan
            plan = self.create_installation_plan(config, analysis)
            
            # Display plan
            self.display_installation_plan(plan)
            
            # Confirm execution
            if self.language == "cz":
                confirm = input("\nPokračovat s instalací? (y/n): ").lower()
            else:
                confirm = input("\nProceed with installation? (y/n): ").lower()
                
            if confirm not in ['y', 'yes', 'ano']:
                print("Installation cancelled / Instalace zrušena")
                return
                
            # Execute installation
            self.execute_installation(plan, config)
            
            # Validate installation
            if self.validate_installation():
                if self.language == "cz":
                    print("\n✅ Workstation setup dokončen úspěšně!")
                else:
                    print("\n✅ Workstation setup completed successfully!")
            else:
                if self.language == "cz":
                    print("\n❌ Setup dokončen s chybami. Zkontrolujte logy.")
                else:
                    print("\n❌ Setup completed with errors. Check logs.")
                    
        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user / Setup zrušen uživatelem")
        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            if self.language == "cz":
                print(f"\n❌ Setup selhal: {e}")
            else:
                print(f"\n❌ Setup failed: {e}")


if __name__ == "__main__":
    wizard = WorkstationWizard()
    wizard.run_setup()
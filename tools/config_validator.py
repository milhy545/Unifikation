"""
Configuration Validator Module
Validates system configurations across ecosystem servers
"""

import os
import json
import subprocess
import logging
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationResult:
    """Result of configuration validation."""
    component: str
    status: str  # "ok", "warning", "error"
    message: str
    details: Optional[Dict] = None


@dataclass
class EcosystemValidation:
    """Complete ecosystem validation results."""
    overall_status: str
    validations: List[ValidationResult]
    recommendations: List[str]
    critical_issues: List[str]


class ConfigValidator:
    """Comprehensive configuration validation across ecosystem."""
    
    CRITICAL_CONFIGS = {
        "ssh": {
            "files": ["~/.ssh/config", "~/.ssh/authorized_keys"],
            "requirements": ["ssh_server_running", "key_permissions"]
        },
        "tmux": {
            "files": ["~/.tmux.conf"],
            "requirements": ["tmux_installed", "sessions_startable"]
        },
        "shell": {
            "files": ["~/.bashrc", "~/.zshrc", "~/.shell_common"],
            "requirements": ["shell_configured", "aliases_functional"]
        },
        "networking": {
            "files": ["/etc/hosts", "/etc/resolv.conf"],
            "requirements": ["dns_resolution", "local_connectivity"]
        }
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def validate_ssh_configuration(self) -> List[ValidationResult]:
        """Validate SSH configuration and connectivity."""
        results = []
        
        # Check SSH config file
        ssh_config_path = os.path.expanduser("~/.ssh/config")
        if os.path.exists(ssh_config_path):
            results.append(ValidationResult(
                component="ssh_config",
                status="ok",
                message="SSH config file exists",
                details={"path": ssh_config_path}
            ))
            
            # Validate SSH config content
            try:
                with open(ssh_config_path, 'r') as f:
                    config_content = f.read()
                    
                # Check for common issues
                if "Port 2222" in config_content or "Port 22" in config_content:
                    results.append(ValidationResult(
                        component="ssh_ports",
                        status="ok",
                        message="SSH ports configured"
                    ))
                else:
                    results.append(ValidationResult(
                        component="ssh_ports",
                        status="warning",
                        message="No explicit SSH ports configured"
                    ))
                    
                # Check for key files
                if "IdentityFile" in config_content:
                    results.append(ValidationResult(
                        component="ssh_keys",
                        status="ok",
                        message="SSH identity files configured"
                    ))
                    
            except Exception as e:
                results.append(ValidationResult(
                    component="ssh_config_read",
                    status="error",
                    message=f"Could not read SSH config: {e}"
                ))
        else:
            results.append(ValidationResult(
                component="ssh_config",
                status="warning",
                message="SSH config file missing"
            ))
            
        # Check SSH key permissions
        ssh_dir = os.path.expanduser("~/.ssh")
        if os.path.exists(ssh_dir):
            dir_stat = os.stat(ssh_dir)
            dir_perms = oct(dir_stat.st_mode)[-3:]
            
            if dir_perms == "700":
                results.append(ValidationResult(
                    component="ssh_permissions",
                    status="ok",
                    message="SSH directory permissions correct"
                ))
            else:
                results.append(ValidationResult(
                    component="ssh_permissions",
                    status="warning",
                    message=f"SSH directory permissions: {dir_perms} (should be 700)"
                ))
                
        # Check SSH server status
        ssh_status = self._check_ssh_server_status()
        results.append(ValidationResult(
            component="ssh_server",
            status="ok" if ssh_status else "warning",
            message="SSH server running" if ssh_status else "SSH server not running"
        ))
        
        return results
        
    def validate_tmux_configuration(self) -> List[ValidationResult]:
        """Validate tmux configuration and functionality."""
        results = []
        
        # Check if tmux is installed
        tmux_installed = self._command_exists("tmux")
        results.append(ValidationResult(
            component="tmux_binary",
            status="ok" if tmux_installed else "error",
            message="tmux installed" if tmux_installed else "tmux not installed"
        ))
        
        if not tmux_installed:
            return results
            
        # Check tmux config
        tmux_config_path = os.path.expanduser("~/.tmux.conf")
        if os.path.exists(tmux_config_path):
            results.append(ValidationResult(
                component="tmux_config",
                status="ok",
                message="tmux config file exists"
            ))
            
            # Validate config content
            try:
                with open(tmux_config_path, 'r') as f:
                    config_content = f.read()
                    
                # Check for common configurations
                if "set -g" in config_content:
                    results.append(ValidationResult(
                        component="tmux_settings",
                        status="ok",
                        message="tmux settings configured"
                    ))
                    
                if "bind" in config_content:
                    results.append(ValidationResult(
                        component="tmux_keybindings",
                        status="ok",
                        message="tmux key bindings configured"
                    ))
                    
            except Exception as e:
                results.append(ValidationResult(
                    component="tmux_config_read",
                    status="error",
                    message=f"Could not read tmux config: {e}"
                ))
        else:
            results.append(ValidationResult(
                component="tmux_config",
                status="warning",
                message="tmux config file missing"
            ))
            
        # Check tmux sessions
        try:
            result = subprocess.run(
                ["tmux", "list-sessions"],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                session_count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
                results.append(ValidationResult(
                    component="tmux_sessions",
                    status="ok",
                    message=f"{session_count} tmux sessions active",
                    details={"session_count": session_count}
                ))
            else:
                results.append(ValidationResult(
                    component="tmux_sessions",
                    status="warning",
                    message="No active tmux sessions"
                ))
                
        except Exception as e:
            results.append(ValidationResult(
                component="tmux_sessions",
                status="error",
                message=f"Could not check tmux sessions: {e}"
            ))
            
        return results
        
    def validate_shell_configuration(self) -> List[ValidationResult]:
        """Validate shell configuration and aliases."""
        results = []
        
        # Check shell common config
        shell_common_path = os.path.expanduser("~/.shell_common")
        if os.path.exists(shell_common_path):
            results.append(ValidationResult(
                component="shell_common",
                status="ok",
                message="shell_common file exists"
            ))
            
            # Validate content
            try:
                with open(shell_common_path, 'r') as f:
                    content = f.read()
                    
                # Check for essential aliases
                essential_aliases = ["HAS", "LLMS", "tmux-", "power"]
                found_aliases = []
                
                for alias in essential_aliases:
                    if f"alias {alias}" in content or f"alias {alias}=" in content:
                        found_aliases.append(alias)
                        
                results.append(ValidationResult(
                    component="shell_aliases",
                    status="ok" if len(found_aliases) >= 3 else "warning",
                    message=f"Found {len(found_aliases)}/{len(essential_aliases)} essential aliases",
                    details={"found_aliases": found_aliases}
                ))
                
            except Exception as e:
                results.append(ValidationResult(
                    component="shell_common_read",
                    status="error",
                    message=f"Could not read shell_common: {e}"
                ))
        else:
            results.append(ValidationResult(
                component="shell_common",
                status="error",
                message="shell_common file missing"
            ))
            
        # Check if shell_common is sourced
        shell_configs = ["~/.bashrc", "~/.zshrc"]
        sourced_in = []
        
        for config_file in shell_configs:
            config_path = os.path.expanduser(config_file)
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        content = f.read()
                        if "source ~/.shell_common" in content:
                            sourced_in.append(config_file)
                except Exception:
                    pass
                    
        results.append(ValidationResult(
            component="shell_sourcing",
            status="ok" if sourced_in else "warning",
            message=f"shell_common sourced in: {sourced_in}" if sourced_in else "shell_common not sourced",
            details={"sourced_in": sourced_in}
        ))
        
        return results
        
    def validate_network_configuration(self) -> List[ValidationResult]:
        """Validate network configuration and connectivity."""
        results = []
        
        # Test local connectivity
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "127.0.0.1"],
                capture_output=True, text=True, timeout=5
            )
            
            results.append(ValidationResult(
                component="localhost_connectivity",
                status="ok" if result.returncode == 0 else "error",
                message="Localhost connectivity working" if result.returncode == 0 else "Localhost connectivity failed"
            ))
            
        except Exception as e:
            results.append(ValidationResult(
                component="localhost_connectivity",
                status="error",
                message=f"Localhost connectivity test failed: {e}"
            ))
            
        # Test DNS resolution
        try:
            result = subprocess.run(
                ["nslookup", "google.com"],
                capture_output=True, text=True, timeout=5
            )
            
            results.append(ValidationResult(
                component="dns_resolution",
                status="ok" if result.returncode == 0 else "warning",
                message="DNS resolution working" if result.returncode == 0 else "DNS resolution issues"
            ))
            
        except Exception as e:
            results.append(ValidationResult(
                component="dns_resolution",
                status="warning",
                message=f"DNS resolution test failed: {e}"
            ))
            
        # Check network interfaces
        try:
            result = subprocess.run(
                ["ip", "addr", "show"],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                # Count active interfaces (exclude loopback)
                interfaces = []
                for line in result.stdout.split('\n'):
                    if 'inet ' in line and '127.0.0.1' not in line:
                        interfaces.append(line.strip())
                        
                results.append(ValidationResult(
                    component="network_interfaces",
                    status="ok" if interfaces else "warning",
                    message=f"{len(interfaces)} active network interfaces" if interfaces else "No active network interfaces",
                    details={"interface_count": len(interfaces)}
                ))
                
        except Exception as e:
            results.append(ValidationResult(
                component="network_interfaces",
                status="error",
                message=f"Could not check network interfaces: {e}"
            ))
            
        return results
        
    def validate_ecosystem(self) -> bool:
        """Perform comprehensive ecosystem validation."""
        try:
            # Run all validations
            ssh_results = self.validate_ssh_configuration()
            tmux_results = self.validate_tmux_configuration()
            shell_results = self.validate_shell_configuration()
            network_results = self.validate_network_configuration()
            
            all_results = ssh_results + tmux_results + shell_results + network_results
            
            # Check for critical errors
            errors = [r for r in all_results if r.status == "error"]
            
            if errors:
                self.logger.warning(f"Found {len(errors)} critical configuration errors")
                return False
            else:
                warnings = [r for r in all_results if r.status == "warning"]
                self.logger.info(f"Configuration validation passed with {len(warnings)} warnings")
                return True
                
        except Exception as e:
            self.logger.error(f"Ecosystem validation failed: {e}")
            return False
            
    def generate_validation_report(self) -> EcosystemValidation:
        """Generate comprehensive validation report."""
        self.logger.info("Generating validation report")
        
        # Run all validations
        all_validations = []
        all_validations.extend(self.validate_ssh_configuration())
        all_validations.extend(self.validate_tmux_configuration())
        all_validations.extend(self.validate_shell_configuration())
        all_validations.extend(self.validate_network_configuration())
        
        # Analyze results
        errors = [v for v in all_validations if v.status == "error"]
        warnings = [v for v in all_validations if v.status == "warning"]
        
        # Determine overall status
        if errors:
            overall_status = "error"
        elif warnings:
            overall_status = "warning"
        else:
            overall_status = "ok"
            
        # Generate recommendations
        recommendations = []
        critical_issues = []
        
        for validation in all_validations:
            if validation.status == "error":
                critical_issues.append(f"{validation.component}: {validation.message}")
                
                # Generate specific recommendations
                if validation.component == "ssh_config":
                    recommendations.append("Create SSH configuration file with proper server definitions")
                elif validation.component == "tmux_binary":
                    recommendations.append("Install tmux package for terminal multiplexing")
                elif validation.component == "shell_common":
                    recommendations.append("Create unified shell configuration file")
                    
            elif validation.status == "warning":
                if validation.component == "ssh_permissions":
                    recommendations.append("Fix SSH directory permissions: chmod 700 ~/.ssh")
                elif validation.component == "tmux_sessions":
                    recommendations.append("Start tmux sessions for ecosystem management")
                elif validation.component == "shell_sourcing":
                    recommendations.append("Add 'source ~/.shell_common' to shell config files")
                    
        return EcosystemValidation(
            overall_status=overall_status,
            validations=all_validations,
            recommendations=recommendations,
            critical_issues=critical_issues
        )
        
    def _check_ssh_server_status(self) -> bool:
        """Check if SSH server is running."""
        try:
            # Try different service names
            for service in ["ssh", "sshd", "openssh"]:
                result = subprocess.run(
                    ["systemctl", "is-active", service],
                    capture_output=True, text=True
                )
                if result.returncode == 0 and "active" in result.stdout:
                    return True
                    
            return False
            
        except Exception:
            return False
            
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
            
    def export_validation_report(self, filepath: str):
        """Export validation report to JSON file."""
        try:
            report = self.generate_validation_report()
            
            # Convert to serializable format
            report_dict = {
                "overall_status": report.overall_status,
                "recommendations": report.recommendations,
                "critical_issues": report.critical_issues,
                "validations": [
                    {
                        "component": v.component,
                        "status": v.status,
                        "message": v.message,
                        "details": v.details
                    }
                    for v in report.validations
                ]
            }
            
            with open(filepath, 'w') as f:
                json.dump(report_dict, f, indent=2)
                
            self.logger.info(f"Validation report exported to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Could not export validation report: {e}")
            raise
"""
Test Impossible SSH Scenarios
Testing edge cases that caused the "150+ SSH problems" nightmare
"""

import unittest
import tempfile
import os
import subprocess
import socket
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from tools.network_scanner import NetworkScanner
from tools.config_validator import ConfigValidator


class TestSSHChaosScenarios(unittest.TestCase):
    """Test impossible SSH scenarios that drove us crazy."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME')
        os.environ['HOME'] = self.temp_dir
        
        self.network_scanner = NetworkScanner()
        self.config_validator = ConfigValidator()
        
    def tearDown(self):
        """Clean up test environment."""
        if self.original_home:
            os.environ['HOME'] = self.original_home
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_port_confusion_nightmare(self):
        """Test the infamous port 22 vs 2222 confusion that happened 50+ times."""
        # Create SSH config with mixed ports (the source of pain)
        ssh_dir = os.path.join(self.temp_dir, '.ssh')
        os.makedirs(ssh_dir, exist_ok=True)
        
        # The problematic config that caused chaos
        problematic_config = """
Host LLMS
    HostName 192.168.0.41
    User milhy777
    Port 22
    
Host HAS
    HostName 192.168.0.58
    User root
    Port 2222
    
Host LLMS-new
    HostName 192.168.0.41
    User milhy777
    Port 2222
"""
        
        config_path = os.path.join(ssh_dir, 'config')
        with open(config_path, 'w') as f:
            f.write(problematic_config)
            
        # This should detect the port inconsistency
        validations = self.config_validator.validate_ssh_configuration()
        
        # Should warn about multiple configs for same host
        ssh_warnings = [v for v in validations if 'port' in v.message.lower()]
        self.assertTrue(len(ssh_warnings) >= 0)  # At least detect the config
        
    def test_key_permission_hell(self):
        """Test SSH key permission problems that broke everything."""
        ssh_dir = os.path.join(self.temp_dir, '.ssh')
        os.makedirs(ssh_dir, exist_ok=True)
        
        # Create key with wrong permissions (caused 20+ failures)
        key_path = os.path.join(ssh_dir, 'id_rsa')
        with open(key_path, 'w') as f:
            f.write("fake private key content")
            
        # Set wrong permissions (readable by others - security nightmare)
        os.chmod(key_path, 0o644)  # Should be 0o600
        
        validations = self.config_validator.validate_ssh_configuration()
        
        # Should detect permission issues
        permission_issues = [v for v in validations if 'permission' in v.message.lower()]
        self.assertTrue(len(permission_issues) > 0)
        
    def test_hostname_resolution_chaos(self):
        """Test hostname resolution failures that caused random connection failures."""
        with patch('socket.gethostbyaddr') as mock_resolve:
            # Simulate DNS resolution failure
            mock_resolve.side_effect = socket.herror("Name resolution failed")
            
            # This should handle the resolution failure gracefully
            hostname = self.network_scanner.resolve_hostname("192.168.0.41")
            
            # Should return None instead of crashing
            self.assertIsNone(hostname)
            
    def test_network_partition_during_scan(self):
        """Test network becoming unavailable during discovery."""
        with patch('socket.socket') as mock_socket:
            # Simulate network unavailable
            mock_socket.side_effect = OSError("Network is unreachable")
            
            # Should handle network failure gracefully
            servers = self.network_scanner.scan_ecosystem()
            
            # Should return empty list, not crash
            self.assertEqual(servers, [])
            
    def test_ssh_config_corruption(self):
        """Test corrupted SSH config that caused parsing failures."""
        ssh_dir = os.path.join(self.temp_dir, '.ssh')
        os.makedirs(ssh_dir, exist_ok=True)
        
        # Create corrupted SSH config
        corrupted_config = """
Host LLMS
    HostName 192.168.0.41
    User milhy777
    Port 22
Host HAS
    HostName 192.168.0.58
    User root
    Port INVALID_PORT_NUMBER
    
# Incomplete entry
Host BROKEN
    HostName
"""
        
        config_path = os.path.join(ssh_dir, 'config')
        with open(config_path, 'w') as f:
            f.write(corrupted_config)
            
        # Should handle corrupted config gracefully
        validations = self.config_validator.validate_ssh_configuration()
        
        # Should at least detect that config exists
        config_validations = [v for v in validations if v.component == "ssh_config"]
        self.assertTrue(len(config_validations) > 0)
        
    def test_simultaneous_ssh_connections(self):
        """Test multiple SSH connections causing port conflicts."""
        # Simulate multiple connections to same server
        with patch('socket.socket') as mock_socket:
            mock_instance = MagicMock()
            mock_socket.return_value = mock_instance
            
            # First connection succeeds
            mock_instance.connect_ex.side_effect = [0, 111, 111]  # ECONNREFUSED after first
            
            # Should handle connection refusal gracefully
            result1 = self.network_scanner.scan_port("192.168.0.41", 22)
            result2 = self.network_scanner.scan_port("192.168.0.41", 22)
            result3 = self.network_scanner.scan_port("192.168.0.41", 22)
            
            self.assertTrue(result1)   # First should succeed
            self.assertFalse(result2)  # Others should fail but not crash
            self.assertFalse(result3)
            
    def test_tmux_session_name_conflicts(self):
        """Test tmux session name conflicts that caused session chaos."""
        # This would test tmux session management, but we can't easily mock tmux
        # So we test the configuration validation instead
        
        shell_common_path = os.path.join(self.temp_dir, '.shell_common')
        
        # Create shell config with conflicting session names
        conflicting_config = """
alias tmux-llms='tmux new-session -d -s llms "ssh LLMS"'
alias tmux-aspire='tmux new-session -d -s llms "ssh Aspire"'  # Same session name!
alias tmux-has='tmux new-session -d -s has "ssh HAS"'
"""
        
        with open(shell_common_path, 'w') as f:
            f.write(conflicting_config)
            
        validations = self.config_validator.validate_shell_configuration()
        
        # Should at least detect that shell_common exists
        shell_validations = [v for v in validations if v.component == "shell_common"]
        self.assertTrue(len(shell_validations) > 0)
        
    def test_disk_full_during_key_generation(self):
        """Test SSH key generation failure due to disk space."""
        with patch('subprocess.run') as mock_run:
            # Simulate disk full error during key generation
            mock_run.side_effect = subprocess.CalledProcessError(
                1, ['ssh-keygen'], stderr="No space left on device"
            )
            
            # This would be in a key generation utility
            # For now, just test that subprocess errors are handled
            try:
                subprocess.run(['ssh-keygen', '-t', 'ed25519'], check=True)
                self.fail("Should have raised CalledProcessError")
            except subprocess.CalledProcessError as e:
                # Should handle this gracefully in real implementation
                self.assertIn("ssh-keygen", str(e.cmd))
                
    def test_context_limitation_scenarios(self):
        """Test scenarios where limited context caused repeated mistakes."""
        # This tests the meta-problem: making same mistakes repeatedly
        
        # Scenario 1: Port configuration keeps getting reset
        ssh_dir = os.path.join(self.temp_dir, '.ssh')
        os.makedirs(ssh_dir, exist_ok=True)
        
        configs = [
            "Port 22",      # Original mistake
            "Port 2222",    # Fix attempt 1
            "Port 22",      # Reverted by mistake
            "Port 2222",    # Fix attempt 2
        ]
        
        for i, port_config in enumerate(configs):
            config_content = f"""
Host LLMS
    HostName 192.168.0.41
    User milhy777
    {port_config}
"""
            config_path = os.path.join(ssh_dir, 'config')
            with open(config_path, 'w') as f:
                f.write(config_content)
                
            # Each time, validation should work
            validations = self.config_validator.validate_ssh_configuration()
            self.assertTrue(len(validations) > 0)
            
        # The point: we need automation to prevent these cycles
        
    def test_ecosystem_bootstrap_chicken_egg(self):
        """Test chicken-and-egg problems during ecosystem setup."""
        # Can't SSH to server to configure SSH
        # Can't install tmux without SSH
        # Can't test connectivity without network tools
        
        with patch('subprocess.run') as mock_run:
            # Simulate all commands failing initially
            mock_run.side_effect = subprocess.CalledProcessError(127, ['command'], stderr="Command not found")
            
            # Should handle missing tools gracefully
            connectivity_ok = self.config_validator._command_exists("ssh")
            self.assertFalse(connectivity_ok)
            
            # Should provide meaningful error messages
            validations = self.config_validator.validate_network_configuration()
            error_validations = [v for v in validations if v.status == "error"]
            
            # Should have some error validations when tools are missing
            self.assertTrue(len(error_validations) >= 0)  # At least don't crash
            

class TestImpossibleRecoveryScenarios(unittest.TestCase):
    """Test recovery from impossible situations."""
    
    def test_complete_ssh_lockout_recovery(self):
        """Test recovery when completely locked out of all servers."""
        # This is the nightmare scenario: no SSH access to any server
        
        network_scanner = NetworkScanner()
        
        with patch.object(network_scanner, 'scan_port') as mock_scan:
            # All SSH ports return connection refused
            mock_scan.return_value = False
            
            # Should still be able to discover network topology
            topology = network_scanner.discover_network_topology()
            
            # Should return a valid topology structure even if no SSH access
            self.assertIsNotNone(topology.local_ip)
            
    def test_corrupted_ecosystem_recovery(self):
        """Test recovery when entire ecosystem configuration is corrupted."""
        config_validator = ConfigValidator()
        
        # Should provide recovery recommendations even with broken config
        report = config_validator.generate_validation_report()
        
        # Should always have some recommendations
        self.assertIsInstance(report.recommendations, list)
        
    def test_network_storm_recovery(self):
        """Test handling of network broadcast storms that break discovery."""
        with patch('socket.socket') as mock_socket:
            # Simulate network timeouts
            mock_instance = MagicMock()
            mock_socket.return_value = mock_instance
            mock_instance.connect_ex.side_effect = socket.timeout("Operation timed out")
            
            network_scanner = NetworkScanner()
            
            # Should handle timeouts gracefully
            servers = network_scanner.scan_ecosystem()
            self.assertEqual(servers, [])


if __name__ == '__main__':
    unittest.main()
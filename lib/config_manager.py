"""
Configuration management module for the Network Device Management tool.

This module handles device configuration operations like applying, backing up,
and comparing configurations.
"""
import os
import time
from pathlib import Path
from .ansible_runner import AnsibleRunner
from .inventory import InventoryManager

class ConfigManager:
    """Manages network device configurations."""
    
    def __init__(self, config_dir="configs"):
        """Initialize the configuration manager with the config directory."""
        self.config_dir = config_dir
        self.ansible_runner = AnsibleRunner()
        self.inventory_manager = InventoryManager()
        
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
    
    def push_config(self, hostname, config_content):
        """
        Push configuration to a device.
        
        Args:
            hostname (str): Hostname of the device
            config_content (str): Configuration content to apply
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create a temporary config file
            temp_config_file = f"temp_{hostname}_config.txt"
            with open(temp_config_file, 'w') as f:
                f.write(config_content)
            
            # Run Ansible playbook to apply the configuration
            extra_vars = {
                'target_host': hostname,
                'config_file': temp_config_file
            }
            
            result = self.ansible_runner.run_playbook('playbooks/configure_device.yml', extra_vars)
            
            # Clean up temporary file
            if os.path.exists(temp_config_file):
                os.remove(temp_config_file)
            
            return result.get('success', False)
        except Exception as e:
            print(f"Error pushing configuration: {str(e)}")
            return False
    
    def backup_config(self, hostname):
        """
        Backup configuration from a device.
        
        Args:
            hostname (str): Hostname of the device
            
        Returns:
            str: Path to the backup file or None if failed
        """
        try:
            # Create device-specific directory under configs
            device_dir = os.path.join(self.config_dir, hostname)
            os.makedirs(device_dir, exist_ok=True)
            
            # Create backup filename with timestamp
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(device_dir, f"{hostname}_{timestamp}.cfg")
            
            # Run Ansible playbook to backup the configuration
            extra_vars = {
                'target_host': hostname,
                'backup_file': backup_file
            }
            
            result = self.ansible_runner.run_playbook('playbooks/backup_config.yml', extra_vars)
            
            if result.get('success', False):
                # Also create a 'latest' symlink/copy for easy access
                latest_file = os.path.join(device_dir, f"{hostname}_latest.cfg")
                if os.path.exists(latest_file):
                    os.remove(latest_file)
                
                # Copy the backup to the latest file
                with open(backup_file, 'r') as src:
                    with open(latest_file, 'w') as dst:
                        dst.write(src.read())
                
                return backup_file
            else:
                return None
        except Exception as e:
            print(f"Error backing up configuration: {str(e)}")
            return None
    
    def get_config(self, hostname, revision=None):
        """
        Get device configuration content.
        
        Args:
            hostname (str): Hostname of the device
            revision (str, optional): Git revision or None for latest
            
        Returns:
            str: Configuration content or None if failed
        """
        try:
            # If revision is None, read the latest file
            if revision is None:
                config_file = os.path.join(self.config_dir, hostname, f"{hostname}_latest.cfg")
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        return f.read()
                return None
            
            # Otherwise, use GitManager to get a specific version
            from .git_manager import GitManager
            git_manager = GitManager()
            return git_manager.get_file_at_revision(
                os.path.join(hostname, f"{hostname}_latest.cfg"), 
                revision
            )
        except Exception as e:
            print(f"Error getting configuration: {str(e)}")
            return None
    
    def compare_configs(self, hostname, source_revision=None, target_revision=None):
        """
        Compare two revisions of a device configuration.
        
        Args:
            hostname (str): Hostname of the device
            source_revision (str, optional): Source revision (None for current)
            target_revision (str, optional): Target revision (None for latest backup)
            
        Returns:
            str: Diff output or None if failed
        """
        try:
            source_config = self.get_config(hostname, source_revision)
            target_config = self.get_config(hostname, target_revision)
            
            if source_config is None or target_config is None:
                return None
            
            import difflib
            diff = difflib.unified_diff(
                source_config.splitlines(),
                target_config.splitlines(),
                fromfile=f"{hostname} ({source_revision or 'current'})",
                tofile=f"{hostname} ({target_revision or 'latest backup'})",
                lineterm=''
            )
            
            return '\n'.join(diff)
        except Exception as e:
            print(f"Error comparing configurations: {str(e)}")
            return None

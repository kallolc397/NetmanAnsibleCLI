"""
Ansible integration module for the Network Device Management tool.

This module handles running Ansible playbooks and modules.
"""
import os
import json
import tempfile
import subprocess
from pathlib import Path
import yaml

class AnsibleRunner:
    """Runs Ansible playbooks and modules for network automation."""
    
    def __init__(self, inventory_file="data/ansible_inventory.yml"):
        """Initialize with the inventory file path."""
        self.inventory_file = inventory_file
    
    def run_playbook(self, playbook_path, extra_vars=None):
        """
        Run an Ansible playbook.
        
        Args:
            playbook_path (str): Path to the playbook file
            extra_vars (dict, optional): Extra variables to pass to the playbook
            
        Returns:
            dict: Result of the playbook run
        """
        try:
            # Check if playbook exists
            if not os.path.exists(playbook_path):
                return {'success': False, 'error': f"Playbook {playbook_path} not found"}
            
            # Create a temporary file for extra vars if provided
            extra_vars_file = None
            if extra_vars:
                fd, extra_vars_file = tempfile.mkstemp(suffix='.json')
                with os.fdopen(fd, 'w') as f:
                    json.dump(extra_vars, f)
            
            # Build command
            cmd = ['ansible-playbook', '-i', self.inventory_file, playbook_path]
            
            if extra_vars_file:
                cmd.extend(['-e', f'@{extra_vars_file}'])
            
            # Add JSON output formatter for easier parsing
            result_file = tempfile.mktemp(suffix='.json')
            cmd.extend(['--callback-plugin-path', '.', '-e', f'ansible_callback_result_file={result_file}'])
            
            # Run the command
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Read the result file if it exists
            result = {'success': process.returncode == 0}
            if process.returncode != 0:
                result['error'] = process.stderr
            
            # Try to parse the output for any returned facts or data
            try:
                if os.path.exists(result_file):
                    with open(result_file, 'r') as f:
                        result.update(json.load(f))
                    os.remove(result_file)
            except:
                pass
            
            # Clean up
            if extra_vars_file and os.path.exists(extra_vars_file):
                os.remove(extra_vars_file)
            
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run_module(self, host, module, module_args=None):
        """
        Run an Ansible module.
        
        Args:
            host (str): Target host or group
            module (str): Ansible module name
            module_args (dict, optional): Module arguments
            
        Returns:
            dict: Result of the module run
        """
        try:
            # Create a temporary file for module args if provided
            args_file = None
            if module_args:
                fd, args_file = tempfile.mkstemp(suffix='.json')
                with os.fdopen(fd, 'w') as f:
                    json.dump(module_args, f)
            
            # Build command
            module_with_args = module
            if args_file:
                with open(args_file, 'r') as f:
                    args_data = json.load(f)
                args_str = " ".join(f"{k}='{v}'" for k, v in args_data.items())
                module_with_args = f"{module} {args_str}"
            
            cmd = [
                'ansible',
                host,
                '-i', self.inventory_file,
                '-m', module
            ]
            
            if args_file:
                cmd.extend(['-a', f'@{args_file}'])
            elif module_args:
                args_str = " ".join(f"{k}='{v}'" for k, v in module_args.items())
                cmd.extend(['-a', args_str])
            
            # Run the command
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Parse the output
            result = {'success': process.returncode == 0}
            
            if process.returncode == 0:
                # Try to parse JSON output
                try:
                    output = process.stdout.strip()
                    # Ansible often returns output like "hostname | SUCCESS => { json data }"
                    if ' => ' in output:
                        json_part = output.split(' => ', 1)[1].strip()
                        parsed_output = json.loads(json_part)
                        result.update(parsed_output)
                    else:
                        result['stdout'] = output
                except:
                    result['stdout'] = process.stdout
            else:
                result['error'] = process.stderr
            
            # Clean up
            if args_file and os.path.exists(args_file):
                os.remove(args_file)
            
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_inventory(self):
        """
        Get the Ansible inventory.
        
        Returns:
            dict: Ansible inventory or None if failed
        """
        try:
            with open(self.inventory_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error getting inventory: {str(e)}")
            return None

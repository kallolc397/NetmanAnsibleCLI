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

# Check if we're in demo mode
DEMO_MODE = os.environ.get('NETMAN_DEMO_MODE', 'false').lower() in ('true', '1', 'yes')

# Import simulator for demo mode
DeviceSimulator = None
if DEMO_MODE:
    try:
        from .simulator import DeviceSimulator
    except ImportError:
        pass

class AnsibleRunner:
    """Runs Ansible playbooks and modules for network automation."""
    
    # Initialize simulator if in demo mode
    _simulator = None
    
    @classmethod
    def _get_simulator(cls):
        """Get or initialize the simulator."""
        if DEMO_MODE and DeviceSimulator and cls._simulator is None:
            cls._simulator = DeviceSimulator()
        return cls._simulator
    
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
        # Use simulated responses in demo mode
        if DEMO_MODE:
            simulator = self._get_simulator()
            if simulator:
                return self._simulate_playbook(playbook_path, extra_vars)
            
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
            
            # Run the command
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Parse the output
            result = {'success': process.returncode == 0}
            if process.returncode != 0:
                result['error'] = process.stderr
            else:
                result['stdout'] = process.stdout
                
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
        # Use simulated responses in demo mode
        if DEMO_MODE and self._simulator:
            return self._simulate_module(host, module, module_args)
            
        try:
            # Create a temporary file for module args if provided
            args_file = None
            if module_args:
                fd, args_file = tempfile.mkstemp(suffix='.json')
                with os.fdopen(fd, 'w') as f:
                    json.dump(module_args, f)
            
            # Build command
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
    
    def _simulate_playbook(self, playbook_path, extra_vars=None):
        """
        Simulate running an Ansible playbook in demo mode.
        
        Args:
            playbook_path (str): Path to the playbook file
            extra_vars (dict, optional): Extra variables to pass to the playbook
            
        Returns:
            dict: Simulated result of the playbook run
        """
        # Get target host from extra vars
        target_host = extra_vars.get('target_host', 'demo-router1') if extra_vars else 'demo-router1'
        
        # Determine device type based on hostname pattern
        device_type = 'cisco_ios'  # Default
        if 'switch' in target_host:
            device_type = 'cisco_ios'
        elif 'router' in target_host:
            device_type = 'cisco_ios'
        elif 'juniper' in target_host or 'srx' in target_host:
            device_type = 'junos'
        elif 'arista' in target_host or 'eos' in target_host:
            device_type = 'arista_eos'
            
        result = {'success': True}
        
        # Simulate different playbooks
        if 'backup_config' in playbook_path:
            # Simulate backup config playbook
            backup_file = extra_vars.get('backup_file', '/tmp/backup.cfg') if extra_vars else '/tmp/backup.cfg'
            result['backup_path'] = backup_file
            result['changed'] = True
            
        elif 'configure_device' in playbook_path:
            # Simulate configure device playbook
            result['changed'] = True
            result['diff'] = {
                'before': '# Previous config',
                'after': '# New config'
            }
            
        elif 'get_device_status' in playbook_path:
            # Simulate get device status playbook
            version = self._simulator.get_response(device_type, 'show version')
            interfaces = self._simulator.get_response(device_type, 'show interfaces')
            
            result['facts'] = {
                'hostname': target_host,
                'version': version.split('\n')[0] if version else 'Unknown version',
                'uptime': '1 day, 2 hours, 5 minutes',
                'serial': f"SIM{target_host[:3]}12345",
                'model': f"SIM-{device_type.upper()}",
                'interfaces': ['GigabitEthernet0/0', 'GigabitEthernet0/1'],
                'status': ['Up', 'Running'],
                'interfaces_detail': interfaces
            }
            
        elif 'demo_connectivity' in playbook_path:
            # Simulate demo connectivity playbook
            version = self._simulator.get_response(device_type, 'show version')
            clock = self._simulator.get_response(device_type, 'show clock')
            
            result['ping_status'] = {'ping': 'pong', 'success': True}
            result['device_info'] = [
                version.split('\n') if version else ['Version unknown'],
                clock.split('\n') if clock else ['Clock unknown']
            ]
            
        else:
            # Generic simulation for other playbooks
            result['message'] = f"Simulated execution of {os.path.basename(playbook_path)}"
            result['stdout'] = f"Simulated output for {target_host}"
            result['changed'] = True
            
        return result
    
    def _simulate_module(self, host, module, module_args=None):
        """
        Simulate running an Ansible module in demo mode.
        
        Args:
            host (str): Target host or group
            module (str): Ansible module name
            module_args (dict, optional): Module arguments
            
        Returns:
            dict: Simulated result of the module run
        """
        # Determine device type based on hostname pattern
        device_type = 'cisco_ios'  # Default
        if 'switch' in host:
            device_type = 'cisco_ios'
        elif 'router' in host:
            device_type = 'cisco_ios'
        elif 'juniper' in host or 'srx' in host:
            device_type = 'junos'
        elif 'arista' in host or 'eos' in host:
            device_type = 'arista_eos'
            
        result = {'success': True, 'changed': False}
        
        # Handle command modules
        if module in ('ios_command', 'junos_command', 'eos_command'):
            commands = module_args.get('commands', []) if module_args else []
            outputs = []
            
            for cmd in commands:
                output = self._simulator.get_response(device_type, cmd)
                outputs.append(output)
                
            result['stdout'] = "\n".join(outputs)
            result['stdout_lines'] = [out.split('\n') for out in outputs]
            
        # Handle config modules
        elif module in ('ios_config', 'junos_config', 'eos_config'):
            result['changed'] = True
            result['updates'] = ['line 1', 'line 2']
            result['diff'] = {
                'before': '# Previous config',
                'after': '# New config'
            }
            
        # Handle facts modules
        elif module in ('ios_facts', 'junos_facts', 'eos_facts'):
            version = self._simulator.get_response(device_type, 'show version')
            
            result['ansible_facts'] = {
                'ansible_net_hostname': host,
                'ansible_net_version': version.split('\n')[0] if version else 'Unknown',
                'ansible_net_model': f"SIM-{device_type.upper()}",
                'ansible_net_serialnum': f"SIM{host[:3]}12345",
                'ansible_net_interfaces': {
                    'GigabitEthernet0/0': {
                        'bandwidth': 1000000,
                        'description': 'WAN Interface',
                        'duplex': 'full',
                        'ipv4': {'address': '10.0.0.1', 'subnet': '24'},
                        'lineprotocol': 'up',
                        'operstatus': 'up'
                    },
                    'GigabitEthernet0/1': {
                        'bandwidth': 1000000,
                        'description': 'LAN Interface',
                        'duplex': 'full',
                        'ipv4': {'address': '192.168.1.1', 'subnet': '24'},
                        'lineprotocol': 'up',
                        'operstatus': 'up'
                    }
                }
            }
            
        else:
            # Generic simulation for other modules
            result['msg'] = f"Simulated execution of {module} on {host}"
            
        return result

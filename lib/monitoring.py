"""
Monitoring module for the Network Device Management tool.

This module handles device status monitoring and fact gathering.
"""
import time
import subprocess
from .ansible_runner import AnsibleRunner

class Monitor:
    """Monitors network devices."""
    
    @staticmethod
    def check_device_status(device_info):
        """
        Check if a device is reachable.
        
        Args:
            device_info (dict): Device information
            
        Returns:
            tuple: (status_bool, response_time_ms)
        """
        try:
            ip = device_info['ip']
            
            # Run ping command to check if device is reachable
            start_time = time.time()
            ping_count = '-n' if subprocess.os.name == 'nt' else '-c'
            ping_process = subprocess.run(
                ['ping', ping_count, '1', ip],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            end_time = time.time()
            
            # Calculate response time in milliseconds
            response_time = (end_time - start_time) * 1000  # ms
            
            # Check if ping was successful
            return ping_process.returncode == 0, response_time
        except Exception as e:
            print(f"Error checking device status: {str(e)}")
            return False, 0
    
    @staticmethod
    def get_device_facts(device_info):
        """
        Get facts about a network device using Ansible.
        
        Args:
            device_info (dict): Device information
            
        Returns:
            dict: Device facts or None if failed
        """
        try:
            ansible_runner = AnsibleRunner()
            
            # Run Ansible playbook to gather facts
            extra_vars = {
                'target_host': device_info['hostname']
            }
            
            result = ansible_runner.run_playbook('playbooks/get_device_status.yml', extra_vars)
            
            if result.get('success', False) and 'facts' in result:
                return result['facts']
            return None
        except Exception as e:
            print(f"Error getting device facts: {str(e)}")
            return None
    
    @staticmethod
    def monitor_interfaces(device_info):
        """
        Monitor network interfaces on a device.
        
        Args:
            device_info (dict): Device information
            
        Returns:
            dict: Interface status information or None if failed
        """
        try:
            ansible_runner = AnsibleRunner()
            
            # Run Ansible module directly to get interface info
            module = f"{device_info['device_type']}_command"
            args = {'commands': ['show interfaces']}
            
            result = ansible_runner.run_module(
                device_info['hostname'],
                module,
                args
            )
            
            if result.get('success', False) and 'stdout' in result:
                # Basic parsing of interface output could be added here
                return {
                    'raw_output': result['stdout'],
                    'parsed': parse_interface_output(result['stdout'], device_info['device_type'])
                }
            return None
        except Exception as e:
            print(f"Error monitoring interfaces: {str(e)}")
            return None

def parse_interface_output(output, device_type):
    """
    Parse interface output based on device type.
    This is a simplified example, actual implementation would be more complex.
    
    Args:
        output (str): Command output
        device_type (str): Type of device
        
    Returns:
        dict: Parsed interface information
    """
    # This is a very simplified example
    # In a real implementation, you would use TextFSM or similar for parsing
    interfaces = {}
    
    if 'cisco_ios' in device_type:
        # Very basic parsing for demonstration
        lines = output.split('\n')
        current_interface = None
        
        for line in lines:
            if line.strip() == '':
                continue
                
            # Check if this is an interface definition line
            if not line.startswith(' '):
                parts = line.split(' ')
                current_interface = parts[0]
                interfaces[current_interface] = {
                    'status': 'up' if 'up' in line.lower() else 'down',
                    'description': '',
                    'details': {}
                }
            elif current_interface and 'Description:' in line:
                interfaces[current_interface]['description'] = line.split('Description:')[1].strip()
    
    return interfaces

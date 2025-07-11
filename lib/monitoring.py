"""
Monitoring module for the Network Device Management tool.

This module handles device status monitoring and fact gathering.
"""
import time
import subprocess
import os
import platform
from .ansible_runner import AnsibleRunner

# Import the simulator for demo mode
try:
    from .simulator import DeviceSimulator
except ImportError:
    DeviceSimulator = None

# Check if we're in demo mode
DEMO_MODE = os.environ.get('NETMAN_DEMO_MODE', 'false').lower() in ('true', '1', 'yes')

class Monitor:
    """Monitors network devices."""
    
    # Initialize simulator if in demo mode
    _simulator = DeviceSimulator() if DEMO_MODE and DeviceSimulator else None
    
    @classmethod
    def check_device_status(cls, device_info):
        """
        Check if a device is reachable.
        
        Args:
            device_info (dict): Device information
            
        Returns:
            tuple: (status_bool, response_time_ms)
        """
        # Use simulator in demo mode
        if DEMO_MODE and cls._simulator:
            return cls._simulator.simulate_connection(device_info)
            
        try:
            ip = device_info['ip']
            
            # Run ping command to check if device is reachable
            start_time = time.time()
            ping_count = '-n' if platform.system() == 'Windows' else '-c'
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
    
    @classmethod
    def get_device_facts(cls, device_info):
        """
        Get facts about a network device using Ansible.
        
        Args:
            device_info (dict): Device information
            
        Returns:
            dict: Device facts or None if failed
        """
        # Use simulator in demo mode
        if DEMO_MODE and cls._simulator:
            # Simulate device facts using show version output
            device_type = device_info.get('device_type', 'cisco_ios')
            version_output = cls._simulator.get_response(device_type, 'show version')
            clock_output = cls._simulator.get_response(device_type, 'show clock')
            interfaces_output = cls._simulator.get_response(device_type, 'show ip interface brief')
            
            # Parse interfaces from the interface output
            interfaces = []
            if interfaces_output:
                for line in interfaces_output.split('\n'):
                    if 'Interface' not in line and line.strip():  # Skip header and empty lines
                        interface_name = line.split()[0]
                        interfaces.append(interface_name)
            
            # Extract uptime from the version output if available
            uptime = "1 day, 0 hours, 0 minutes"  # Default
            if version_output and 'uptime is' in version_output:
                uptime_parts = version_output.split('uptime is')[1].split('\n')[0].strip()
                uptime = uptime_parts
                
            # Extract serial number if available
            serial = f"SIM{device_info.get('hostname', 'UNKNOWN')[:3]}12345"  # Default
            if version_output and 'Processor board ID' in version_output:
                serial_line = [line for line in version_output.split('\n') if 'Processor board ID' in line]
                if serial_line:
                    serial = serial_line[0].split('Processor board ID')[1].strip()
            
            # Create a comprehensive simulated facts dictionary
            return {
                'hostname': device_info.get('hostname', 'unknown'),
                'version': version_output.split('\n')[0] if version_output else 'Unknown',
                'uptime': uptime,
                'serial': serial,
                'model': f"CISCO2901/K9" if 'cisco' in device_type else f"SIM-{device_type.upper()}",
                'interfaces': interfaces if interfaces else [
                    'GigabitEthernet0/0', 
                    'GigabitEthernet0/1', 
                    'GigabitEthernet0/2', 
                    'Loopback0'
                ],
                'time': clock_output,
                'os_type': 'ios' if 'cisco' in device_type else device_type,
                'vendor': 'cisco' if 'cisco' in device_type else device_type.split('_')[0],
                'memory': {
                    'total': '512MB',
                    'free': '256MB'
                },
                'configuration': 'Running'
            }
        
        try:
            ansible_runner = AnsibleRunner()
            
            # Run Ansible playbook to gather facts
            extra_vars = {
                'target_host': device_info['hostname']
            }
            
            result = ansible_runner.run_playbook('playbooks/get_device_status.yml', extra_vars)
            
            if result and result.get('success', False) and 'facts' in result:
                return result['facts']
            
            # If we get here, the actual facts gathering failed, so use the simulator as fallback
            if DEMO_MODE and cls._simulator:
                print(f"Using simulator for device facts as a fallback")
                return cls.get_device_facts(device_info)
            
            return None
        except Exception as e:
            print(f"Error getting device facts: {str(e)}")
            
            # If there's an error, use the simulator as fallback in demo mode
            if DEMO_MODE and cls._simulator:
                print(f"Using simulator for device facts due to error: {str(e)}")
                return cls.get_device_facts(device_info)
                
            return None
    
    @classmethod
    def monitor_interfaces(cls, device_info):
        """
        Monitor network interfaces on a device.
        
        Args:
            device_info (dict): Device information
            
        Returns:
            dict: Interface status information or None if failed
        """
        # Use simulator in demo mode
        if DEMO_MODE and cls._simulator:
            device_type = device_info.get('device_type', 'cisco_ios')
            interfaces_output = cls._simulator.get_response(device_type, 'show interfaces')
            
            return {
                'raw_output': interfaces_output,
                'parsed': parse_interface_output(interfaces_output, device_type)
            }
            
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

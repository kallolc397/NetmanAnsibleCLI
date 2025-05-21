"""
Inventory management module for the Network Device Management tool.

This module handles adding, removing, and listing devices in the inventory.
"""
import os
import json
import yaml
from pathlib import Path

class InventoryManager:
    """Manages network device inventory."""
    
    def __init__(self, inventory_file="data/inventory.json", ansible_inventory_file="data/ansible_inventory.yml"):
        """Initialize the inventory manager with file paths."""
        self.inventory_file = inventory_file
        self.ansible_inventory_file = ansible_inventory_file
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Ensure inventory files exist."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.inventory_file), exist_ok=True)
        
        # Create JSON inventory file if it doesn't exist
        if not os.path.exists(self.inventory_file):
            with open(self.inventory_file, 'w') as f:
                json.dump([], f)
        
        # Create Ansible inventory file if it doesn't exist
        if not os.path.exists(self.ansible_inventory_file):
            with open(self.ansible_inventory_file, 'w') as f:
                yaml.dump({'all': {'children': {}}}, f)
    
    def add_device(self, hostname, ip, device_type, username, password, ssh_port=22, groups=None):
        """
        Add a device to the inventory.
        
        Args:
            hostname (str): Device hostname
            ip (str): Device IP address
            device_type (str): Device type (e.g., cisco_ios)
            username (str): Username for authentication
            password (str): Password for authentication
            ssh_port (int): SSH port (default: 22)
            groups (list): List of groups the device belongs to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load current inventory
            with open(self.inventory_file, 'r') as f:
                inventory = json.load(f)
            
            # Check if device already exists
            for device in inventory:
                if device['hostname'] == hostname:
                    return False  # Device already exists
            
            # Add new device
            device_info = {
                'hostname': hostname,
                'ip': ip,
                'device_type': device_type,
                'username': username,
                'password': password,
                'ssh_port': ssh_port,
                'groups': groups or []
            }
            
            inventory.append(device_info)
            
            # Save updated inventory
            with open(self.inventory_file, 'w') as f:
                json.dump(inventory, f, indent=2)
            
            # Update Ansible inventory file
            self._update_ansible_inventory()
            
            return True
        except Exception as e:
            print(f"Error adding device: {str(e)}")
            return False
    
    def remove_device(self, hostname):
        """
        Remove a device from the inventory.
        
        Args:
            hostname (str): Hostname of the device to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load current inventory
            with open(self.inventory_file, 'r') as f:
                inventory = json.load(f)
            
            # Find and remove the device
            device_found = False
            inventory = [device for device in inventory if not (device['hostname'] == hostname and (device_found := True))]
            
            if not device_found:
                return False  # Device not found
            
            # Save updated inventory
            with open(self.inventory_file, 'w') as f:
                json.dump(inventory, f, indent=2)
            
            # Update Ansible inventory file
            self._update_ansible_inventory()
            
            return True
        except Exception as e:
            print(f"Error removing device: {str(e)}")
            return False
    
    def list_devices(self, group=None):
        """
        List devices in the inventory, optionally filtered by group.
        
        Args:
            group (str, optional): Filter devices by group
            
        Returns:
            list: List of device dictionaries
        """
        try:
            with open(self.inventory_file, 'r') as f:
                inventory = json.load(f)
            
            if group:
                inventory = [device for device in inventory if group in device.get('groups', [])]
            
            return inventory
        except Exception as e:
            print(f"Error listing devices: {str(e)}")
            return []
    
    def get_device(self, hostname):
        """
        Get a specific device by hostname.
        
        Args:
            hostname (str): Hostname of the device
            
        Returns:
            dict: Device information or None if not found
        """
        try:
            with open(self.inventory_file, 'r') as f:
                inventory = json.load(f)
            
            for device in inventory:
                if device['hostname'] == hostname:
                    return device
            
            return None
        except Exception as e:
            print(f"Error getting device: {str(e)}")
            return None
    
    def _update_ansible_inventory(self):
        """
        Update the Ansible inventory file based on the JSON inventory.
        """
        try:
            # Load current inventory
            with open(self.inventory_file, 'r') as f:
                inventory = json.load(f)
            
            # Create Ansible inventory structure
            ansible_inventory = {
                'all': {
                    'children': {}
                }
            }
            
            # Populate groups
            all_groups = set()
            for device in inventory:
                for group in device.get('groups', []):
                    all_groups.add(group)
            
            # Initialize all groups
            for group in all_groups:
                ansible_inventory['all']['children'][group] = {'hosts': {}}
            
            # Add ungrouped section
            ansible_inventory['all']['children']['ungrouped'] = {'hosts': {}}
            
            # Add devices to their groups
            for device in inventory:
                device_vars = {
                    'ansible_host': device['ip'],
                    'ansible_user': device['username'],
                    'ansible_password': device['password'],
                    'ansible_port': device['ssh_port'],
                    'ansible_network_os': device['device_type']
                }
                
                # Add to specific groups
                device_groups = device.get('groups', [])
                if device_groups:
                    for group in device_groups:
                        ansible_inventory['all']['children'][group]['hosts'][device['hostname']] = device_vars
                else:
                    # Add to ungrouped if no groups specified
                    ansible_inventory['all']['children']['ungrouped']['hosts'][device['hostname']] = device_vars
            
            # Save updated Ansible inventory
            with open(self.ansible_inventory_file, 'w') as f:
                yaml.dump(ansible_inventory, f, default_flow_style=False)
                
        except Exception as e:
            print(f"Error updating Ansible inventory: {str(e)}")

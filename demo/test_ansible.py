#!/usr/bin/env python3
"""
NetMan Ansible Integration Tester

This script tests the Ansible integration in NetMan using demo mode.
"""
import os
import sys
import json
import yaml
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import NetMan modules
from lib.ansible_runner import AnsibleRunner
from lib.inventory import InventoryManager
from lib.simulator import DeviceSimulator

def test_ansible_inventory():
    """Test Ansible inventory generation."""
    print("\n--- Testing Ansible Inventory Generation ---")
    inventory_manager = InventoryManager()
    
    # Ensure demo devices exist
    devices = inventory_manager.list_devices()
    if not devices:
        print("Adding demo devices to inventory...")
        inventory_manager.add_device(
            hostname="demo-router1",
            ip="192.168.1.1",
            device_type="cisco_ios",
            username="demo",
            password="demo123",
            ssh_port=22,
            groups=["demo", "routers"]
        )
        inventory_manager.add_device(
            hostname="demo-switch1",
            ip="192.168.1.2",
            device_type="cisco_ios",
            username="demo",
            password="demo123",
            ssh_port=22,
            groups=["demo", "switches"]
        )
    
    # Check if Ansible inventory file exists
    ansible_inventory_path = "data/ansible_inventory.yml"
    if os.path.exists(ansible_inventory_path):
        print(f"Ansible inventory exists at: {ansible_inventory_path}")
        with open(ansible_inventory_path, 'r') as f:
            inventory = yaml.safe_load(f)
            
        # Print inventory structure
        print("\nAnsible Inventory Structure:")
        print(f"- All groups: {list(inventory.get('all', {}).get('children', {}).keys())}")
        hosts = []
        for group in inventory.get('all', {}).get('children', {}).values():
            if 'hosts' in group:
                hosts.extend(list(group['hosts'].keys()))
        print(f"- All hosts: {hosts}")
    else:
        print(f"Error: Ansible inventory file not found at {ansible_inventory_path}")

def test_ansible_playbook():
    """Test running an Ansible playbook."""
    print("\n--- Testing Ansible Playbook Execution (Demo Mode) ---")
    ansible_runner = AnsibleRunner()
    
    # Create mock simulator for testing
    os.environ['NETMAN_DEMO_MODE'] = 'true'
    simulator = DeviceSimulator()
    
    # Test demo connectivity playbook
    print("\nTesting demo_connectivity.yml playbook:")
    result = ansible_runner.run_playbook('playbooks/demo_connectivity.yml', {'target_host': 'demo-router1'})
    
    if result.get('success', False):
        print("✓ Playbook execution successful")
        print(f"Result keys: {list(result.keys())}")
    else:
        print("✗ Playbook execution failed")
        print(f"Error: {result.get('error', 'Unknown error')}")

def test_ansible_simulation():
    """Test simulating Ansible functionality."""
    print("\n--- Testing Network Device Simulation (Demo Mode) ---")
    os.environ['NETMAN_DEMO_MODE'] = 'true'
    
    print("\nSimulating command output...")
    
    # Use the device simulator to test commands
    from lib.simulator import DeviceSimulator
    simulator = DeviceSimulator()
    
    # Test some common commands on a Cisco IOS device
    cisco_commands = ['show version', 'show interfaces', 'show ip interface brief']
    
    for cmd in cisco_commands:
        print(f"\nCommand: {cmd}")
        output = simulator.get_response('cisco_ios', cmd)
        # Print just a snippet of the output (first 3 lines)
        lines = output.split('\n') if output else []
        for i in range(min(3, len(lines))):
            print(f"  {lines[i]}")
        print("  ...")
    
    # Test simulated connection
    status, response_time = simulator.simulate_connection({'hostname': 'demo-router1', 'ip': '192.168.1.1'})
    print(f"\nConnection status: {'Up' if status else 'Down'}, Response time: {response_time:.2f}ms")
    
    # Demonstrate configuration management
    print("\nSimulating Ansible configuration management:")
    print("""
In a real environment, NetMan would:
1. Generate a configuration from templates
2. Use Ansible playbooks to deploy it to devices
3. Track changes using Git for version control
4. Verify the deployment was successful
    """)
    
    print("Example configuration that would be deployed:")
    print("  hostname ROUTER1")
    print("  interface GigabitEthernet0/0")
    print("  description WAN Interface")
    print("  ip address 10.0.0.1 255.255.255.0")
    print("  ...")
    
    print("\nThis simulation shows how NetMan uses Ansible under the hood to manage network devices.")

def main():
    """Main function."""
    print("NetMan Ansible Integration Tester")
    print("=================================")
    
    # Make sure we're in demo mode
    os.environ['NETMAN_DEMO_MODE'] = 'true'
    
    # Run all tests
    test_ansible_inventory()
    test_ansible_simulation()
    
    print("\nTests completed!")

if __name__ == "__main__":
    main()